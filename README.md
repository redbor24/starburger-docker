# Учебный проект [Devman](http://Devman.org) "Разворачиваем сайт в Docker-е"

Данный проект нацелен на разворачивание готового сайта на Django и Node.JS с использованием БД Postgres посредством 
Docker-а на удалённом сервере.

## Исходный Docker-образ
Создавать образ сайта будем на базе Docker-образа [tiangolo](https://github.com/tiangolo/uwsgi-nginx-docker/tree/master), 
который уже имеет на борту `Nginx` и `uwsgi`.

## Структура каталогов
 - `dev/` - скрипты, конфигурация и `docker-compose.yaml` для `development` деплоя.
 - `prod/` - скрипты, конфигурация и `docker-compose.yaml` для `production` деплоя.
 - `star-burger/` - исходный код бэка проекта.
 - `front/` - исходный код фронта проекта.

### Подготовка
Для запуска сайта требуется файл `.env` со следующим содержимым:
 - **SECRET_KEY**=<[секретный ключ Django](https://www.educative.io/answers/how-to-generate-a-django-secretkey)>
 - **YANDEX_GEOCODER_API**=<[ключ Yandex GeoAPI](https://developer.tech.yandex.ru/services)>

   _Если остались вопросы можно посмотреть [сюда](https://dvmn.org/encyclopedia/api-docs/yandex-geocoder-api/)._

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

В папках `/dev` и `/prod` находятся файлы `.env-example`, предзаполненные значениями, которые не требуют изменения для
простого запуска сайта.

На основе файла `.env-example` в нужной вам папке создайте `.env`-файл, дописав в него вышеописанные параметры.

### Deploymant

#### Варианты деплоя
Проект может быть развёрнут в режиме `разработчика` и `production`-режиме. 
Переключение между ними выполняется посредством использования 
[Docker-context](https://docs.docker.com/engine/context/working-with-contexts/).

Для работы с удалённым сервером необходимо [создать](https://code.visualstudio.com/docs/containers/ssh) `Docker-context`.
```shell
docker context create starburger-prod --docker host=ssh://<user>@<remote_host_IP>
```
 - _Подставьте нужные вам значения пользователя на удалённом сервере и IP-адреса удалённого сервера_

Пример:
```shell
docker context create starburger-prod --docker host=ssh://root@12.23.34.45
```
Эта команда создаст `docker context` с подключением к серверу с IP-адресом `12.23.34.45` под пользователем `root`.

Переключение между контекстами:
```shell
docker context use <context-name>
```

#### Порт сайта
Сейчас сайт отзывается на порту `8080`, а не на `80`. Это сделано специально,
во избежание конфликтов с уже имеющимися сервисами, которые уже сидят на 80-ом порту и помешают протестировать 
сайт при первом запуске.

Чтобы изменить порт сайта, скорректируйте строку в файле `./dev/docker-compose.yaml` или 
`./prod/docker-compose.yaml`:
```yaml
services:
  ...
  back:
    ...
    ports:
      - 8080:8080  << впишите перед двоеточием нужный вам порт
```


#### Development deploy
Разворачивание и запуск сайта в локальном Docker-е:
```shell
docker context use default
cd ./dev
docker compose up -d --build
``` 
Будет выполнена сборка фронтенда, статики, применены миграции и запущен сайт в Docker-е разработчика.
 - _Вызов применения миграций и сборки статики прописан в скрипте `./prestart.sh`._ 

Создайте суперпользователя Django
```shell
docker exec -it dev-back-1 python manage.py createsuperuser
```
Откройте сайт [http://localhost:8080](http://localhost:8080).


#### Production deploy
Разворачивание и запуск сайта в удалённом Docker-е:
```shell
docker context use starburger-prod
cd ./prod
docker compose up -d --build
``` 
Будет выполнена сборка фронтенда, статики, применены миграции и запущен сайт в Docker-е на удалённом сервере.
 - _Вызов применения миграций и сборки статики прописан в скрипте `./prestart.sh`._ 

Создайте суперпользователя Django
```shell
docker exec -it prod-back-1 python manage.py createsuperuser
```
Откройте сайт [http://<IP-адрес вашего сервера>:8080](http://:8080).


### Локальный запуск проекта *без* использования `Docker`
Перейдите в папку `star-burger` с исходным кодом проекта.

Активируйте виртуальное окружение:
```shell
venv\scripts\activate
```

Создайте `.env`-файл с нужными вам значениями параметров, согласно приведённому выше описанию. 

#### Сборка фронтенда
[Установите Node.js](https://nodejs.org/en/), если у вас его ещё нет.

Проверьте, что `Node.js` и его пакетный менеджер корректно установлены. Если всё исправно, то терминал выведет их версии:

```shell
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

```shell
cd star-burger
npm ci --dev
```

Выполните сборку фронтенда:

*nix:
```shell
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```
Windows:
```shell
.\node_modules\.bin\parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
```

Выполните миграции:
```shell
python manage.py makemigrations
```

Создайте суперпользователя Django:
```shell
python manage.py createsuperuser
```

Запустите сайт:
```shell
python manage.py runserver
```
Перейдите по указанной ссылке. 