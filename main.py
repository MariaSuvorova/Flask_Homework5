from enum import Enum
from random import choice

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()
ID = 0
tasks = []


def _get_id() -> int:
    global ID
    ID += 1
    return ID


class Status(str, Enum):
    DONE = 'выполнена'
    TODO = 'не выполнена'


class TaskIn(BaseModel, use_enum_values=True):
    title: str
    description: str
    status: Status


class Task(TaskIn, use_enum_values=True):
    id: int


def _generate_tasks(task_quality: int = 10) -> None:
    tasks.extend([Task(id=_get_id(), title=f'Задача{i}',
                       description=f'описание{i}', status=choice(list(Status)))
                  for i in range(1, task_quality + 1)])


@app.get('/', response_class=HTMLResponse)
async def index():
    return {'message': 'Главная страница'}


# GET /tasks — возвращает список всех задач.
@app.get('/tasks', response_model=list[Task])
async def get_tasks():
    if len(tasks) == 0:
        _generate_tasks()
    return tasks


# GET /tasks/{id} — возвращает задачу с указанным идентификатором.
@app.get('/tasks/{id}', response_model=Task)
async def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail='Task not found')


# POST /tasks — добавляет новую задачу.
@app.post('/tasks', response_model=Task)
async def create_task(query: TaskIn):
    new_task = Task(id=_get_id(), title=query.title,
                    description=query.description, status=query.status)
    tasks.append(new_task)
    return new_task


# PUT /tasks/{id} — обновляет задачу с указанным идентификатором
@app.put('/tasks/{id}', response_model=Task)
async def edit_task(task_id: int, query: TaskIn):
    for task in tasks:
        if task.id == task_id:
            task.title = query.title
            task.description = query.description
            task.status = query.status
            return task
    raise HTTPException(status_code=404, detail='Task not found')


# DELETE /tasks/{id} — удаляет задачу с указанным идентификатором
@app.delete('/tasks/{id}', response_model=dict)
async def remove_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {'message': 'Successful task deletion'}
    raise HTTPException(status_code=404, detail='Task not found')


if __name__ == '__main__':
    # run('main:app', host='127.0.0.1', port=8000, reload=True)
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
