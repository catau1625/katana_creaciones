from django.contrib import admin
from .models import Producto, Proyecto, Compra, MensajeContacto, ComentarioAdmin


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url_demo', 'destacado')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'fecha', 'pagado')
    list_filter = ('pagado',)


@admin.register(MensajeContacto)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'nombre', 'fecha', 'leido')
    list_filter = ('leido',)


@admin.register(ComentarioAdmin)
class ComentarioAdminView(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'fecha', 'leido')
