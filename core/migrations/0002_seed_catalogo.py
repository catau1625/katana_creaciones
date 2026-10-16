"""Migración de datos: siembra el catálogo de servicios y proyectos
de ejemplo para que el nuevo front-end se vea completo en producción.

Es idempotente: usa get_or_create por slug, por lo que no duplica ni
sobreescribe registros existentes con el mismo slug.
"""
from django.db import migrations


SERVICIOS = [
    ("Desarrollo Web", "desarrollo-web",
     "Webs y apps a medida, rápidas, seguras y escalables.", 499000),
    ("Soporte Técnico", "soporte-tecnico",
     "Mantenimiento preventivo y correctivo con atención 24/7.", 99000),
    ("Cloud & Hosting", "cloud-hosting",
     "Infraestructura en la nube de alto rendimiento y SLA 99.9%.", 199000),
    ("Ciberseguridad", "ciberseguridad",
     "Auditorías, firewall, antivirus gestionado y respuesta a incidentes.", 299000),
    ("Redes & CCTV", "redes-cctv",
     "Diseño e instalación de redes, WiFi empresarial y videovigilancia.", 349000),
    ("Data & BI", "data-bi",
     "Paneles de datos en tiempo real y automatización de reportes.", 399000),
]

PROYECTOS = [
    ("Sistema ERP a medida", "erp-a-medida",
     "Sistema de gestión para Logística Andina con Python y PostgreSQL.", True),
    ("Tienda online omnicanal", "tienda-omnicanal",
     "E-commerce para Moda Nova con React y Node.js.", True),
    ("Portal de citas médicas", "portal-citas",
     "Agendamiento online para Clínica San Rafael con Vue y Laravel.", False),
]


def seed(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Proyecto = apps.get_model("core", "Proyecto")
    for nombre, slug, descripcion, precio in SERVICIOS:
        Producto.objects.get_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": precio,
                "activo": True,
            },
        )
    for nombre, slug, descripcion, destacado in PROYECTOS:
        Proyecto.objects.get_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "descripcion": descripcion,
                "destacado": destacado,
            },
        )


def unseed(apps, schema_editor):
    Producto = apps.get_model("core", "Producto")
    Proyecto = apps.get_model("core", "Proyecto")
    Producto.objects.filter(slug__in=[s[1] for s in SERVICIOS]).delete()
    Proyecto.objects.filter(slug__in=[p[1] for p in PROYECTOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
