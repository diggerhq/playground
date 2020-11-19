FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash gcc postgresql-dev python3-dev musl-dev
# ENV STATIC_URL /static
# ENV STATIC_PATH /var/www/app/static
WORKDIR code
COPY requirements.txt /tmp
COPY . /code
RUN pip install -r /tmp/requirements.txt
COPY start.sh /tmp/start.sh
EXPOSE 8080
ENTRYPOINT bash /tmp/start.sh
