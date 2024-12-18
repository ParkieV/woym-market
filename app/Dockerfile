FROM python:3.10.5

WORKDIR /app

RUN mkdir -p ./data

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt 

COPY . .

CMD ["python3", "main.py"]