# ⚔️ Katana Creaciones Web

Sitio personal desarrollado en **Django (Python)** con la paleta:
`#05060E · #12163A · #2E1A63 · #5B2A86 · #B14AED`

## Estructura

| Ruta | Contenido |
|---|---|
| `/` | Inicio con menú y destacados |
| `/productos/` | Página Web, Aplicaciones, Mantenimiento |
| `/productos/<slug>/` | Detalle de cada producto: descripción, precio y banner |
| `/proyectos/` | ForestIA, Wisapp, ConceTour3D |
| `/proyectos/<slug>/` | Cuadro interactivo con iframe del proyecto |
| `/contacto/` | Formulario (nombre, asunto, descripción, archivo) → contacto@katanacreacionesweb.cl |
| `/perfil/` | Cliente ve sus compras y mensajes del admin |
| `/registro/`, `/login/` | Cuentas de cliente |
| `/panel/` | Panel propio para editar productos/proyectos y enviar comentarios a clientes |
| `/admin/` | Django Admin completo (gestiona todo lo demás) |

## Instalación local

```bash
cd katana_creaciones
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_datos          # carga los 3 productos y 3 proyectos
python manage.py createsuperuser     # tu cuenta de administrador
python manage.py runserver
```

## Despliegue en DigitalOcean — Droplet (recomendado para tu caso)

1. Crea un Droplet Ubuntu 22.04/24.04 en DigitalOcean.
2. Instala dependencias:

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx
```

3. Sube el código (git clone o `scp`), crea el entorno:

```bash
cd katana_creaciones
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py seed_datos
python manage.py createsuperuser
```

4. Corre con Gunicorn (usa systemd para que quede siempre activo):

```bash
gunicorn --bind 0.0.0.0:8000 katana.wsgi
```

5. Configura Nginx como proxy reverso apuntando a `127.0.0.1:8000`, con
   `proxy_pass` y sirviendo `/static/` y `/media/`.
6. Apunta el dominio `katanacreacionesweb.cl` al Droplet y genera SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d katanacreacionesweb.cl -d www.katanacreacionesweb.cl
```

7. Define las variables de entorno en producción:

```bash
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="una-clave-larga-y-aleatoria"
export DJANGO_ALLOWED_HOSTS="katanacreacionesweb.cl,www.katanacreacionesweb.cl"
export EMAIL_HOST_PASSWORD="tu-clave-smtp"
```

## Alternativa dentro de DigitalOcean: App Platform

Si prefieres no administrar el servidor: **App Platform** despliega Django
directamente desde tu repositorio Git (GitHub), con:

- SSL automático y dominio personalizado
- Despliegues automáticos con cada `git push`
- Base de datos gestionada (Managed PostgreSQL) como add-on
- Variables de entorno desde el panel web

Solo necesitas un `Procfile` o comando de inicio: `gunicorn katana.wsgi`.
Para tu proyecto actual (SQLite + archivos locales) el Droplet es más simple
y económico; App Platform conviene cuando migres a PostgreSQL y quieres
CI/CD automático.

## Notas

- Los archivos adjuntos del formulario se guardan en `media/contacto/` y se
  adjuntan al email si el backend SMTP lo soporta.
- Los links de demo de ForestIA, Wisapp y ConceTour3D se agregan en el campo
  `url_demo` del modelo Proyecto (desde `/panel/` o `/admin/`) y aparecen en
  el cuadro interactivo automáticamente.
