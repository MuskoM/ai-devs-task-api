FROM python:3.10.14-alpine3.19

WORKDIR /app

ARG TASK_API_KEY_ARG
EXPOSE 8080

COPY . .

RUN python3 -m pip install -r requirements.txt

ENV TASK_API_KEY=${TASK_API_KEY_ARG}

ENTRYPOINT [ "uvicorn", "main:app"]
CMD [ "--port", "8080", "--log-level", "info"]

LABEL author="nvi0"
LABEL project="ai_devs_2_reloaded"
LABEL version="0.1"