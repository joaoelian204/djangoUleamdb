"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para el panel de administración
    path('', views.home, name='home'),  # Ruta para la página de inicio
    path('signup/', views.signup, name='signup'),  # Ruta para la página de registro
    path('tasks/', views.tasks, name='tasks'),  # Ruta para listar tareas
    path('tasks/create/', views.create_task, name='create_task'),  # Ruta para crear una nueva tarea
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),  # Ruta para ver detalles de una tarea
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),  # Ruta para marcar una tarea como completada
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),  # Ruta para eliminar una tarea
    path('tasks/<int:task_id>/subtasks/create/', views.create_subtask, name='create_subtask'),  # Ruta para crear una subtarea (utilizada en subtareas)
    path('tasks/<int:task_id>/subtasks/<int:subtask_id>/', views.subtask_detail, name='subtask_detail'),  # Ruta para ver detalles de una subtarea (utilizada en subtareas)
    path('tasks/<int:task_id>/subtasks/<int:subtask_id>/update/', views.update_subtask, name='update_subtask'),  # Ruta para actualizar una subtarea (utilizada en subtareas)
    path('tasks/<int:task_id>/subtasks/<int:subtask_id>/toggle_completion/', views.toggle_subtask_completion, name='toggle_subtask_completion'),  # Ruta para alternar la finalización de una subtarea (utilizada en subtareas)
    path('tasks/<int:task_id>/subtasks/<int:subtask_id>/delete/', views.delete_subtask, name='delete_subtask'),  # Ruta para eliminar una subtarea (utilizada en subtareas)
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),  # Ruta para listar tareas completadas
    path('logout/', views.signout, name='logout'),  # Ruta para cerrar sesión
    path('signin/', views.signin, name='signin'),  # Ruta para iniciar sesión
]
