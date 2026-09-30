# Fake Image Detector

This project has a React frontend and FastAPI backend that scrape images from a public website and classify them as AI-generated or real.

## Local setup

Install backend dependencies:

```powershell
python -m pip install -r backend/requirements.txt
playwright install chromium
```

Run the API:

```powershell
cd backend
# For Windows – use Uvicorn with multiple workers (recommended 4)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
# If you prefer Linux‑based Gunicorn, use Docker (see docker-compose.yml)
```

Run the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The API is available at `http://127.0.0.1:8000/docs`.


## What's new in v2

- **Upload mode**: `POST /analyze/upload` classifies a single image and returns a Grad-CAM heat-map.
- **Summary + verdict**: AI/Real/Uncertain counts, AI percentage and an overall verdict for every scan.
- **Better accuracy handling**: flip test-time augmentation, batched inference, and an `UNCERTAIN` label below `UNCERTAIN_THRESHOLD` (default 60%).
- **Safe redirects**: sites/CDNs that redirect now work; every redirect hop is re-checked against the SSRF filter.
- **Result cache** (10 min, `CACHE_TTL_SECONDS`) so repeat scans are instant.
- **Proper HTTP errors** (`400/413/502/503`) and a `/health` endpoint that reports `model_ready`.
- **New UI**: URL/Upload tabs, drag & drop, filters, confidence bars, heat-map toggle.

## Deployment

The classifier checkpoint at `ml/models/efficientnet_b0.pth` is required at runtime. It is no longer ignored by Git or Vercel; add it before deploying:

```powershell
git add ml/models/efficientnet_b0.pth
```

The API only fetches publicly routable HTTP(S) URLs. It limits each analysis to 25 images and each downloaded image to 10 MB; configure this with `MAX_IMAGES_PER_ANALYSIS` and `MAX_IMAGE_BYTES` if needed.

Playwright rendering falls back to a regular HTTP request when Chromium is unavailable.
