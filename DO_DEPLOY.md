# Guía de Despliegue — DigitalOcean Droplet + Supabase

## Opción recomendada: script automatizado

El repo incluye `deploy_droplet.sh` que automatiza todo el proceso.

### Requisitos previos

1. **Droplet creado** en DigitalOcean: Ubuntu 22.04/24.04, plan Basic ($6/mes).
   - Autenticación: SSH Key (recomendado) o password.
   - **Anota la IP pública** que te asigna.
2. **Base de datos Supabase** creada y contraseña de la base a mano.
3. (Opcional) **Dominio** con registro A apuntando a la IP del droplet.

### Pasos

**1. Conéctate al droplet como root:**

```bash
ssh root@TU_IP_DEL_DROPLET
```

**2. Ejecuta el script de deploy:**

```bash
curl -sSL https://raw.githubusercontent.com/catau1625/katana_creaciones/main/deploy_droplet.sh | bash
```

El script te pedirá:
- La contraseña de la base de datos de Supabase
- Un dominio (opcional, puedes dejarlo vacío y usar solo la IP)
- Si quieres SSL/HTTPS ahora (solo si el dominio ya apunta al droplet)

**3. Crea el superusuario del admin:**

```bash
su - katana -c 'cd ~/katana_creaciones && source venv/bin/activate && python manage.py createsuperuser'
```

**4. (Opcional) Carga datos de prueba:**

```bash
su - katana -c 'cd ~/katana_creaciones && source venv/bin/activate && python manage.py seed_datos'
```

**5. Abre en el navegador:**
- Sitio: `http://TU_IP_DEL_DROPLET` o `https://tudominio.cl`
- Admin: `http://TU_IP_DEL_DROPLET/admin`

---

## Qué hace el script automáticamente

| Paso | Acción |
|---|---|
| 1 | Actualiza el sistema e instala Python, Nginx, Git, UFW, Certbot |
| 2 | Crea el usuario `katana` |
| 3 | Clona/actualiza el repositorio desde GitHub |
| 4 | Crea el entorno virtual e instala `requirements.txt` |
| 5 | Genera el `.env` con SECRET_KEY aleatoria, ALLOWED_HOSTS y `DATABASE_URL` apuntando al **pooler de Supabase (puerto 6543)** con la contraseña URL-encodeada |
| 6 | Ejecuta `migrate` y `collectstatic` |
| 7 | Crea y activa el servicio systemd de Gunicorn |
| 8 | Configura Nginx como reverse proxy (static, media, proxy al socket) |
| 9 | Activa el firewall (SSH + HTTP/HTTPS) |
| — | Permisos finales y SSL opcional con Certbot |

---

## Detalles técnicos importantes (Supabase)

- **DATABASE_URL** usa el **pooler Supavisor** en el puerto **6543** (modo Transaction).
  El puerto 5432 es IPv6-only en el plan gratuito de Supabase y causa
  `Network is unreachable` en servidores sin salida IPv6.
- El `settings.py` usa `conn_max_age=0`, obligatorio con el pooler en modo Transaction.
- Si la contraseña de Supabase contiene caracteres especiales
  (`#`, `@`, `:`, `/`, `*`, `%`), el script la codifica automáticamente con
  `urllib.parse.quote()`.
- El `.env` se crea con permisos `600` (solo lectura del propietario) y **nunca**
  se commitea (está en `.gitignore`).

---

## Comandos útiles del día a día

```bash
# Actualizar código desde GitHub
su - katana
cd ~/katana_creaciones
git pull origin main
source venv/bin/activate
pip install -r requirements.txt   # solo si cambiaron dependencias
python manage.py migrate
python manage.py collectstatic --noinput
exit
systemctl restart gunicorn

# Estado y logs
systemctl status gunicorn
journalctl -u gunicorn -f              # logs de la app en vivo
tail -f /var/log/nginx/error.log       # logs de Nginx

# SSL (si agregaste dominio después)
certbot --nginx -d tudominio.cl -d www.tudominio.cl
```

---

## Diagnóstico rápido

| Síntoma | Causa | Solución |
|---|---|---|
| `Network is unreachable` (IPv6) | DATABASE_URL usa puerto 5432 | Usar pooler: `...pooler.supabase.com:6543` |
| `password authentication failed` | Contraseña con caracteres especiales sin codificar | El script la codifica; si lo haces a mano, usa `urllib.parse.quote()` |
| `DisallowedHost / 400` | `ALLOWED_HOSTS` incompleto | Incluir la IP y/o dominio en `.env` y reiniciar gunicorn |
| `No module named psycopg2` | Falta dependencia | `pip install psycopg2-binary` |
| Estático 404 | Falta collectstatic o ruta Nginx | Ejecutar collectstatic; verificar `alias` en Nginx |
| `NameError: BASE_DIR` | `load_dotenv` antes de definir `BASE_DIR` | Orden en settings.py: imports → `BASE_DIR` → `load_dotenv` → resto |

---

## Costos estimados

| Servicio | Costo mensual |
|---|---|
| DigitalOcean Droplet (1GB) | $6 USD |
| Supabase (Plan Free) | $0 |
| Dominio (.cl) | ~$10-15 USD/año |
| **Total** | **~$6 USD/mes + dominio** |
