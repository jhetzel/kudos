FROM python:3.12

# Setze Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY . /app/

# Einstiegspunkt setzen
CMD ["python", "chain/core/main.py"]