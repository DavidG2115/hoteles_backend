from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    #path para crear usuario
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),  # Crear usuario
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login con JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refrescar token
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),  # Obtener perfil con Bearer Token
    path('usuarios/', ListarUsuariosView.as_view(), name='obtener_usuarios'),  # Listar usuarios
    path('<int:pk>/editar/', EditarUsuarioView.as_view(), name='editar_usuario'),  # Editar usuario
    path('usuarios/<int:pk>/eliminar/', EliminarUsuarioView.as_view(), name='eliminar_usuario'), # Eliminar usuario
]
