FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/

ENV PYTHONPATH="$PYTHONPATH:/code/app"

ENV APP_NAME=${APP_NAME}
ENV RELOAD=${RELOAD}
ENV HOST=${HOST}
ENV RELOAD=${RELOAD}
ENV PORT=${PORT}
ENV ORIGINS=${ORIGINS}
ENV ALLOW_CREDENTIALS=${ALLOW_CREDENTIALS}
ENV ALLOW_METHODS=${ALLOW_METHODS}
ENV ALLOW_HEADERS=${ALLOW_HEADERS}


CMD ["python", "app/main.py"]