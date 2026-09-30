# gunicorn_config.py
# Multi‑worker configuration for FastAPI (Windows/Linux)
import multiprocessing

# Use twice the number of CPU cores as workers – good default
workers = multiprocessing.cpu_count() * 2

# Worker class that supports ASGI/FastAPI
worker_class = "uvicorn.workers.UvicornWorker"

# Bind to the same port you normally use
bind = "0.0.0.0:8000"

# Logging level – adjust as needed
loglevel = "info"

# Give enough time for inference (seconds)
timeout = 120

# Keep‑alive connections
keepalive = 2
