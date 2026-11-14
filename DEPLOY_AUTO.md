# Guía de despliegue — katanacreacionesweb.cl (Droplet DigitalOcean)

> **Escenario confirmado (2026-11-14):** el sitio Katana vive en un **Droplet** (no App Platform).
> Repo: https://github.com/catau1625/katana_creaciones · Branch: `main`
> Pendiente: publicar los commits `1c2937f` (videos HD) y `3cc3f12` (demo rediseñado dark).

---

## PARTE 1 — Deploy manual AHORA (salir del paso, ~10 min)

### 1.1 Datos que necesitas reunir

| Dato | Dónde conseguirlo |
|---|---|
| **IP del Droplet** | DigitalOcean → Droplets → el droplet de Katana |
| **Usuario SSH** | El que usaste al instalar (`katana`, `root` u otro — según `DO_DEPLOY.md` es `katana`) |
| **Cómo te autenticas** | ¿Password o llave SSH? Si es password, te lo pedirá al conectar |

### 1.2 Ejecutar el deploy

```bash
ssh <USUARIO>@<IP_DEL_DROPLET>

# Dentro del droplet:
cd ~/katana_creaciones          # ajusta si la ruta es otra (p. ej. /opt/katana_creaciones)
git pull origin main            # trae 1c2937f + 3cc3f12
source venv/bin/activate        # o: source venv/bin/activate.fish según tu shell
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

### 1.3 Reiniciar la aplicación

Depende de cómo corre Gunicorn en ese droplet. Probar en orden:

```bash
# Opción A: servicio systemd
sudo systemctl restart gunicorn

# Opción B: si el servicio tiene otro nombre, listar:
systemctl list-units --type=service | grep -iE "gunicorn|katana|uwsgi"

# Opción C: si corre con tmux/nohup a mano (ver procesos):
ps aux | grep -i gunicorn
# → matar y relanzar según el comando que se vea en el proceso
```

### 1.4 Verificar que quedó publicado

```bash
curl -s https://katanacreacionesweb.cl/proyectos/forestia/ | grep -c "crecimiento.mp4"
# 1 = deploy OK con videos HD

curl -s https://katanacreacionesweb.cl/static/forestia/demo.html | grep -c "kimi-icon"
# 0 = demo rediseñado activo (ya no depende del runtime de widgets)
```

> ⚠️ **Si el `collectstatic` usa manifiesto** (whitenoise `CompressedManifestStaticFilesStorage` cuando `DEBUG=False`): debe correrse en cada deploy, tal como arriba. Sin eso, los CSS/JS nuevos no se servirán.

---

## PARTE 2 — Auto-deploy con GitHub Actions (para no volver a hacer lo anterior a mano)

Una vez hecho el manual y verificado, automatizar. Es el mismo mecanismo que ya funciona en el repo ForestIA (deploy en ~58 s por push).

### 2.1 Preparar acceso SSH dedicado al droplet

En tu Mac:

```bash
# Si no existe ya una clave para este droplet:
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_katana -N "" -C "katana-deploy"
cat ~/.ssh/id_ed25519_katana.pub
```

Copiar la salida y agregarla en el droplet:

```bash
ssh <USUARIO>@<IP_DEL_DROPLET>
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "PEGA_AQUI_LA_CLAVE_PUBLICA" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Probar desde el Mac (sin password):

```bash
ssh -i ~/.ssh/id_ed25519_katana <USUARIO>@<IP_DEL_DROPLET> "echo OK"
```

### 2.2 Crear los secretos en GitHub

En https://github.com/catau1625/katana_creaciones → **Settings → Secrets and variables → Actions → New repository secret**:

| Secreto | Valor |
|---|---|
| `KATANA_HOST` | IP del droplet |
| `KATANA_USER` | usuario SSH |
| `KATANA_SSH_KEY` | contenido completo de `~/.ssh/id_ed25519_katana` (la **privada**) |

```bash
# Para copiar la privada completa al portapapeles (Mac):
cat ~/.ssh/id_ed25519_katana | pbcopy
```

### 2.3 Crear el workflow

Archivo nuevo `.github/workflows/deploy.yml` en el repo:

```yaml
name: Deploy to Droplet

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Desplegar vía SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.KATANA_HOST }}
          username: ${{ secrets.KATANA_USER }}
          key: ${{ secrets.KATANA_SSH_KEY }}
          script: |
            set -e
            cd ~/katana_creaciones
            git fetch origin
            git reset --hard origin/main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate --noinput
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```

> **Ajustes posibles según el servidor** (verificarlos en el deploy manual de la Parte 1):
> - Ruta del repo (`cd ~/katana_creaciones`)
> - Nombre del servicio (`gunicorn` — anotar el real de la Opción 1.3-B)
> - Si el usuario no tiene sudo sin password: agregarlo a sudoers con `NOPASSWD` solo para systemctl, o ejecutar el reinicio con otro mecanismo.

### 2.4 Probar el pipeline

```bash
git commit --allow-empty -m "probar auto-deploy"
git push
```

Luego: GitHub → repo → pestaña **Actions** → debe salir un run verde → verificar con el `curl` del paso 1.4.

A partir de ahí: **cada push a `main` se publica solo.**

---

## PARTE 3 — Referencia rápida de mantenimiento

| Tarea | Comando / lugar |
|---|---|
| Ver si hay commits sin publicar | `git log origin/main..HEAD` (local) o comparar en GitHub |
| Forzar deploy manual | GitHub → Actions → "Deploy to Droplet" → **Run workflow** |
| Ver logs del servidor | `ssh <USUARIO>@<IP> 'sudo journalctl -u gunicorn -n 100'` |
| Ver logs de Nginx | `ssh <USUARIO>@<IP> 'sudo tail -50 /var/log/nginx/error.log'` |
| La BD de producción es **Supabase** | Nunca usar `db.sqlite3` local; las migraciones corren contra Supabase vía `DATABASE_URL` del `.env` del droplet |

## Checklist

- [ ] 1.2 Deploy manual ejecutado (commits 1c2937f y 3cc3f12)
- [ ] 1.4 Verificación `crecimiento.mp4` = 1 y `kimi-icon` = 0
- [ ] 2.1 Clave SSH dedicada probada (`echo OK` sin password)
- [ ] 2.2 Secretos `KATANA_HOST` / `KATANA_USER` / `KATANA_SSH_KEY` creados
- [ ] 2.3 Workflow `.github/workflows/deploy.yml` commiteado y pusheado
- [ ] 2.4 Run de prueba verde + verificación pública
