# __Pay2U_back_4__
MVP Pay2U - все подписки в одном приложении

#### сайт доступен по адресу:
```bash
pay2u.myddns.me
```

#### документация к API доступна по адресу:
```bash
pay2u.myddns.me/api/v1/schema/docs/
```

![Github Actions main workflow](https://github.com/LynnG3/Pay2U_back_4/actions/workflows/main.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=20B2AA)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## Использованные при реализации проекта технологии
 - Docker
 - Django
 - DjangoRestFramework
 - Djoser
 - DRF Spectacular
 - Nginx
 - Python
 - PostgreSQL

## __Как развернуть проект__

### Для установки проекта потребуется выполнить следующие действия:

_Локальная настройка и запуск проекта_

Клонировать репозиторий к себе на компьютер и перейти в директорию с проектом:
```bash
git clone https://github.com/LynnG3/Pay2U_back_4.git
cd Pay2U_back_4
```
Для проекта создать и активировать виртуальное окружение, установить зависимости:
__для windows:__
```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
cd backend
```
__для linux:__
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
cd backend
```
### .env
Для корректной работы backend-части проекта, создайте в корне файл `.env` и заполните его переменными по примеру из файла `.env.example` или по примеру ниже:
```bash
POSTGRES_USER=pay2u_user
POSTGRES_PASSWORD=pay2u_password
POSTGRES_DB=pay2u
DB_NAME=pay2u
DB_HOST=db
DB_PORT=5432
SECRET_KEY=django-example-secret-key       # стандартный ключ, который создается при старте проекта
DEBUG=True
ALLOWED_HOSTS=IP_адрес_сервера, 127.0.0.1, localhost, домен_сервера,
SUPERUSER_USERNAME=admin       # переменные для автоматического создания суперюзера,
SUPERUSER_PASSWORD=admin       # если не указать, применятся стандартные из скрипта
SUPERUSER_EMAIL=admin@example.com      # вид стандартных переменных ('admin', 'admin@example.com, 'admin')
DOCKERHUB_USERNAME=dockerhubuser          # переменные для сохраниения образов на докер хаб пользователя/организации и тд
PROJECT_NAME=pay2u            # название образа для каждого контейнер сопоставимо с названием проекта
```

Установите [docker compose](https://www.docker.com/) на свой компьютер.
Для запуска проекта на локальной машине достаточно:
* Запустить проект, ключ `-d` запускает проект в фоновом режиме
* выполнить миграции
* собрать статику и скопировать её
* запустить скрипт для создания суперюзера
```bash
docker compose -f docker-compose.production.yml up --build -d
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic  && \
docker compose -f docker-compose.production.yml exec backend cp -r /app/static_backend/. /backend_static/static/
docker compose -f docker-compose.production.yml exec backend bash create_superuser_script.sh
```

## Если вы используете удаленный сервер
__Для работы на удаленном сервере потребуется:__
1. Установить Nginx
2. Отредактировать конфигурационный файл:
   ```bash
   server {
    server_name IP_адрес_сервера домен_сервера;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
   }
   ```
3. Установить ssl сертификаты и выпустить их:
4. Настроить и установить Docker
5. Перенести файл `docker-compose.production.yml с локальной машины на удаленную
6. Запустить контейнеры
7. Выполнить миграции собрать статику и скопировать её, так же как описано для локальной машины
   _Необходимые команды_
```bash
sudo apt install nginx -y                                # устанавливаем Nginx
sudo systemctl start nginx                               # запускаем Nginx
sudo nano /etc/nginx/sites-enabled/default               # заходим редактировать файл конфигурации
sudo nginx -t                                            # проверяем корректность настроек
sudo service nginx reload                                # перезапускаем Nginx
sudo service nginx status                                # проверяем что Nginx запущен и работает без ошибок
sudo apt install snapd && \                              # Устанавливаем certbot для получения SSL-сертификата
sudo snap install core && \                              # Устанавливаем certbot для получения SSL-сертификата
sudo snap refresh core && \                              # Устанавливаем certbot для получения SSL-сертификата
sudo snap install --classic certbot && \                 # Устанавливаем certbot для получения SSL-сертификата
sudo ln -s /snap/bin/certbot /usr/bin/certbot            # Устанавливаем certbot для получения SSL-сертификата
sudo certbot --nginx                                     # Запускаем certbot получаем SSL-сертификат
sudo service nginx reload                                # Сертификат автоматически сохранится в конфигурации Nginx
sudo apt update && sudo apt install curl                 # Устанавливаем Docker
curl -fSl https://get.docker.com -o get-docker.sh        # Устанавливаем Docker
sudo sh ./get-docker.sh                                  # Настраиваем Docker
sudo apt-get install docker-compose-plugin               # Настраиваем Docker
sudo nano docker-compose.production.yml                  # В этот файл перенесем содержимое из файла на локальной машине
sudo docker compose -f docker-compose.production.yml up -d # Запускаем контейнеры на удаленном сервере в фоновом режиме
```
## Автоматизация запуска при изменении в коде

__Workflow__
Для постоянного использования CI/CD интеграции и деплоя в репозитории проекта на GitHub в разделе Actions
перейти `Settings/Secret and variables/Actions` нужно прописать переменные окружения для доступа к сервисам - _Secrets_:

```
DOCKER_USERNAME                # логин в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
DOCKER_USER                    # имя пользователя для репозиториев
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa) по выбору: удаленный сервер или локальная машина
PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа по выбору: удаленный сервер или локальная машина
```
По команде `git push` в репозитории на github отрабатывают сценарии:
* __tests__ - для всех веток проверка кода по стандартам PEP8.
* __build_and_push_to_docker_hub__ - сборка и отправка образов в удаленный репозиторий на DockerHub
* __deploy__ - автоматический деплой проекта



#### Авторы

backend:
- Polina Grunina /
Telegram: @GrethenMorgan
- Denis Shtanskiy /
Telegram: @shtanskiy

frontend:
- Olga Pankrashina /
Telegram: @olyaolya2713
