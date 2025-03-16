from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PerfilUsuarioView, RegistroUsuarioView

urlpatterns = [
    #path para crear usuario
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),  # Crear usuario
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login con JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refrescar token
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),  # Obtener perfil con Bearer Token
]
