from loguru import logger as LOG
import json
import os
import re

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
import requests as r
import uvicorn

from db.sqllite import (
    create_connection,
    create_task,
    create_table,
    update_task,
    get_task,
    get_tasks
)

database_conn = create_connection('./db/local.db')
create_table(database_conn)

AI_DEVS_API_ULR = "https://tasks.aidevs.pl"
AI_DEVS_API_KEY = os.environ['TASK_API_KEY']

class AuthorizationPacket(BaseModel):
    taskName: str

class Answer(BaseModel):
    token: str
    body: str
    taskName: str
    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

def save_new_task(taskName):
    task = get_task(database_conn, (taskName,)).fetchone()
    if (not task):
        create_task(database_conn, (taskName, False))
    

@app.post('/authorize')
async def authorize(auth: AuthorizationPacket):
    resp = r.post(f'{AI_DEVS_API_ULR}/token/{auth.taskName}',
                  json={'apikey': AI_DEVS_API_KEY})
    if resp.status_code == 200:
        save_new_task(auth.taskName)
    return resp.json()


@app.get('/getTask')
async def getTask(token: str, question: str = None):
    if question:
        resp = r.post(f'{AI_DEVS_API_ULR}/task/{token}', data={'question': question})
    else:
        resp = r.get(f'{AI_DEVS_API_ULR}/task/{token}')
    return resp.json()


@app.post('/sendAnswer')
async def sendAnswer(answer: Answer):
    try:
        if answer.body.startswith('[') or answer.body.startswith('{'):
            json_output = json.loads(answer.body)
        else:
            json_output = answer.body
        LOG.info(json_output)
    except SyntaxError:
        return Response(content="Incorrect json", status_code=400)
    resp = r.post(f'{AI_DEVS_API_ULR}/answer/{answer.token}', json={'answer': json_output})
    if (resp.status_code == 200):
        update_task(database_conn, (True, answer.taskName,)) 
    LOG.info(resp.request.__dict__)
    return resp.json()

@app.get('/tasks')
async def getTasks():
    return [{'name': t[1], 'isComplete': bool(t[2])} for t in get_tasks(database_conn).fetchall()]

def transcribe(client: OpenAI, file_path: str) -> str:
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file,
    )
    return transcription.text

@app.get('/whisper')
async def get_whisper():
    resp = r.post(f'{AI_DEVS_API_ULR}/token/whisper',
                  json={'apikey': AI_DEVS_API_KEY})

    resp = r.get(f'{AI_DEVS_API_ULR}/task/{resp.json()["token"]}')
    message: str = resp.json()['msg']
    audio_link: str = re.findall(r'https://tasks.*\.mp3', message)[0]

    client = OpenAI()
    audio_file_path = 'assets/audio.mp3'
    try:
        transcription = transcribe(client, audio_file_path)
        return Response(transcription)
    except FileNotFoundError:
        with open(audio_file_path,'wb+') as audio_file:
            response = r.get(audio_link)
            audio_file.write(response.content)
        return Response(transcribe(client, audio_file_path))

    


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3001, reload=True)