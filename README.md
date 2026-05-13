# Proxy Service

Сервис для получения прокси-доступа с регистрацией, активацией по email и десктоп-клиентом.

## Стек технологий

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis, JWT
- **Frontend:** Vue 3, Vuetify 3, Pinia, Vite
- **Desktop:** Tauri + Vue
- **Контейнеризация:** Docker, Docker Compose
- **Email:** Resend SMTP
- **Тесты:** pytest + pytest-asyncio

## Требования

- Docker и Docker Compose
- Node.js (v18+)
- Rust (только для сборки десктоп-приложения)

## Быстрый запуск

### 1. Склонируйте репозиторий

```
git clone https://github.com/MomaPu/Proxy-Service.git
cd proxy-service
```
## 2. Настройте переменные окружения
Создайте файл backend/.env:
```
DATABASE_URL=postgresql+asyncpg://proxy_user:proxy_pass@postgres/proxy_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=сгенерируйте_случайную_строку
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Resend SMTP (для отправки писем)
MAIL_USERNAME=resend
MAIL_PASSWORD=re_ваш_api_ключ
MAIL_FROM=onboarding@resend.dev
SMTP_SERVER=smtp.resend.com
SMTP_PORT=587
```
## 3. Запустите бэкенд

``` 
docker-compose up -d
```
## 4. Создайте тестовые прокси-серверы
```
docker-compose exec backend python init_db.py
```
## 5. Запустите фронтенд
```
cd frontend
npm install
npm run dev
```
## 6. Запустите десктоп-приложение
```
cd desktop-app
npm install
npm run tauri dev
```
## Как пользоваться
### Регистрация
Откройте http://localhost:3000/register
Введите email и пароль
На указанную почту придёт ключ активации
(P.S Если Resend в Demo версии, то ключ придет на ту почту, 
которая была указана в профиле)
### Активация ключа
#### 1 Вариант
Через Swagger UI: http://localhost:8000/docs
Выполните POST /api/v1/activate/key с телом:
```
{
  "activation_key": "ключ_из_письма"
}
```
#### 2 Вариант
Работа с десктоп-приложением
Вставьте ключ активации в поле Activation Key
Нажмите Connect
Приложение покажет данные прокси и статус подключения
Для отключения нажмите Disconnect

## Вход в личный кабинет
Перейдите на http://localhost:3000/login

Введите email и пароль

После успешного входа увидите:

- Данные вашего прокси (хост, порт, протокол) 

- Кнопку «Обновить ключ»

- Возможность сменить пароль

## API эндпоинты
Полная документация: http://localhost:8000/docs

## Структура проекта
![img.png](readme_img/img.png)

## Логика работы
- Пользователь регистрируется → бэкенд генерирует уникальный ключ

- Celery отправляет письмо с ключом на почту

- Пользователь активирует ключ 

- Система находит свободную виртуальную машину и привязывает к пользователю

- В личном кабинете отображаются данные прокси

- Десктоп-приложение использует этот же ключ для подключения

## Запуск тестов
```
cd backend
pytest -v
```

## Устранение неполадок
### Ошибка «port is already allocated»
Измените порты в docker-compose.yml:
```
postgres:
  ports:
    - "5433:5432"  # вместо 5432:5432
```
### Письма не приходят
- Проверьте логи: docker-compose logs celery_worker

- Убедитесь, что SMTP настройки в .env правильные

- Проверьте папку «Спам»

- Если используете Resend Demo, убедитесь, что почта указана в профиле

## Десктоп-приложение не собирается

Установите Rust: https://rustup.rs/

## Скриншоты
### Регистрация
![img_1.png](readme_img/img_1.png)

### Авторизация
![img_2.png](readme_img/img_2.png)

### Активация ключа (Десктоп-приложение)
![img_3.png](readme_img/img_3.png)

### Личный кабинет

![img_4.png](readme_img/img_4.png)

### Письмо с ключом

![img_5.png](readme_img/img_5.png)

# Контакты
Telegram: @MomaPu

Email: matvey.seymachin@mail.ru

