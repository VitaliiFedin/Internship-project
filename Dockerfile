FROM python:3.11-slim

RUN mkdir "code"

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


COPY . /code/

WORKDIR /code/app


CMD ["python", "main.py"]