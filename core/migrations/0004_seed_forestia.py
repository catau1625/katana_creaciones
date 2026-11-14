from django.db import migrations


DESCRIPCION = (
    'Plataforma de simulaciones agrícolas: carga datos de suelo, clima y especie, '
    'y genera una evolución predictiva de las plantas y las capas que las contienen, '
    'considerando el consumo de nutrientes de cada especie.'
)


def crear_forestia(apps, schema_editor):
    Proyecto = apps.get_model('core', 'Proyecto')
    Proyecto.objects.get_or_create(
        slug='forestia',
        defaults={
            'nombre': 'ForestIA',
            'descripcion': DESCRIPCION,
            'destacado': True,
        },
    )


def borrar_forestia(apps, schema_editor):
    Proyecto = apps.get_model('core', 'Proyecto')
    Proyecto.objects.filter(slug='forestia').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_proyecto_video_proyecto_video_url'),
    ]

    operations = [
        migrations.RunPython(crear_forestia, borrar_forestia),
    ]
