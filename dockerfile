FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Create data directory
RUN mkdir -p data

# Run both bot and web app
CMD ["sh", "-c", "python bot.py & gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120"]