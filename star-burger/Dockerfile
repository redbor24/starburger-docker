FROM tiangolo/uwsgi-nginx:python3.11

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

COPY . /app

ENV UWSGI_INI /app/uwsgi.ini

COPY starburger.conf /etc/nginx/conf.d/starburger.conf
EXPOSE 8080

RUN apt update -y && apt upgrade -y && apt install -y nodejs \
    && apt install -y npm && npm install -g core-js@^3 \
    && npx browserslist@latest --update-db \
    && npm ci --dev
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
