FROM python:3.12-slim
# Systempakete installieren
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    && rm -rf /var/lib/apt/lists/* \
|| (echo "APT INSTALL FAILED" && cat /var/log/apt/term.log && exit 1)

# Geckodriver installieren (Version ggf. anpassen)
ENV GECKODRIVER_VERSION=0.35.0
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux-aarch64.tar.gz" -O /tmp/geckodriver.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin \
    && rm /tmp/geckodriver.tar.gz \
    && chmod +x /usr/local/bin/geckodriver

# Arbeitsverzeichnis
WORKDIR /app

# Python-Abhängigkeiten
# requirements.txt sollte streamlit, selenium usw. enthalten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Deine App kopieren
COPY . .

# Xvfb + Streamlit starten
# Wichtig: DISPLAY muss mit docker-compose übereinstimmen (:99)
CMD bash -c "\
    Xvfb :99 -screen 0 1920x1080x24 & \
    export DISPLAY=:99 && \
    streamlit run scripts/streamlit.py --server.port=${STREAMLIT_SERVER_PORT:-8501} --server.address=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0} \
"