import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import SubtaskForm, TaskForm
from .models import Task

logger = logging.getLogger(__name__)

# Vista para la página principal
def home(request):
    return render(request, 'home.html')

# Vista para el registro de usuarios
def signup(request):
    if request.method == 'GET':
        # Si el método es GET, muestra el formulario de registro
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        # Verifica que las contraseñas coincidan
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Crea un nuevo usuario
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                # Inicia sesión automáticamente al usuario
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                # Si el nombre de usuario ya existe, muestra un error
                return render(request, "signup.html", {"form": UserCreationForm, "error": "Username already exists"})
        # Si las contraseñas no coinciden, muestra un error
        return render(request, "signup.html", {"form": UserCreationForm, "error": "Passwords do not match"})

# Vista para iniciar sesión
def signin(request):
    if request.method == 'GET':
        # Si el método es GET, muestra el formulario de inicio de sesión
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        # Autentica al usuario
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            # Si la autenticación falla, muestra un error
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Username or password is incorrect'})
        else:
            # Si la autenticación es exitosa, inicia sesión y redirige a la lista de tareas
            login(request, user)
            return redirect('tasks')

# Vista para cerrar sesión
def signout(request):
    logout(request)
    return redirect('home')

# Vista para mostrar las tareas pendientes (solo accesible si el usuario está logueado)
@login_required
def tasks(request):
    # Obtiene las tareas que no tienen fecha de completado y pertenecen al usuario
    tasks = Task.objects.filter(user=request.user, parent_task__isnull=True, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks, 'tipopagina': 'Tareas Pendientes'})

# Vista para mostrar las tareas completadas
@login_required
def tasks_completed(request):
    # Obtiene las tareas completadas ordenadas por fecha de completado
    tasks = Task.objects.filter(user=request.user, parent_task__isnull=True, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks, 'tipopagina': 'Tareas Completadas'})

# Vista para crear una nueva tarea
@login_required
def create_task(request):
    if request.method == 'GET':
        # Si el método es GET, muestra el formulario para crear una tarea
        return render(request, "create_task.html", {'form': TaskForm()})
    else:
        try:
            # Intenta crear una nueva tarea con los datos del formulario
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            # Muestra un mensaje de éxito
            messages.success(request, "Tarea creada con éxito.")
            return redirect('tasks')
        except ValueError:
            # Si hay un error en los datos, muestra un error
            return render(request, "create_task.html", {'form': TaskForm(), 'error': 'Ingrese tipos de datos correctos'})

# Vista para ver los detalles de una tarea
@login_required
def task_detail(request, task_id):
    # Obtiene la tarea y sus subtareas relacionadas
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    subtasks = task.subtasks.all()

    if request.method == 'GET':
        # Muestra el formulario para editar la tarea
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form, 'subtasks': subtasks})
    else:
        try:
            # Actualiza la tarea con los datos del formulario
            form = TaskForm(request.POST, instance=task)
            form.save()
            messages.success(request, "Tarea actualizada con éxito.")
            return redirect('task_detail', task_id=task.id)
        except ValueError:
            # Si hay un error al actualizar, muestra un mensaje de error
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'subtasks': subtasks, 'error': 'Error updating task'})

# Vista para completar una tarea
@login_required
def complete_task(request, task_id):
    # Marca la tarea como completada al agregar una fecha de completado
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        messages.success(request, "Tarea completada con éxito.")
        return redirect('tasks')

# Vista para eliminar una tarea
@login_required
def delete_task(request, task_id):
    # Elimina la tarea si es una petición POST
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Tarea eliminada con éxito.")
        return redirect('tasks')
    
#---------------------- Funciones para las subtareas ----------------------#

