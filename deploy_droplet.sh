#!/usr/bin/env bash
# ============================================================
# Deploy automatizado: Katana Creaciones en DigitalOcean Droplet
# Ejecutar como root en un droplet Ubuntu 22.04/24.04 recién creado:
#   curl -sSL https://raw.githubusercontent.com/catau1625/katana_creaciones/main/deploy_droplet.sh | bash
# O clonar el repo y ejecutar: bash deploy_droplet.sh
# ============================================================
set -euo pipefail

# ---------- Colores ----------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ---------- Configuración (editar o responder los prompts) ----------
REPO_URL="https://github.com/catau1625/katana_creaciones.git"
APP_USER="katana"
APP_DIR="/home/${APP_USER}/katana_creaciones"
DOMAIN="${DOMAIN:-}"
SUPABASE_DB_PASSWORD="${SUPABASE_DB_PASSWORD:-}"
SUPABASE_PROYECTO_REF="${SUPABASE_PROYECTO_REF:-iqaahyghgtlqohxjsjpr}"
SUPABASE_REGION="${SUPABASE_REGION:-aws-0-sa-east-1}"
SECRET_KEY_VALUE="${SECRET_KEY_VALUE:-}"

echo "============================================================"
echo "  Deploy de Katana Creaciones en DigitalOcean Droplet"
echo "============================================================"

# ---------- Verificar que somos root ----------
[ "$(id -u)" -eq 0 ] || err "Este script debe ejecutarse como root (sudo bash deploy_droplet.sh)"

# ---------- Prompts para valores sensibles ----------
# Leer desde /dev/tty para que funcione también con: curl ... | bash
if [ -z "$SUPABASE_DB_PASSWORD" ]; then
    read -rsp "→ Contraseña de la base de datos de Supabase: " SUPABASE_DB_PASSWORD < /dev/tty
    echo
    [ -n "$SUPABASE_DB_PASSWORD" ] || err "La contraseña es obligatoria"
fi

if [ -z "$SECRET_KEY_VALUE" ]; then
    SECRET_KEY_VALUE=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50)
    ok "SECRET_KEY generada automáticamente"
fi

if [ -z "$DOMAIN" ]; then
    read -rp "→ Dominio (deja vacío para usar solo IP): " DOMAIN < /dev/tty
fi

SERVER_IP=$(curl -4 -s --max-time 10 ifconfig.me 2>/dev/null || hostname -I | tr ' ' '\n' | grep -E '^[0-9]+\.' | head -1)
[ -n "$SERVER_IP" ] || err "No se pudo detectar la IP pública. Define SERVER_IP manualmente."
ALLOWED_HOSTS_VALUE="${SERVER_IP},localhost,127.0.0.1"
SERVER_NAMES="${SERVER_IP}"
if [ -n "$DOMAIN" ]; then
    ALLOWED_HOSTS_VALUE="${ALLOWED_HOSTS_VALUE},${DOMAIN},www.${DOMAIN}"
    SERVER_NAMES="${SERVER_IP} ${DOMAIN} www.${DOMAIN}"
    warn "Asegúrate de que el dominio ${DOMAIN} apunte a la IP ${SERVER_IP} (registro A)"
fi

ok "Configuración: IP=${SERVER_IP}, Dominio=${DOMAIN:-ninguno}"

# ---------- 1. Actualizar sistema e instalar dependencias ----------
echo; echo "--- [1/9] Actualizando sistema e instalando dependencias ---"
export DEBIAN_FRONTEND=noninteractive
apt update -qq && apt upgrade -y -qq
apt install -y -qq python3 python3-pip python3-venv git nginx curl ufw
apt install -y -qq certbot python3-certbot-nginx || warn "Certbot no instalado (SSL manual)"
ok "Dependencias del sistema instaladas"

# ---------- 2. Crear usuario de la aplicación ----------
echo; echo "--- [2/9] Creando usuario '${APP_USER}' ---"
if ! id "$APP_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" "$APP_USER"
    usermod -aG sudo "$APP_USER"
    ok "Usuario creado"
else
    warn "Usuario ya existe, continuando"
fi

# ---------- 3. Clonar/actualizar repositorio ----------
echo; echo "--- [3/9] Clonando repositorio ---"
if [ -d "$APP_DIR" ]; then
    warn "El directorio ya existe, haciendo git pull..."
    su - "$APP_USER" -c "cd $APP_DIR && git pull origin main"
else
    su - "$APP_USER" -c "git clone $REPO_URL $APP_DIR"
fi
ok "Repositorio listo en $APP_DIR"

# ---------- 4. Entorno virtual + dependencias ----------
echo; echo "--- [4/9] Creando entorno virtual e instalando dependencias ---"
su - "$APP_USER" -c "
    cd $APP_DIR
    [ -d venv ] || python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
