FROM python:3.10-slim

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    apt-utils \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic-dev \
    && apt-get clean

# Crea un utente non root
RUN useradd -m myuser
USER myuser

# Crea la directory di lavoro
WORKDIR /app

# Copia i file del progetto
COPY . /app

# Aggiorna pip e installa le dipendenze Python
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Comando di avvio dell'app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.enableCORS=false"]