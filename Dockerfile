FROM python:3.6.3

COPY . /src/bonham

WORKDIR /var/www/

RUN pip install -e /src/bonham

ENTRYPOINT bonham-run
