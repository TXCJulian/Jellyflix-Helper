FROM python:3.13-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Systemabhängigkeiten (z.B. für pip build)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY app/ app/
COPY dependencies/ dependencies/

# Port
EXPOSE 5000

# Startbefehl
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]