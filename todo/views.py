from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task

# Create your views here.
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            due_at = None
            due_at_value = request.POST.get('due_at', '').strip()
            if due_at_value:
                parsed = parse_datetime(due_at_value)
                if parsed is not None:
                    due_at = make_aware(parsed) if parsed.tzinfo is None else parsed
            task = Task.objects.create(title=title, due_at=due_at)
            priority = request.POST.get('priority', 'low')
            if 'task_priorities' not in request.session:
                request.session['task_priorities'] = {}
            request.session['task_priorities'][str(task.id)] = priority
            request.session.modified = True
        return redirect('index')

    tasks = Task.objects.all()
    if request.GET.get('filter') == 'active':
        tasks = tasks.filter(completed=False)

    if request.GET.get('order') == 'due':
        tasks = tasks.order_by('due_at')
    else:
        tasks = tasks.order_by('-posted_at')

    task_priorities = request.session.get('task_priorities', {})
    tasks_with_priority = []
    for task in tasks:
        priority = task_priorities.get(str(task.id), 'low')
        tasks_with_priority.append({'task': task, 'priority': priority})

    context = {
        'tasks_with_priority': tasks_with_priority,
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

    task_priorities = request.session.get('task_priorities', {})
    current_priority = task_priorities.get(str(task_id), 'low')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            task.title = title

        due_at_value = request.POST.get('due_at', '').strip()
        if due_at_value:
            parsed = parse_datetime(due_at_value)
            if parsed is not None:
                task.due_at = make_aware(parsed) if parsed.tzinfo is None else parsed
            else:
                task.due_at = None
        else:
            task.due_at = None

        task.save()

        priority = request.POST.get('priority', 'low')
        if 'task_priorities' not in request.session:
            request.session['task_priorities'] = {}
        request.session['task_priorities'][str(task_id)] = priority
        request.session.modified = True
        return redirect('detail', task.id)

    context = {
        'task': task,
        'priority': current_priority,
    }
    return render(request, 'todo/edit.html', context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    if 'task_priorities' in request.session:
        request.session['task_priorities'].pop(str(task_id), None)
        request.session.modified = True
    return redirect('index')


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.completed = True
    task.save()
    return redirect('index')
