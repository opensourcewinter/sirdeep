FROM python:3.11-slim

# Install system dependencies (FFmpeg for 24/7 radio and fonts for Pillow card rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run bot entrypoint
CMD ["python", "main.py"]
