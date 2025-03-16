from .models import Usuario

class UsuarioFactory:
    @staticmethod
    def crear_usuario(username, email, password, rol):
        if rol not in dict(Usuario.ROLES):
            raise ValueError("Rol no válido")

        usuario = Usuario(username=username, email=email, rol=rol)
        usuario.set_password(password)  # Hash de la contraseña
        usuario.save()
        return usuario
