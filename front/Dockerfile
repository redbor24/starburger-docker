FROM python:3.9.17-slim-bullseye
RUN apt update -y && apt upgrade -y && apt install -y nodejs \
    && apt install -y npm && npm install -g core-js@^3

COPY package*.json /app/front/

WORKDIR /app/front
RUN npm ci --dev

COPY bundles-src/ /app/front/bundles-src/
COPY assets/ /app/front/assets/

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
CMD /bin/bash