"
ok "Entorno virtual listo"

# ---------- 5. Archivo .env ----------
echo; echo "--- [5/9] Creando archivo .env ---"
ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$SUPABASE_DB_PASSWORD''', safe=''))")
DATABASE_URL="postgresql://postgres.${SUPABASE_PROYECTO_REF}:${ENCODED_PASSWORD}@${SUPABASE_REGION}.pooler.supabase.com:6543/postgres"

cat > "$APP_DIR/.env" << EOF
SECRET_KEY=${SECRET_KEY_VALUE}
DEBUG=False
ALLOWED_HOSTS=${ALLOWED_HOSTS_VALUE}
CSRF_TRUSTED_ORIGINS=https://${DOMAIN:-$SERVER_IP}
DATABASE_URL=${DATABASE_URL}
SUPABASE_URL=https://${SUPABASE_PROYECTO_REF}.supabase.co
SUPABASE_KEY=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

chmod 600 "$APP_DIR/.env"
chown "${APP_USER}:${APP_USER}" "$APP_DIR/.env"
ok ".env creado (permisos 600)"

# ---------- 6. Migraciones + collectstatic ----------
echo; echo "--- [6/9] Ejecutando migraciones y collectstatic ---"
su - "$APP_USER" -c "
    cd $APP_DIR
    source venv/bin/activate
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
"
ok "Migraciones aplicadas y estáticos recolectados"

# ---------- 7. Servicio Gunicorn (systemd) ----------
echo; echo "--- [7/9] Configurando servicio Gunicorn ---"
cat > /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=Gunicorn daemon for Katana Creaciones
After=network.target

[Service]
User=${APP_USER}
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn \\
    --workers 3 \\
    --bind unix:${APP_DIR}/gunicorn.sock \\
    --access-logfile - \\
    --error-logfile - \\
    katana.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now gunicorn
sleep 2
systemctl is-active --quiet gunicorn && ok "Gunicorn corriendo" || err "Gunicorn no inició. Revisa: journalctl -u gunicorn -n 30"

# ---------- 8. Nginx ----------
echo; echo "--- [8/9] Configurando Nginx ---"
cat > /etc/nginx/sites-available/katana << EOF
server {
    listen 80;
    server_name ${SERVER_NAMES};

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias ${APP_DIR}/staticfiles/;
    }

    location /media/ {
        alias ${APP_DIR}/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:${APP_DIR}/gunicorn.sock;
    }
}
EOF

ln -sf /etc/nginx/sites-available/katana /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx && systemctl enable nginx
ok "Nginx configurado"

# ---------- 9. Firewall ----------
echo; echo "--- [9/9] Configurando firewall ---"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
ok "Firewall activo (SSH + HTTP/HTTPS permitidos)"

# ---------- Permisos finales ----------
chown -R "${APP_USER}:www-data" "$APP_DIR"
chmod -R 755 "$APP_DIR"

# ---------- SSL opcional ----------
if [ -n "$DOMAIN" ]; then
    echo
    read -rp "→ ¿Configurar SSL/HTTPS ahora con Certbot? (requiere DNS apuntando) [s/N]: " DO_SSL < /dev/tty
    if [[ "$DO_SSL" =~ ^[Ss]$ ]]; then
        certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --redirect --agree-tos -m "admin@$DOMAIN" --no-eff-email || warn "SSL falló. Puedes ejecutarlo luego: certbot --nginx -d $DOMAIN"
    fi
fi

# ---------- Resumen ----------
echo
echo "============================================================"
echo -e "${GREEN}  ¡DEPLOY COMPLETADO!${NC}"
echo "============================================================"
echo "  Sitio:      http://${DOMAIN:-$SERVER_IP}"
echo "  Admin:      http://${DOMAIN:-$SERVER_IP}/admin"
echo "  App dir:    $APP_DIR"
echo
echo "  Próximos pasos:"
echo "  1. Crear superusuario:"
echo "     su - ${APP_USER} -c 'cd $APP_DIR && source venv/bin/activate && python manage.py createsuperuser'"
echo "  2. (Opcional) Cargar datos de prueba:"
echo "     su - ${APP_USER} -c 'cd $APP_DIR && source venv/bin/activate && python manage.py seed_datos'"
echo
echo "  Comandos útiles:"
echo "     systemctl status gunicorn     → estado de la app"
echo "     systemctl restart gunicorn    → reiniciar app"
echo "     journalctl -u gunicorn -f     → logs en vivo"
echo "     tail -f /var/log/nginx/error.log → logs de Nginx"
echo "============================================================"
