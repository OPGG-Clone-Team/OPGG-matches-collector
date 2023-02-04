FROM python:3.10.9

COPY . /app

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["export", "APP_ENV=DEVELOPMENT"]
CMD ["python", "app.py"]