# WoymMarket

## Описание проекта
---
CRM-система для управления товаром на маркетплейсах с возможностью отслеживать остатки товаров на складах

## Инструкция запуска

1) На сервере создаем SSH-ключ
``ssh-keygen -t ed25519 -C <КОММЕНТАРИЙ>``
2) Переходим по ссылке `https://github.com/ParkieV/woym-market` и заходим в Settings -> Deploy keys. Создаём новый ключ и вставляем в соответствующее окно публичный ключ созданного SSH-ключа.
3) На сервере в файл `.ssh/config` вставляем следующий текст
```
Host *
    AddKeysToAgent yes
    IdentityFile <ПУТЬ_ДО_КЛЮЧА>
```
4) Выполняем команду
``git clone git@github.com:ParkieV/woym-market.git``
5) Переходим в созданную папку `woym-market/`
6) Создаем файл `.env` со следующим содержанием
```
DB_ROOT_USER=<ИМЯ_ПОЛЬЗОВАТЕЛЯ>
DB_ROOT_PASSWORD=<НАЗВАНИЕ_ПОЛЬЗОВАТЕЛЯ>
DB_NAME=<ИМЯ_БАЗЫ_ДАННЫХ>
```
7) В папке `backend/` создаем файл `.env.<ТИП_КОНТУРА>` со следующей структурой
```
DBUSER=<ИМЯ_ПОЛЬЗОВАТЕЛЯ>
DBPASSWORD=<ПАРОЛЬ_БАЗЫ_ДАННЫХ>
DBHOST=<ХОСТ_БАЗЫ_ДАННЫХ>
RESET_DB=False
DBNAME=<ИМЯ_БАЗЫ_ДАННЫХ_В_СУБД>
DBPORT=<ПОРТ_БАЗЫ_ДАННЫХ>
SCHEDULE_UPDATE=True
MODE=<LOCAL/DEV/PROD(Для тестового контура PROD)>
YANDEX_DISK_TOKEN=<ТОКЕН_ЯНДЕКС_ДИСКА>
YANDEX_DISK_WORK_DIR=prod
USE_SENTRY=False
SENTRY_SDK_DSN=https://316d8287e77f4a2d184d9b495df0c2b8@o4506834496126976.ingest.us.sentry.io/4507912844279808
LOKI_URL=http://loki:3100/loki/api/v1/push
LOG_ENDPOINTS=True
```
8) В папке `frontend/` создаем файл `.env.<ТИП_КОНТУРА>` со следующей структурой
```
PUBLIC_BASE_URL="https://<ДОМЕН_КОНТУРА>/backend"
PUBLIC_LOCAL_BASE_URL="https://<ДОМЕН_КОНТУРА>/backend"
PUBLIC_ALLOW_NON_HTTPS=0
```
9) Возвращаемся в корневую папку проекта и устанавливаем snap и certbot
```
sudo apt install snapd
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
11) Выполняем команду
``sudo certbot certonly --standalone -d <НЕОБХОДИМЫЙ_ДОМЕН> -d www.<НЕОБХОДИМЫЙ_ДОМЕН>``
12) Выполняем команду
``docker compose -f docker-compose.<КОНТУР>.yml up --build -d``
