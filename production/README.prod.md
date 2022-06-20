# Разворачивание в `prod`

1. Клонируйте репозиторий и перейдите в созданную директорию
```sh
git clone https://github.com/gennadis/self-storage.git
```

2. Переименуйте файл `.env.dev.example` на `.env.dev` и заполните его по образцу
```sh
SECRET_KEY=<secret_key>
DEBUG=False
ALLOWED_HOSTS=<example.com www.example.com>

YOOKASSA_API_KEY=<yookassa_api_key>
YOOKASSA_SHOP_ID=<yookassa_shop_id>

POSTGRES_USER=<storage_user>
POSTGRES_PASSWORD=<storage_password>
POSTGRES_DB=<storage_db>
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_HOST=db
POSTGRES_PORT=5432

EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=<your_email>
EMAIL_HOST_PASSWORD=<your_password>
EMAIL_PORT=587
DEFAULT_FROM_EMAIL=<your_email>

DOCKERIZED=True

BASE_URL=https://example.com
CSRF_TRUSTED_ORIGINS=https://example.com

ROLLBAR_TOKEN=<rollbar_token>
```

3. Запустите скрипт для автоматического деплоя
- Обновит код репозитория
- Соберёт контейнеры
- Подгрузит статику фронтенда
- Зарегистрирует деплой на rollbar
- Сообщит об успешном завершении деплоя
```sh
./deploy.sh
```

4. В файле `production/data/ngin/conf.d/nginx.conf` в отмеченных комментариями местах замените доменное имя 

5. Запустите скрипт инициализации `letsencrypt`, который:
- загрузит SSL сертификаты от Let’s Encrypt
- перезапустит nginx
```sh
sudo ./init-letsencrypt.sh
```

6. Накатите миграции
```sh
docker compose -f docker-compose.prod.yaml exec backend python manage.py migrate
```

7. Запустите команды для наполнения БД тестовыми данными
```sh
python manage.py load_warehouses https://raw.githubusercontent.com/aosothra/remote_content/master/self_storage/warehouses.json
```

```
python manage.py generate_boxes
```

8. Создайте суперпользователя
```
docker compose -f docker-compose.prod.yaml exec backend python manage.py createsuperuser
```

9. Запустите сервер и откройте сайт в браузере по адресу [https://example.com](https://example.com)

---

В дополнение к пользовательской части сайта, также доступны следующие страницы для менеджера:


10. Для работы с сервисом используйте следующие ссылки (замените `example.com` на адрес вашего домена):
- главная [https://example.com](https://example.com)
- панель управления просроченной арендой [https://example.com/overdue](https://example.com/overdue)
- панель управления доставкой [https://example.com/delivery](https://example.com/delivery)

