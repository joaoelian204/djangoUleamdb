from django.contrib.auth.models import User  # Importa el modelo de usuario de Django
from django.db import models  # Importa el módulo de modelos de Django


# Define el modelo Task que hereda de models.Model
class Task(models.Model):
# Define los campos del modelo Task
    # Título de la tarea, con un máximo de 100 caracteres
    title = models.CharField(max_length=100) 
    # Descripción de la tarea, puede estar vacío
    description = models.TextField(blank=True)  
    # Indica si la tarea es importante (True o False)
    important = models.BooleanField(default=False)
    # Fecha de creación de la tarea, se establece automáticamente al crear
    created = models.DateTimeField(auto_now_add=True)
    # Fecha de finalización, puede ser nula o estar vacía
    datecompleted = models.DateTimeField(null=True, blank=True)
    # Relación con el modelo User, se elimina la tarea si se elimina el usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Relación de tarea padre, puede ser nula y se elimina si se elimina la tarea padre (Subtareas)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subtasks', null=True, blank=True)

    def __str__(self):  # Método para representar el objeto Task como una cadena
        # Devuelve el título de la tarea y el nombre de usuario del creador
        return f"{self.title} - by {self.user.username}"

    @property  # Propiedad para verificar si la tarea está completada
    def completed(self):
        # Devuelve True si hay una fecha de finalización
        return self.datecompleted is not None
