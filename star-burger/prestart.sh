#! /usr/bin/env bash

sleep 10;

SECRET_KEY=empty python manage.py migrate --noinput
SECRET_KEY=empty python manage.py collectstatic --noinput
