FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY bot.py .

# Create required folders
RUN mkdir -p screenshots/hydra/normal screenshots/hydra/hard screenshots/hydra/brutal screenshots/hydra/nightmare \
    screenshots/chimera/easy screenshots/chimera/normal screenshots/chimera/hard screenshots/chimera/brutal screenshots/chimera/nightmare screenshots/chimera/ultra \
    screenshots/cvc

# Environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]