from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    """Servicios que ofrece Katana Creaciones Web."""
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField(help_text='Precio en CLP')
    banner_texto = models.CharField(max_length=200, blank=True, help_text='Frase entretenida para el banner')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    """Proyectos en los que has trabajado."""
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField()
    url_demo = models.URLField(blank=True, help_text='Link al sitio para mostrarlo en el cuadro interactivo')
    imagen = models.ImageField(upload_to='proyectos/', blank=True, null=True)
    destacado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    """Productos comprados por cada cliente registrado."""
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.cliente.username} - {self.producto}'


class MensajeContacto(models.Model):
    """Mensajes que llegan desde el formulario de contacto."""
    nombre = models.CharField(max_length=120)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='contacto/', blank=True, null=True)
    email_respuesta = models.EmailField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.asunto} - {self.nombre}'


class ComentarioAdmin(models.Model):
    """Comentarios personales que el administrador envía a clientes,
    asociados a un producto/servicio en particular."""
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Para {self.cliente.username}: {self.mensaje[:40]}'
