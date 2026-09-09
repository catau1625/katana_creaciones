from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Producto, Proyecto, Compra, ComentarioAdmin, MensajeContacto
from .forms import (ContactoForm, RegistroForm, ProductoForm, ProyectoForm,
                    ComentarioForm, CompraForm)


def es_admin(user):
    return user.is_authenticated and user.is_staff


def inicio(request):
    productos = Producto.objects.filter(activo=True)[:3]
    proyectos = Proyecto.objects.filter(destacado=True)[:3]
    return render(request, 'inicio.html', {'productos': productos, 'proyectos': proyectos})


def productos(request):
    lista = Producto.objects.filter(activo=True)
    return render(request, 'productos.html', {'productos': lista})


def producto_detalle(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    return render(request, 'producto_detalle.html', {'producto': producto})


def proyectos(request):
    lista = Proyecto.objects.all()
    return render(request, 'proyectos.html', {'proyectos': lista})


def proyecto_detalle(request, slug):
    proyecto = get_object_or_404(Proyecto, slug=slug)
    return render(request, 'proyecto_detalle.html', {'proyecto': proyecto})


def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save()
            # Envía el mensaje por email a contacto@katanacreacionesweb.cl
            archivo = f"\nArchivo adjunto: {msg.archivo.name}" if msg.archivo else ""
            send_mail(
                subject=f'[Contacto Web] {msg.asunto}',
                message=f'Nombre: {msg.nombre}\nEmail: {msg.email_respuesta}\n\n{msg.descripcion}{archivo}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
            messages.success(request, '¡Mensaje enviado! Te contactaremos pronto.')
            return redirect('contacto')
    else:
        form = ContactoForm()
    return render(request, 'contacto.html', {'form': form})


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


@login_required
def perfil(request):
    compras = Compra.objects.filter(cliente=request.user)
    comentarios = ComentarioAdmin.objects.filter(cliente=request.user)
    return render(request, 'perfil.html', {
        'compras': compras, 'comentarios': comentarios,
    })


# ---------- Panel de administración personalizado ----------

@user_passes_test(es_admin)
def panel_admin(request):
    return render(request, 'panel/base_panel.html', {
        'productos': Producto.objects.all(),
        'proyectos': Proyecto.objects.all(),
        'mensajes': MensajeContacto.objects.all()[:20],
        'comentarios': ComentarioAdmin.objects.all()[:20],
    })


@user_passes_test(es_admin)
def producto_editar(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto guardado.')
            return redirect('panel_admin')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'panel/form.html', {'form': form, 'titulo': 'Producto'})


@user_passes_test(es_admin)
def proyecto_editar(request, pk=None):
    proyecto = get_object_or_404(Proyecto, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto guardado.')
            return redirect('panel_admin')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'panel/form.html', {'form': form, 'titulo': 'Proyecto'})


@user_passes_test(es_admin)
def comentario_nuevo(request):
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario enviado al cliente.')
            return redirect('panel_admin')
    else:
        form = ComentarioForm()
    return render(request, 'panel/form.html', {'form': form, 'titulo': 'Comentario a cliente'})


@user_passes_test(es_admin)
def compra_nueva(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compra asociada al cliente.')
            return redirect('panel_admin')
    else:
        form = CompraForm()
    return render(request, 'panel/form.html', {'form': form, 'titulo': 'Asociar compra'})
