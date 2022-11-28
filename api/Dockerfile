FROM python:3.11

RUN apt update -y && apt install -y \
    gcc openssl \
    mariadb-common libmariadb3 libmariadb-dev \
    libpq5 libpq-dev postgresql-common

RUN python -m venv /venv

COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install -r /requirements.txt

COPY ./entrypoint.sh /entrypoint

WORKDIR /app

COPY ./src ./src

EXPOSE 5000

ENTRYPOINT ["/entrypoint"]
CMD ["/venv/bin/python", "-m", "flask", "--app", "src.main", "--debug", "run", "--host", "0.0.0.0"]
