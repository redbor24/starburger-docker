# Учебный проект [Devman](http://Devman.org) "Разворачиваем сайт в Docker-е"

Данный проект нацелен на разворачивание готового сайта на Django и Node.JS с использованием БД Postgres посредством 
Docker-а на удалённом сервере.

## Исходный Docker-образ
Создавать образ сайта будем на базе Docker-образа [tiangolo](https://github.com/tiangolo/uwsgi-nginx-docker/tree/master), 
который уже имеет на борту `Nginx` и `uwsgi`.

## Структура каталогов
 - `dev/` - скрипты, конфигурация и `docker-compose.yaml` для `development` деплоя.
 - `prod/` - скрипты, конфигурация и `docker-compose.yaml` для `production` деплоя.
 - `star-burger/` - исходный код проекта. Фронт и бэк в одном флаконе.

## Варианты деплоя
Проект может быть развёрнут в режиме разработчика и production-режиме. 
Переключение между ними выполняется посредством использования 
[Docker-context](https://docs.docker.com/engine/context/working-with-contexts/).

После установки Docker на локальную машину в нём уже есть `default context`, который мы будем использовать в качестве
контекста разработки:
```commandline
> docker context list
NAME                TYPE                DESCRIPTION                               DOCKER ENDPOINT                             KUBERNETES ENDPOINT   ORCHESTRATOR
default *           moby                Current DOCKER_HOST based configuration   npipe:////./pipe/docker_engine
...
```

Для работы с удалённым сервером необходимо [создать](https://code.visualstudio.com/docs/containers/ssh) ещё один
`Docker-context`.
```commandline
docker context create starburger-prod --docker host=ssh://<user>@<remote_host_IP>
```
 - _Подставьте нужные вам значения пользователя на удалённом сервере и IP-адреса удалённого сервера_

Переключение между контекстами:
```commandline
docker context use <context-name>
```

### Подготовка
Для обоих режимов запуска сайта требуется файл `.env` со следующим содержимым:
 - **SECRET_KEY**=<[секретный ключ Django](https://www.educative.io/answers/how-to-generate-a-django-secretkey)>
 - **YANDEX_GEOCODER_API**=<[ключ Yandex GeoAPI](https://developer.tech.yandex.ru/services)>

   _Если что-то осталось непонятным можно ещё [сюда](https://dvmn.org/encyclopedia/api-docs/yandex-geocoder-api/) 
   посмотреть._
 - **DEBUG**=

   _Может иметь значения `True` или `False`_

 - **DATABASE_URL**=postgres://postgres:postgres@db:5432/postgres

    _Не нужно трогать, т.к. это строка подключения к БД Postgres, которая поднимается вместе с сайтом в отдельном 
   контейнере. Однако, если вы хотите подключаться к своему Postgres-у, то можете указать здесь свои параметры 
   подключения_ 

 - **ALLOWED_HOSTS**=

    _Принимает значения вида IP-адреса или имён хостов через запятую.
   Для `production`-варианта должно обязательно содержать IP-адрес удалённого сервера, иначе сайт не будет доступен
   из интернета._
 
   _Для `development`-варианта можно не заполнять._

Создайте `.env`-файлы с нужными значениями в папках `/dev` и `/prod`  

### Deploymant
#### Development deploy
Для запуска сайта в локальном Docker-е выполните:
```commandline
cd dev
docker context use default
docker compose up -d --build
``` 
Он выполнит сборку фронтенда, соберёт статику, выполнит миграции и запустит сайт в Docker-е разработчика.
Применение миграций и сборка статики прописана в скрипте `./prestart.sh`. 

##### Создайте суперпользователя Django
```commandline
docker exec -it dev-web-1 python manage.py createsuperuser
```

#### Production deploy
Для запуска сайта в удалённом Docker-е выполните
```commandline
cd prod
docker context use starburger-prod
docker compose up -d --build
``` 
Он выполнит сборку фронтенда, соберёт статику, выполнит миграции и запустит сайт в Docker-е на удалённом сервере.
Применение миграций и сборка статики прописана в скрипте `./prestart.sh`. 

##### Создайте суперпользователя Django
```commandline
docker exec -it prod-web-1 python manage.py createsuperuser
```

### Локальный запуск проекта *без* использования `Docker`
Перейдите в папку `star-burger` с исходным кодом проекта.

Активируйте виртуальное окружение:
```commandline
venv\scripts\activate
```

Создайте `.env`-файл с нужными вам значениями параметров, согласно приведённому выше описанию. 

#### Сборка фронтенда

[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что `Node.js` и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```commandline
nodejs --version
# v12.18.2
# Если ошибка, попробуйте node:
node --version
# v12.18.2

npm --version
# 6.14.5
```

Версия `Node.js` должна быть не младше 10.0. Версия `npm` 
не важна ([как обновить Node.js](https://phoenixnap.com/kb/update-node-js-version)).

Перейдите в каталог проекта и установите пакеты `Node.js`:

```commandline
cd star-burger
npm ci --dev
```

Выполните сборку фронтенда:

*nix:
```commandline
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```
Windows:
```commandline
.\node_modules\.bin\parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

Выполните миграции:
```commandline
python manage.py makemigrations
```

Создайте суперпользователя Django:
```commandline
python manage.py createsuperuser
```

Запустите сайт:
```commandline
python manage.py runserver
```
Перейдите по указанной ссылке. 