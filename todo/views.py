from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task

# Create your views here.

def parse_due_at(value):
    if value:
        dt = parse_datetime(value)
        return make_aware(dt) if dt else None
    return None

def index(request):
    if request.method == 'POST':
        due_at_value = request.POST.get('due_at')
        task = Task(
            title=request.POST['title'],
            due_at=parse_due_at(due_at_value)
        )
        task.save()
    
    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')
    
    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        due_at_value = request.POST.get('due_at')
        task.title = request.POST['title']
        task.due_at = parse_due_at(due_at_value)
        task.save()
        return redirect('detail', task.id)

    context = {
        'task': task,
    }
    return render(request, 'todo/edit.html', context)
  
def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect('index')
  
def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    task.completed = True
    task.save()
    return redirect(index)
