"""Model loading, batched inference (with flip TTA) and Grad-CAM explanations."""
import base64
import io
import os
import sys
import threading

try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
except ModuleNotFoundError:  # keeps the API importable without torch
    torch = None
    nn = None
    models = None
    transforms = None

import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

LABELS = ["AI", "REAL"]
BATCH_SIZE = int(os.environ.get("INFERENCE_BATCH_SIZE", "8"))
# Below this confidence (%) the result is reported as UNCERTAIN instead of
# pretending the model is sure.
UNCERTAIN_THRESHOLD = float(os.environ.get("UNCERTAIN_THRESHOLD", "60"))

_model = None
_model_lock = threading.Lock()
_explain_lock = threading.Lock()


def _load_ml_config():
    if torch is None:
        raise RuntimeError("Torch is not installed in the runtime.")
    from ml.config import DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES
    return DEVICE, MODEL_PATH, IMAGE_SIZE, NUM_CLASSES


def build_model(num_classes: int):
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def get_model():
    """Load the checkpoint once (thread-safe) and reuse it."""
    global _model
    device, model_path, image_size, num_classes = _load_ml_config()

    if _model is None:
        with _model_lock:
            if _model is None:
                if not os.path.isfile(model_path):
                    raise FileNotFoundError(f"Model file not found: {model_path}")
                from ml.utils import load_model
                _model = load_model(build_model(num_classes), model_path, device)

    return _model, device, image_size


def is_model_ready() -> bool:
    try:
        get_model()
        return True
    except Exception:
        return False


def _transform(image_size: int):
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def _to_result(probabilities) -> dict:
    ai_p, real_p = float(probabilities[0]) * 100.0, float(probabilities[1]) * 100.0
    idx = 0 if ai_p >= real_p else 1
    confidence = max(ai_p, real_p)
    label = LABELS[idx] if confidence >= UNCERTAIN_THRESHOLD else "UNCERTAIN"
    return {
        "prediction": label,
        "confidence": round(confidence, 2),
        "ai_probability": round(ai_p, 2),
        "real_probability": round(real_p, 2),
    }


def _predict_pil_batch(pil_images: list) -> list[dict]:
    model, device, image_size = get_model()
    tfm = _transform(image_size)
    batch = torch.stack([tfm(img.convert("RGB")) for img in pil_images]).to(device)

    with torch.inference_mode():
        probs = torch.softmax(model(batch), dim=1)
        # Test-time augmentation: average with the horizontally flipped view.
        flipped = torch.softmax(model(torch.flip(batch, dims=[3])), dim=1)
        probs = ((probs + flipped) / 2.0).cpu()

    return [_to_result(p) for p in probs]


def predict_image(image_path: str) -> dict:
    with Image.open(image_path) as img:
        return _predict_pil_batch([img.copy()])[0]


def predict_images(image_paths: list[str]) -> list[dict]:
    """Batched prediction. One bad file never breaks the others."""
    if torch is None:
        raise RuntimeError("Torch is not installed in the runtime.")

    get_model()  # fail loudly (once) if the model can't be loaded

    results: list[dict | None] = [None] * len(image_paths)

    for start in range(0, len(image_paths), BATCH_SIZE):
        chunk = image_paths[start:start + BATCH_SIZE]
        loaded, positions = [], []
        for offset, path in enumerate(chunk):
            try:
                with Image.open(path) as img:
                    loaded.append(img.convert("RGB"))
                positions.append(start + offset)
            except Exception:
                results[start + offset] = {"prediction": "UNKNOWN", "confidence": None}

        if not loaded:
            continue
        try:
            for pos, res in zip(positions, _predict_pil_batch(loaded)):
                results[pos] = res
        except Exception:
            for pos in positions:
                results[pos] = {"prediction": "UNKNOWN", "confidence": None}

    return results  # type: ignore[return-value]


def explain_image(pil_image: Image.Image) -> str:
    """Grad-CAM heat-map (base64 PNG) showing what drove the prediction."""
    import cv2

    model, device, image_size = get_model()
    rgb = pil_image.convert("RGB")
    x = _transform(image_size)(rgb).unsqueeze(0).to(device)
    x.requires_grad_(True)

    activations, gradients = [], []
    layer = model.features[-1]

    def forward_hook(_module, _inp, out):
        activations.append(out)
        out.register_hook(lambda grad: gradients.append(grad))

    handle = layer.register_forward_hook(forward_hook)
    try:
        with _explain_lock, torch.enable_grad():
            model.zero_grad()
            output = model(x)
            target = int(output.argmax(dim=1).item())
            output[0, target].backward()
    finally:
        handle.remove()

    weights = gradients[0].mean(dim=(2, 3), keepdim=True)
    cam = torch.relu((weights * activations[0]).sum(dim=1)).squeeze(0).detach().cpu().numpy()
    cam = cam - cam.min()
    cam = cam / (cam.max() + 1e-8)

    original = np.array(rgb)
    cam = cv2.resize(cam, (original.shape[1], original.shape[0]))
    heat = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    overlay = np.uint8(0.55 * original + 0.45 * heat)

    buffer = io.BytesIO()
    Image.fromarray(overlay).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def predict_pil(pil_image: Image.Image) -> dict:
    """Predict a single in-memory image (used by the upload endpoint)."""
    return _predict_pil_batch([pil_image])[0]
