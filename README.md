# Flashko — Backend API

Django REST Framework бэкенд для сервиса флеш-карточек Flashko.

## Стек технологий
- **Python:** 3.11+
- **Фреймворк:** Django 5 & Django REST Framework
- **База данных:** PostgreSQL / SQLite (автоматический fallback для PythonAnywhere)
- **Аутентификация:** SimpleJWT (Access Token 15 мин, Refresh Token 7 дней в HttpOnly cookie + fallback в теле запроса)
- **CORS:** `CORS_ALLOW_ALL_ORIGINS = True` (разрешен доступ для любых фронтендов, включая Vercel и localhost)

## Локальный запуск

1. Создать и активировать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# или .venv\Scripts\activate на Windows
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Выполнить миграции:
```bash
python manage.py migrate
```

4. Запустить локальный сервер:
```bash
python manage.py runserver 8000
```

## Тестирование
```bash
python manage.py test
```

## Деплой на PythonAnywhere

1. Склонируйте репозиторий в консоли Bash на PythonAnywhere:
```bash
git clone https://github.com/ibrodevs/Flashko-backend.git
```
2. Создайте виртуальное окружение и установите зависимости.
3. В настройках вкладки **Web** укажите путь к виртуальному окружению и настройте WSGI-файл по образцу `pythonanywhere_wsgi.py`.
4. Соберите статику:
```bash
python manage.py collectstatic --noinput
```
5. Перезагрузите веб-приложение кнопкой **Reload**.
