FROM python

WORKDIR /app/EPT-Shop
ADD ./requirements.txt .
RUN pip install -r requirements.txt

ADD ./static/ ./static/
ADD ./templates/ ./templates/
ADD ./app.py ./app.py
ADD ./flag.txt /flag.txt

EXPOSE 8000

STOPSIGNAL SIGKILL

CMD ["python", "-b", "app.py"]