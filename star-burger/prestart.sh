#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
SECRET_KEY=empty python manage.py migrate --noinput
SECRET_KEY=empty python manage.py collectstatic --noinput
