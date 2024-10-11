from django import forms

from .models import Task


# ------------------- Formulario para Tareas Principales -------------------
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task  # Modelo asociado al formulario
        fields = ['title', 'description', 'important']  # Campos a incluir en el formulario
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe un título'}),  # Widget para el título
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe una descripción'}),  # Widget para la descripción
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),  # Widget para el campo de importancia
        }

# ------------------- Formulario para Subtareas -------------------
class SubtaskForm(forms.ModelForm):
    class Meta:
        model = Task  # Modelo asociado al formulario
        fields = ['title', 'description', 'important']  # Campos a incluir en el formulario
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribe un título de subtarea'}),  # Widget para el título de subtarea
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe una descripción de subtarea'}),  # Widget para la descripción de subtarea
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),  # Widget para el campo de importancia
        }

    def __init__(self, *args, **kwargs):
        super(SubtaskForm, self).__init__(*args, **kwargs)  # Inicializa el formulario
        # Eliminamos el campo parent_task del formulario si existe
        if 'parent_task' in self.fields:
            del self.fields['parent_task']  # Elimina el campo parent_task para que no se muestre en el formulario

