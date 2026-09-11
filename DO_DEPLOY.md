# Guía Completa: Despliegue en DigitalOcean Droplet

## Stack: Ubuntu 22.04 + Nginx + Gunicorn + Supabase (PostgreSQL)

---

## 1. Crear el Droplet en DigitalOcean

1. Ve a [cloud.digitalocean.com](https://cloud.digitalocean.com) → **Create → Droplets**
2. Configura:
   - **Image:** Ubuntu 22.04 (LTS) x64
   - **Plan:** Basic ($6/mes - 1GB RAM / 1 CPU) es suficiente para empezar
   - **Datacenter:** New York 1 o el más cercano
   - **Authentication:** SSH Key (recomendado) o Password
   - **Hostname:** `katana-creaciones`
3. Clic en **Create Droplet**
4. **Anota la IP pública** que te asigna (ej: `164.90.xxx.xxx`)

---

## 2. Acceder al servidor por SSH

```bash
ssh root@TU_IP_DEL_DROPLET
```

Si usaste SSH key, entras directo. Si usaste password, te pedirá la contraseña.

> ⚠️ Reemplaza `TU_IP_DEL_DROPLET` con la IP real en todos los comandos.

---

## 3. Actualizar el sistema e instalar dependencias

```bash
# Actualizar paquetes del sistema
apt update && apt upgrade -y

# Instalar Python, Git, Nginx y utilidades
apt install -y python3 python3-pip python3-venv git nginx curl

# Instalar Certbot para SSL (HTTPS)
apt install -y certbot python3-certbot-nginx

# Verificar versiones
python3 --version    # Debe ser 3.10+
nginx -v             # Debe instalarse correctamente
```

---

## 4. Crear usuario para la aplicación (buena práctica)

```bash
# Crear usuario 'katana' con home directory
adduser katana --disabled-password --gecos ""

# Dar permisos de sudo
usermod -aG sudo katana

# Configurar SSH para el nuevo usuario (opcional, si quieres entrar como katana)
mkdir -p /home/katana/.ssh
cp ~/.ssh/authorized_keys /home/katana/.ssh/ 2>/dev/null || true
chown -R katana:katana /home/katana/.ssh
chmod 700 /home/katana/.ssh
chmod 600 /home/katana/.ssh/authorized_keys
```

---

## 5. Clonar el repositorio de GitHub

```bash
# Como usuario katana
su - katana

# Clonar el repositorio
git clone https://github.com/catau1625/katana_creaciones.git

# Entrar al directorio
cd katana_creaciones
```

> Si el repositorio fuera privado, necesitarías un token de GitHub. Como es público, no necesitas credenciales.

---

## 6. Crear entorno virtual e instalar dependencias

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

---

## 7. Configurar variables de entorno (.env)

```bash
# Crear archivo .env con las variables de producción
cat > /home/katana/katana_creaciones/.env << 'EOF'
DJANGO_SECRET_KEY=tu-clave-super-secreta-de-50-caracteres-aqui-genera-una-nueva
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=TU_IP_DEL_DROPLET,katanacreacionesweb.cl,www.katanacreacionesweb.cl
DATABASE_URL=postgresql://postgres:TU_PASSWORD_SUPABASE@db.TU_PROYECTO.supabase.co:5432/postgres?sslmode=require
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-gmail
EOF
```

> ⚠️ **IMPORTANTE:** Reemplaza los valores:
> - `TU-clave-super-secreta...` → Genera una nueva: https://djecrety.ir/
> - `TU_IP_DEL_DROPLET` → La IP pública de tu droplet
> - `TU_PASSWORD_SUPABASE` → La contraseña de la base de datos en Supabase
> - `db.TU_PROYECTO.supabase.co` → El host que te da Supabase (Project Settings → Database)

---

## 8. Cargar variables de entorno en settings.py

El proyecto usa `os.environ.get()`, así que necesitamos que las variables se carguen. Hay dos formas:

### Opción A: Usar python-dotenv (recomendado)

```bash
# Instalar python-dotenv
pip install python-dotenv
```

Luego editar `settings.py`:

```python
import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv  # ← Agregar esta línea

load_dotenv()  # ← Agregar esta línea (carga el .env)
```

### Opción B: Exportar variables manualmente (sin modificar código)

```bash
export DJANGO_SECRET_KEY="tu-clave-secreta"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="TU_IP,katanacreacionesweb.cl"
export DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres?sslmode=require"
```

> **Opción A es mejor** porque las variables persisten entre sesiones.

---

## 9. Ejecutar migraciones y configurar la base de datos

```bash
# Asegurarte de estar en el entorno virtual
source venv/bin/activate

# Verificar que DATABASE_URL se cargó correctamente
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('DATABASE_URL', 'NO CARGÓ'))"

# Ejecutar migraciones (crea las tablas en Supabase)
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario para el admin de Django
python manage.py createsuperuser
# Te pedirá: username, email, password
```

---

## 10. Probar que Gunicorn funciona

```bash
# Probar Gunicorn manualmente
gunicorn --bind 0.0.0.0:8000 katana.wsgi:application
```

Abre en tu navegador: `http://TU_IP_DEL_DROPLET:8000`

Si ves el sitio, **presiona Ctrl+C** para detener y continuar.

---

## 11. Crear servicio systemd para Gunicorn

```bash
# Salir del usuario katana
exit

# Crear archivo de servicio
cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=Gunicorn daemon for Katana Creaciones
After=network.target

[Service]
User=katana
Group=www-data
WorkingDirectory=/home/katana/katana_creaciones
Environment="PATH=/home/katana/katana_creaciones/venv/bin"
ExecStart=/home/katana/katana_creaciones/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/katana/katana_creaciones/gunicorn.sock \
          --access-logfile - \
          --error-logfile - \
          katana.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
```

```bash
# Iniciar y habilitar el servicio
systemctl start gunicorn
systemctl enable gunicorn

# Verificar estado
systemctl status gunicorn
```

> Debe decir **"active (running)"** en verde.

---

## 12. Configurar Nginx como reverse proxy

```bash
# Crear configuración de Nginx
cat > /etc/nginx/sites-available/katana << 'EOF'
server {
    listen 80;
    server_name TU_IP_DEL_DROPLET katanacreacionesweb.cl www.katanacreacionesweb.cl;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/katana/katana_creaciones/staticfiles/;
    }

    location /media/ {
        alias /home/katana/katana_creaciones/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/katana/katana_creaciones/gunicorn.sock;
    }
}
EOF
```

```bash
# Activar el sitio (crear symlink)
ln -sf /etc/nginx/sites-available/katana /etc/nginx/sites-enabled/

# Eliminar el sitio default de Nginx
rm -f /etc/nginx/sites-enabled/default

# Probar configuración de Nginx
nginx -t

# Debe decir: "syntax is ok" y "test is successful"

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx
```

---

## 13. Configurar firewall

```bash
# Permitir SSH (¡MUY IMPORTANTE! Si no, pierdes acceso)
ufw allow OpenSSH

# Permitir HTTP y HTTPS
ufw allow 'Nginx Full'

# Activar firewall
ufw enable

# Verificar reglas
ufw status
```

---

## 14. Configurar SSL (HTTPS) con Certbot

> ⚠️ **Requisito:** Tu dominio `katanacreacionesweb.cl` debe apuntar a la IP del droplet (registro A en tu DNS).

```bash
# Ejecutar Certbot
certbot --nginx -d katanacreacionesweb.cl -d www.katanacreacionesweb.cl

# Te pedirá:
# 1. Email
# 2. Aceptar términos
# 3. Redirigir HTTP → HTTPS (elige 2: Redirect)

# Verificar renovación automática
certbot renew --dry-run
```

---

## 15. Dar permisos finales

```bash
# Permisos para que Nginx pueda leer los archivos
chown -R katana:www-data /home/katana/katana_creaciones
chmod -R 755 /home/katana/katana_creaciones

# Permisos especiales para media (uploads)
chmod -R 775 /home/katana/katana_creaciones/media 2>/dev/null || true
```

---

## 16. Verificar que todo funciona

```bash
# Verificar Gunicorn
systemctl status gunicorn

# Verificar Nginx
systemctl status nginx

# Ver logs de Gunicorn si hay errores
journalctl -u gunicorn -f

# Ver logs de Nginx si hay errores
tail -f /var/log/nginx/error.log
```

Abre en tu navegador:
- `http://TU_IP_DEL_DROPLET` → Debe cargar el sitio
- `http://TU_IP_DEL_DROPLET/admin` → Panel de administración
- `https://katanacreacionesweb.cl` → Con SSL (si configuraste el dominio)

---

## Comandos útiles para el día a día

```bash
# Actualizar código desde GitHub
su - katana
cd katana_creaciones
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit

# Reiniciar servicios
systemctl restart gunicorn
systemctl restart nginx

# Ver logs en tiempo real
journalctl -u gunicorn -f
tail -f /var/log/nginx/access.log
```

---

## Resumen de archivos creados en el servidor

| Archivo | Ubicación | Propósito |
|---|---|---|
| `.env` | `/home/katana/katana_creaciones/.env` | Variables de entorno |
| `gunicorn.service` | `/etc/systemd/system/gunicorn.service` | Servicio de aplicación |
| `katana` (nginx) | `/etc/nginx/sites-available/katana` | Reverse proxy |

---

## Costos estimados

| Servicio | Costo mensual |
|---|---|
| DigitalOcean Droplet (1GB) | $6 USD |
| Supabase (Plan Free) | $0 |
| Dominio (katanacreacionesweb.cl) | ~$10-15 USD/año |
| **Total** | **~$6 USD/mes + dominio** |
