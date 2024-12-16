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

# Aggiungi il percorso di pip al PATH
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Aggiorna pip
RUN python -m pip install --upgrade pip

# Installa streamlit
RUN pip install streamlit

# Verifica la versione di streamlit
RUN which streamlit
RUN streamlit --version
