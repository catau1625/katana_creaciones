# Guía de Despliegue en Render

## 1. Crear cuenta y servicios en Render

1. Ve a [render.com](https://render.com) y crea una cuenta (puedes usar GitHub login).
2. Desde el Dashboard, crea un **PostgreSQL**:
   - Nombre: `katana-db` (o el que prefieras)
   - Plan: **Free** (incluye 1 GB)
   - Guarda el **Internal Database URL** que te dará Render.

## 2. Crear Web Service

1. En el Dashboard, clic en **New → Web Service**.
2. Conecta tu repositorio de GitHub: `catau1625/katana_creaciones`.
3. Configura lo siguiente:

| Campo | Valor |
|---|---|
| **Name** | `katana-creaciones` |
| **Region** | Oregon (US West) o la más cercana |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn katana.wsgi:application` |
| **Plan** | **Free** |

## 3. Variables de entorno

En la pestaña **Environment** del Web Service, agrega:

| Variable | Valor | Notas |
|---|---|---|
| `DJANGO_SECRET_KEY` | `una-clave-segura-de-50-caracteres` | Genera una nueva, no uses la de desarrollo |
| `DJANGO_DEBUG` | `False` | En producción siempre False |
| `DJANGO_ALLOWED_HOSTS` | `tusitio.onrender.com` | Más tarde añade tu dominio propio |

> **No necesitas `DATABASE_URL` manualmente** — Render la inyecta automáticamente cuando vinculas la PostgreSQL como "managed database".

## 4. Vincular la base de datos (importante)

1. Ve a tu Web Service → **Settings**.
2. En **Databases**, clic en **Add Database**.
3. Selecciona la PostgreSQL `katana-db` que creaste.
4. Render inyectará automáticamente la variable `DATABASE_URL`.

## 5. Primer deploy

1. Clic en **Manual Deploy → Deploy latest commit**.
2. Render ejecutará `build.sh`:
   - Instalará dependencias (`psycopg2-binary`, `dj-database-url`, etc.)
   - Correrá `collectstatic`
   - Correrá `migrate` (creará las tablas en PostgreSQL)
3. Cuando termine, tu sitio estará en: `https://katana-creaciones.onrender.com`

## 6. Crear superusuario (para acceder al admin)

Desde la consola de Render (Web Service → **Shell**):

```bash
python manage.py createsuperuser
```

## 7. Datos de prueba (opcional)

Si quieres poblar la base de datos con datos iniciales:

```bash
python manage.py seed_datos
```

---

## Dominio personalizado (opcional)

1. En tu Web Service → **Settings → Custom Domains**.
2. Añade tu dominio (ej: `katanacreacionesweb.cl`).
3. Render te dará un registro DNS `CNAME` para configurar en tu proveedor de dominio.
4. Actualiza `DJANGO_ALLOWED_HOSTS` con tu dominio.

---

## Costos

| Servicio | Plan Free | Límites |
|---|---|---|
| Web Service | $0 | Se duerme tras 15 min de inactividad (tarda ~30s en despertar) |
| PostgreSQL | $0 | 1 GB storage, se borra tras 90 días de inactividad |

Para producción real con tráfico constante, considera el plan **Starter** ($7/mes web + $7/mes DB).
