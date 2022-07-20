FROM python:3.8-alpine

RUN apk add --no-cache mariadb-connector-c-dev
RUN apk add --update --no-cache --virtual .tmp gcc musl-dev libc-dev linux-headers python3-dev jpeg-dev zlib-dev mariadb-dev build-base
RUN pip install django Pillow uWSGI django-mysql mysqlclient PyMySQL

RUN mkdir /app
COPY ./app /app
WORKDIR /app

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 manage.py migrate \
		&& yes yes | python manage.py collectstatic \
		&&  uwsgi --socket :8000 --master --enable-threads --module app.wsgi
