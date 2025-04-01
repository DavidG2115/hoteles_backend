# Backend - Hoteles de Morelia

Este proyecto es el backend del sistema de gestión multihotel **Hoteles de Morelia**, desarrollado con **Django REST Framework** y PostgreSQL. Proporciona funcionalidades completas para la administración de hoteles, empleados, habitaciones, reservaciones, servicios y reportes.

---

## Tecnologías usadas

- Python 3.12
- Django 4.x
- Django REST Framework
- PostgreSQL
- HTML (para correos)
- JWT o Token Auth (opcional)
- Signals (para patrón Observer)
- Decorators (patrón de validación)
- Factory Method (patrón de creación de usuarios)

---

## Funcionalidades principales

### Autenticación y gestión de usuarios
- Registro y login de usuarios
- Creación de empleados con roles:
  - Administrador
  - Gerente
  - Recepcionista
  - Camarista
  - Mantenimiento
  - Cliente
- Asignación de empleados a hoteles

### Gestión de hoteles y habitaciones
- CRUD de hoteles (solo administradores globales)
- CRUD de habitaciones por hotel
- Asignación de habitaciones a hoteles
- Visualización de habitaciones asignadas al empleado

### Reservaciones
- Crear reservaciones como cliente (autenticado o anónimo)
- Ver reservación por folio
- Cancelar, modificar o eliminar reservaciones (solo empleados autorizados)
- Validaciones personalizadas con **decorators**

### Correos automáticos
- Envío de correos automáticos al crear, cancelar o modificar reservaciones
- HTML personalizado con pie de página y enlaces útiles
- Uso de **signals** para desacoplar la lógica (patrón **Observer**)

### Solicitudes de modificación o cancelación
- Los recepcionistas pueden crear solicitudes
- Gerentes y administradores aprueban o rechazan
- Sistema de control y aprobación seguro y con validaciones

### Reportes
- Reporte de ocupación por fechas
- Reporte de ingresos por habitaciones y servicios
- Reporte de servicios vendidos por categoría

---

## Patrones de diseño aplicados

| Patrón          | Aplicación                                            |
|-----------------|--------------------------------------------------------|
| **Factory Method**  | Creación flexible de usuarios con roles distintos     |
| **Decorator**       | Validaciones reutilizables (estado, permisos, hotel) |
| **Observer (signals)** | Envío automático de correos ante cambios en modelos |

---

## Instalación y ejecución

1. Clona el repositorio:

```bash
git clone https://github.com/DavidG2115/hoteles-backend.git
cd hoteles-backend
```
2. Crea y activa el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Instala las dependencias:

```bash
pip install -r requirements.txt
```
4. Configura tus variables de entorno (PostgreSQL, email, etc.) en .env o settings.py.

5. Aplica las migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```
6. Ejecuta el servidor:

```bash
python manage.py runserver
```

