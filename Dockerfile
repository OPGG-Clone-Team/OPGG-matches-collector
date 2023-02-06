FROM python:3.10.9

COPY . /app

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]