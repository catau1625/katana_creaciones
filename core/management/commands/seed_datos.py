"""Carga los 3 productos y 3 proyectos iniciales.
Uso: python manage.py seed_datos"""
from django.core.management.base import BaseCommand
from core.models import Producto, Proyecto


class Command(BaseCommand):
    help = 'Carga productos y proyectos iniciales'

    def handle(self, *args, **options):
        productos = [
            dict(nombre='Página Web', slug='pagina-web',
                 descripcion='Diseño y desarrollo de sitios web personalizados, '
                             'responsivos y optimizados para buscadores. Incluye '
                             'dominio, hosting orientado y panel autoadministrable.',
                 precio=350000,
                 banner_texto='⚔️ Tu presencia online con filo de katana'),
            dict(nombre='Aplicaciones', slug='aplicaciones',
                 descripcion='Desarrollo de aplicaciones web y móviles a medida: '
                             'sistemas de gestión, tiendas online, apps con '
                             'autenticación, pagos y notificaciones.',
                 precio=800000,
                 banner_texto='🚀 Apps que cortan la competencia'),
            dict(nombre='Mantenimiento', slug='mantenimiento',
                 descripcion='Soporte mensual: actualizaciones de seguridad, '
                             'respaldos, monitoreo de rendimiento, cambios de '
                             'contenido y atención de incidentes.',
                 precio=80000,
                 banner_texto='🛡️ Tu sitio protegido, siempre afilado'),
        ]
        for p in productos:
            Producto.objects.update_or_create(slug=p['slug'], defaults=p)

        proyectos = [
            dict(nombre='ForestIA', slug='forestia',
                 descripcion='Plataforma de inteligencia artificial para el '
                             'monitoreo y gestión de bosques nativos.',
                 url_demo='', destacado=True),
            dict(nombre='Wisapp', slug='wisapp',
                 descripcion='Aplicación de mensajería inteligente con '
                             'asistente de IA integrado para equipos de trabajo.',
                 url_demo='', destacado=True),
            dict(nombre='ConceTour3D', slug='concetour3d',
                 descripcion='Tour virtual 3D interactivo de la ciudad de '
                             'Concepción con puntos de interés y realidad aumentada.',
                 url_demo='', destacado=True),
        ]
        for pr in proyectos:
            Proyecto.objects.update_or_create(slug=pr['slug'], defaults=pr)

        self.stdout.write(self.style.SUCCESS('✅ Datos iniciales cargados'))
