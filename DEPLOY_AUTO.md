# Guía: despliegue de Katana Creaciones Web

> Actualizado: 2026-11-14 · Repositorio: `catau1625/katana_creaciones` · Sitio: https://katanacreacionesweb.cl

---

## 0. Estado actual: ✅ AUTO-DEPLOY ACTIVO

- **Cada `git push` a `main` despliega automáticamente** vía GitHub Actions (~20-30 s). Ver pestaña **Actions** del repo.
- Workflow: `.github/workflows/deploy.yml` (SSH al droplet → `git reset --hard origin/main` → `pip install` → `migrate` → `collectstatic` → restart gunicorn).
- Probado el 2026-11-14 con el commit `30e7053` (run en verde, 18 s).
- Verificación rápida de que el sitio responde:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://katanacreacionesweb.cl/   # esperado: 200
```

> ⚠️ Nota sobre verificaciones por contenido: Whitenoise hashea los nombres de archivos estáticos (ej. `crecimiento.57934cdac0a9.mp4`), así que para buscar un archivo en el HTML hay que grepear el nombre **sin** la extensión: `grep -c "crecimiento"` en vez de `grep -c "crecimiento.mp4"`.

---

## 1. Arquitectura

| Pieza | Dónde está | Deploy |
|---|---|---|
| Sitio Katana (Django 4.2, app `core`) | **Droplet DigitalOcean `143.198.173.51`** (`/home/katana/katana_creaciones`, nginx → gunicorn → Django) | ✅ **Auto (GitHub Actions + SSH)** |
| Base de datos de Katana | **Supabase** (PostgreSQL, ver `DATABASE_URL` en `/home/katana/katana_creaciones/.env` del droplet — NO está en git) | No aplica |
| ForestIA (proyecto) | Droplet propio `159.89.138.58` (`/opt/forestia`) | ✅ Auto (GitHub Actions propio) |
| Página ForestIA dentro de Katana | Este repo (`/proyectos/forestia/`) | Auto (vía deploy de Katana) |

Reglas de oro:
- **Nunca** tocar producción con la `db.sqlite3` local: la BD real es Supabase.
- Cada deploy corre `collectstatic` (el sitio usa `CompressedManifestStaticFilesStorage` de whitenoise → URLs estáticos con hash).
- Dominio detrás de **Cloudflare** (proxy naranja): los cambios DNS no exponen la IP del servidor.
- El `.env` de producción vive solo en el droplet; no subirlo a git.

---

## 2. Configuración del auto-deploy (ya realizada el 2026-11-14)

Referencia por si hay que recrearla o rotar claves:

### Secretos del repo (GitHub → Settings → Secrets and variables → Actions)

| Secreto | Valor |
|---|---|
| `KATANA_HOST` | `143.198.173.51` |
| `KATANA_USER` | `katana` |
| `KATANA_SSH_KEY` | Clave privada ed25519 (pareja de `~/.ssh/katana_deploy.pub` en el Mac del dueño) |

### En el droplet (ya aplicado)

- Clave pública en `/home/katana/.ssh/authorized_keys` (permisos 700/600, dueño `katana`).
- `sudo` sin contraseña para reiniciar el servicio: `/etc/sudoers.d/katana-gunicorn` con `katana ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart gunicorn`.

### Acceso del dueño al droplet

- **Consola web de DigitalOcean** (como root). El acceso SSH directo como root está deshabilitado (`Permission denied (publickey)`); los comandos de emergencia se corren directo en la consola web, sin prefijo `ssh`.

---

## 3. Deploy MANUAL (fallback, solo si el pipeline falla)

En la consola web del droplet (como root):

```bash
su - katana -c "cd /home/katana/katana_creaciones && git fetch origin && git reset --hard origin/main && ./venv/bin/pip install -r requirements.txt && ./venv/bin/python manage.py migrate --noinput && ./venv/bin/python manage.py collectstatic --noinput"
systemctl restart gunicorn
```

Verificación: `curl -s -o /dev/null -w "%{http_code}\n" https://katanacreacionesweb.cl/` → `200`.

---

## 4. Resumen de URLs y referencias

| Qué | URL / dato |
|---|---|
| Repo Katana | https://github.com/catau1625/katana_creaciones |
| Sitio | https://katanacreacionesweb.cl |
| Página del proyecto | https://katanacreacionesweb.cl/proyectos/forestia/ |
| Plataforma ForestIA | https://forestia.katanacreacionesweb.cl (Droplet `159.89.138.58`, auto-deploy propio) |
| Admin Katana | https://katanacreacionesweb.cl/admin/ |
| Panel interno Katana | https://katanacreacionesweb.cl/panel/ |
| Workflow de referencia (ForestIA) | https://github.com/catau1625/ForestIA/blob/main/.github/workflows/deploy.yml |

## 5. Checklist de mantenimiento

- [x] Identificar hosting → **Droplet `143.198.173.51`** (no App Platform)
- [x] Deploy del commit `1c2937f` (videos HD ForestIA) → en producción
- [x] Activar auto-deploy → GitHub Actions + SSH (workflow `deploy.yml`)
- [x] Probar con un push vacío → run verde en 18 s (2026-11-14)
- [ ] (Opcional) Crear superusuario de ForestIA en su droplet: `ssh root@159.89.138.58 'cd /opt/forestia && docker compose exec -T web python manage.py createsuperuser'`
- [x] Desactivar los 6 servicios de ejemplo del seed (`0002_seed_catalogo`, quedaron `activo=False`) y eliminar los 3 proyectos de ejemplo → hecho el 2026-11-14 vía `manage.py shell`
