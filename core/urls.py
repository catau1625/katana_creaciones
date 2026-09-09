from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('productos/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('proyectos/<slug:slug>/', views.proyecto_detalle, name='proyecto_detalle'),
    path('contacto/', views.contacto, name='contacto'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Panel de administración personalizado
    path('panel/', views.panel_admin, name='panel_admin'),
    path('panel/productos/nuevo/', views.producto_editar, name='producto_nuevo'),
    path('panel/productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('panel/proyectos/nuevo/', views.proyecto_editar, name='proyecto_nuevo'),
    path('panel/proyectos/<int:pk>/editar/', views.proyecto_editar, name='proyecto_editar'),
    path('panel/comentarios/', views.comentario_nuevo, name='comentario_nuevo'),
    path('panel/compras/', views.compra_nueva, name='compra_nueva'),
]
