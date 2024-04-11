FROM python:3.10.14-alpine3.19

WORKDIR /app

EXPOSE 8080

COPY . .

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT [ "uvicorn", "main:app"]
CMD [ "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]

LABEL author="nvi0"
LABEL project="ai_devs_2_reloaded"
LABEL version="0.1"
