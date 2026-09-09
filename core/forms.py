from django import forms
from django.contrib.auth.models import User
from .models import Producto, Proyecto, MensajeContacto, ComentarioAdmin, Compra


class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email_respuesta', 'asunto', 'descripcion', 'archivo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 6}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegistroForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'slug', 'descripcion', 'precio', 'banner_texto', 'imagen', 'activo']


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'slug', 'descripcion', 'url_demo', 'imagen', 'destacado']


class CompraForm(forms.ModelForm):
    """Para asociar manualmente un producto a un cliente desde el panel."""
    class Meta:
        model = Compra
        fields = ['cliente', 'producto', 'pagado']


class ComentarioForm(forms.ModelForm):
    """El admin envía comentarios personales a clientes."""
    class Meta:
        model = ComentarioAdmin
        fields = ['cliente', 'producto', 'mensaje']
        widgets = {'mensaje': forms.Textarea(attrs={'rows': 4})}
