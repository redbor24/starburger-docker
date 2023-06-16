FROM tiangolo/uwsgi-nginx:python3.11

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

COPY . /app/star-burger
COPY prestart.sh /app/prestart.sh
COPY uwsgi.ini /app/uwsgi.ini
COPY starburger.conf /etc/nginx/conf.d/starburger.conf

ENV UWSGI_INI /app/uwsgi.ini

WORKDIR /app/star-burger
EXPOSE 8080
