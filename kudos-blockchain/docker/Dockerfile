# Verwende einen offiziellen Python-Image als Basis
FROM python:3.12-slim

# Setze Umgebungsvariablen für konsistente Ausführung
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Erstelle ein Verzeichnis für die App
WORKDIR /app

# Kopiere die Anforderungen und installiere sie
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . /app/

# Standardkommando zum Starten der Anwendung
CMD ["python", "-m", "blockchain"]