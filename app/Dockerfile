FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py gunicorn_conf.py ./

# shared dir where each gunicorn worker writes its metrics
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/metrics

# run as non-root (security best practice)
RUN useradd -r appuser && mkdir -p /tmp/metrics && chown appuser /tmp/metrics
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "-c", "gunicorn_conf.py", "app:app"]
