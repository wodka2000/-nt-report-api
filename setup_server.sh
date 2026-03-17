#!/bin/bash
# Setup iniziale del server Oracle Cloud (Ubuntu 22.04)
# Eseguire una sola volta con: bash setup_server.sh
set -e

APP_DIR="/opt/ntreportbot"
SERVICE_USER="ntbot"

echo "=== 1. Aggiornamento sistema ==="
sudo apt-get update -qq

echo "=== 2. Installazione Python 3.12 ==="
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -qq
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

echo "=== 3. Creazione utente di servizio ==="
sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER" 2>/dev/null || true

echo "=== 4. Creazione cartella applicazione ==="
sudo mkdir -p "$APP_DIR"
sudo chown "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR"

echo "=== 5. Copia file (devono essere già in /tmp/ntreportbot/) ==="
sudo cp -r /tmp/ntreportbot/. "$APP_DIR/"
sudo chown -R "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR"

echo "=== 6. Creazione virtualenv e installazione dipendenze ==="
sudo -u "$SERVICE_USER" python3.12 -m venv "$APP_DIR/venv"
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip" install --quiet --upgrade pip
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip" install --quiet pypdf

echo "=== 7. Installazione servizio systemd ==="
sudo cp "$APP_DIR/ntreportbot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ntreportbot

echo ""
echo "=== Setup completato ==="
echo ""
echo "Prima di avviare il bot, configura le variabili d'ambiente:"
echo "  sudo nano /etc/ntreportbot.env"
echo ""
echo "Inserisci:"
echo "  TELEGRAM_TOKEN=il_tuo_token"
echo "  ANTHROPIC_API_KEY=la_tua_chiave"
echo ""
echo "Poi avvia il bot:"
echo "  sudo systemctl start ntreportbot"
echo "  sudo systemctl status ntreportbot"
