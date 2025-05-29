FROM python:3.12.9-slim

WORKDIR /abot
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]