FROM python:3.10-slim

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    apt-utils \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crea un utente non root
RUN useradd -m myuser
USER myuser

# Crea la directory di lavoro
WORKDIR /app

# Copia i file del progetto
COPY --chown=myuser:myuser . /app

# Aggiorna pip e installa le dipendenze Python
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Imposta la variabile d'ambiente per Streamlit
ENV STREAMLIT_SERVER_PORT=$PORT

# Comando di avvio dell'app
CMD ["streamlit", "run", "app.py", "--server.enableCORS=false"]


