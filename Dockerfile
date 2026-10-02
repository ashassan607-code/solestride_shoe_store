# Phase 5 (Deployment) — container image for the SoleStep shoe store MVP.
# Built for Azure App Service for Containers (Linux, single-container).
FROM python:3.11-slim

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code (includes assets/ for the SoleStep logo)
COPY . .

# SQLite file lives here at runtime; Azure App Service's local disk is
# ephemeral across restarts/scale events — fine for this MVP demo, but
# noted here as a production follow-up (see README "Known limitations").
ENV FLET_WEB=true
ENV PORT=8000
EXPOSE 8000

CMD ["python", "main.py"]
