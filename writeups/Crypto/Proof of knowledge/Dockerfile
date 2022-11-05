FROM python:3

WORKDIR /app

COPY server.py .
COPY flag.txt .
COPY requirements.txt .
COPY templates templates

RUN pip3 install -r requirements.txt

RUN useradd ctf
USER ctf

WORKDIR /app

EXPOSE 1234
CMD [ "python3",  "server.py"]