# Vista para crear una subtarea
@login_required
def create_subtask(request, task_id):
    parent_task = get_object_or_404(Task, pk=task_id, user=request.user)
    
    if request.method == 'POST':
        # Crea la subtarea relacionada con la tarea principal
        form = SubtaskForm(request.POST)
        if form.is_valid():
            new_subtask = form.save(commit=False)
            new_subtask.user = request.user
            new_subtask.parent_task = parent_task
            new_subtask.save()
            return JsonResponse({'message': 'Subtarea creada con éxito.'})
        else:
            # Devuelve errores si el formulario no es válido
            return JsonResponse({'error': 'Formulario inválido.', 'errors': form.errors}, status=400)
    else:
        form = SubtaskForm()
    
    return render(request, 'create_subtask.html', {'form': form, 'parent_task': parent_task})

# Vista para actualizar una subtarea
@login_required
def update_subtask(request, task_id, subtask_id):
    # Obtiene la subtarea y la actualiza con los datos del formulario
    subtask = get_object_or_404(Task, id=subtask_id, user=request.user, parent_task_id=task_id)
    if request.method == 'POST':
        form = SubtaskForm(request.POST, instance=subtask)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Subtarea actualizada con éxito.'})
        else:
            # Devuelve errores si el formulario no es válido
            return JsonResponse({'error': 'Formulario inválido.', 'errors': form.errors}, status=400)
    else:
        form = SubtaskForm(instance=subtask)
    
    return render(request, 'update_subtask.html', {'form': form, 'subtask': subtask})

# Vista para marcar una subtarea como completada o incompleta
@login_required
def complete_subtask(request, task_id, subtask_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtiene la subtarea y cambia su estado de completado
                subtask = get_object_or_404(Task, id=subtask_id, user=request.user, parent_task_id=task_id)
                if subtask.datecompleted is None:
                    subtask.datecompleted = timezone.now()
                    subtask.save()
                    logger.info(f"Subtarea {subtask_id} completada con éxito por el usuario {request.user.username}")
                    message = "Subtarea completada con éxito."
                else:
                    # Marca la subtarea como incompleta
                    subtask.datecompleted = None
                    subtask.save()
                    logger.info(f"Subtarea {subtask_id} marcada como incompleta por el usuario {request.user.username}")
                    message = "Subtarea marcada como incompleta."
                
                # Verifica si todas las subtareas están completadas
                parent_task = subtask.parent_task
                all_subtasks_completed = not parent_task.subtasks.filter(datecompleted__isnull=True).exists()
                
                return JsonResponse({
                    'message': message,
                    'all_subtasks_completed': all_subtasks_completed
                })
        except Exception as e:
            logger.error(f"Error al actualizar la subtarea {subtask_id}: {str(e)}")
            return JsonResponse({'error': 'Error al actualizar la finalización de la subtarea'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido para completar la subtarea'}, status=405)

# Vista para eliminar una subtarea
@login_required
def delete_subtask(request, task_id, subtask_id):
    subtask = get_object_or_404(Task, id=subtask_id, user=request.user, parent_task_id=task_id)
    if request.method == 'POST':
        # Elimina la subtarea
        subtask.delete()
        return JsonResponse({'message': 'Subtarea eliminada con éxito.'})
    return JsonResponse({'error': 'Método no permitido para eliminar la subtarea'}, status=405)

# Vista para ver los detalles de una subtarea
@login_required
def subtask_detail(request, task_id, subtask_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    subtask = get_object_or_404(Task, pk=subtask_id, parent_task=task, user=request.user)
    return render(request, 'subtask_detail.html', {'subtask': subtask})

# Vista para alternar el estado de completado de una subtarea
@login_required
@require_POST
def toggle_subtask_completion(request, task_id, subtask_id):
    try:
        # Alterna el estado de completado de la subtarea
        subtask = get_object_or_404(Task, id=subtask_id, parent_task_id=task_id, user=request.user)
        
        if subtask.datecompleted:
            subtask.datecompleted = None
        else:
            subtask.datecompleted = timezone.now()
        
        subtask.save()

        # Verifica si todas las subtareas de la tarea padre están completadas
        parent_task = subtask.parent_task
        all_subtasks_completed = not parent_task.subtasks.filter(datecompleted__isnull=True).exists()

        return JsonResponse({
            'message': 'Subtarea actualizada con éxito.',
            'completed': subtask.datecompleted is not None,
            'all_subtasks_completed': all_subtasks_completed
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
