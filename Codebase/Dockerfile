FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf \
    OMP_NUM_THREADS=1

WORKDIR /app

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

# Bake the embedding model into the image so the container needs no internet
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    && chmod -R a+rX /opt/hf

COPY src ./src
COPY healthcheck.py .

RUN useradd --system --uid 10001 --no-create-home app
USER app

# Data is mounted at runtime (see docker-compose.yml). final/ and processed/ must be siblings.
ENV HF_HUB_OFFLINE=1 \
    PLACES_DIR=/data/final \
    CACHE_DIR=/data/cache \
    WARMUP=1 \
    REGION_CACHE=4

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]

# Single worker on purpose: more workers multiply memory use
CMD ["uvicorn", "--app-dir", "src", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
