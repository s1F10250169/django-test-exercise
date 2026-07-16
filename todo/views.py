from django.shortcuts import render,redirect
from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task

# Create your views here.
def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'],
                    due_at=make_aware(parse_datetime(request.POST['due_at'])))
        task.save()

    # セッションに優先度を保存
    priority = request.POST.get('priority', 'low')
    if 'task_priorities' not in request.session:
        request.session['task_priorities'] = {}
    request.session['task_priorities'][str(task.id)] = priority
    request.session.modified = True
    
    tasks = Task.objects.all()  
    if request.GET.get('filter') == 'active':
        tasks = tasks.filter(completed=False)
    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')
    
    # タスク情報に優先度を追加
    task_priorities = request.session.get('task_priorities', {})
    tasks_with_priority = []
    for task in tasks:
        priority = task_priorities.get(str(task.id), 'low')
        tasks_with_priority.append({'task': task, 'priority': priority})
    
    context = {
        'tasks': tasks,
        'tasks_with_priority': tasks_with_priority
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task_priorities = request.session.get('task_priorities', {})
    priority = task_priorities.get(str(task_id), 'low')
    
    context = {
        'task': task,
        'priority': priority,
    }
    return render(request, 'todo/detail.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.save()
        # セッションに優先度を保存
        priority = request.POST.get('priority', 'low')
        if 'task_priorities' not in request.session:
            request.session['task_priorities'] = {}
        request.session['task_priorities'][str(task_id)] = priority
        request.session.modified = True
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
    return redirect(index)
  
def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    task.completed = True
    task.save()
    return redirect(index)
