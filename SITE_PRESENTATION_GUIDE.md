# Royal Tashkent Hotel - Presentation Guide

## 1. Что это за проект
Royal Tashkent Hotel - это веб-приложение для бронирования номеров отеля с 3 ролями:
- гость (смотрит сайт и номера)
- пользователь (бронирует, переносит и отменяет брони)
- администратор (управляет номерами, пользователями и бронями)

Приложение построено как server-rendered сайт на FastAPI + Jinja2 и хранит данные в SQL БД через SQLAlchemy.

## 2. Технологический стек
- Backend: FastAPI
- Шаблоны: Jinja2
- ORM: SQLAlchemy
- База данных: PostgreSQL (через `DATABASE_URL`)
- Auth: JWT (cookie `access_token`) + bcrypt (passlib)
- Frontend: HTML/CSS/JS (без тяжелого SPA-фреймворка)
- Контейнеризация: Docker + docker-compose

Ключевые файлы:
- `app/main.py` - маршруты и бизнес-логика
- `app/models.py` - модели `User`, `Room`, `Booking`
- `app/auth.py` - хеширование паролей и JWT
- `app/database.py` - подключение к БД
- `app/templates/*.html` - страницы
- `app/static/css/*.css`, `app/static/js/*.js` - стили и скрипты

## 3. Архитектура и как работает
### 3.1 Поток пользователя
1. Пользователь открывает главную `/` и видит номера.
2. Если не авторизован, при бронировании его переводит на `/login`.
3. После входа при бронировании создается запись в `bookings`.
4. В `/dashboard` пользователь:
- видит свои брони
- переносит даты (`/dashboard/booking/reschedule/{id}`)
- отменяет бронь (`/dashboard/booking/cancel/{id}`)

### 3.2 Поток администратора
1. Админ заходит на `/admin`.
2. Может:
- добавлять/редактировать/удалять номера
- удалять брони
- удалять пользователей (кроме главного админа)
- обновлять свои админ-данные

### 3.3 Авторизация
- При логине создается JWT с `sub=email`.
- JWT кладется в `HttpOnly` cookie `access_token`.
- Пользователь определяется в `get_current_user_from_cookie`.
- Проверки прав администратора выполняются на защищенных роутерах.

## 4. Модели данных
### `users`
- `id`
- `full_name`
- `email` (unique)
- `hashed_password`
- `is_active`
- `is_admin`

### `rooms`
- `id`
- `name`
- `description`
- `price_per_night`
- `image_url`

### `bookings`
- `id`
- `user_id -> users.id`
- `room_id -> rooms.id`
- `check_in_date`
- `check_out_date`
- `total_price`
- `created_at`

## 5. Ключевые функции проекта
- Регистрация и вход
- JWT-сессии через cookie
- Бронирование номеров с расчетом стоимости по дням
- Личный кабинет с переносом/отменой брони
- Админ-панель управления контентом и данными
- Мультиязычность (EN / RU / UZ)
- SEO-страница: `/hotel-in-tashkent`
- Адаптивный UI (desktop/mobile)

## 6. Мультиязычность
Локализация централизована в `app/static/js/i18n.js`.
- Все UI-ключи лежат в объекте `I18N`.
- Элементы в шаблонах имеют `data-i18n`.
- Язык хранится в `localStorage`.
- Переключение языка применяется на все основные страницы.

## 7. Работа с изображениями (важно для Vercel/readonly FS)
При загрузке изображений в админке используется Base64 data URL (если размер до лимита), чтобы не зависеть от записи файлов на диск в окружениях с ограниченной файловой системой.

## 8. Основные маршруты
Публичные:
- `GET /`
- `GET /hotel-in-tashkent`
- `GET /login`, `POST /login`
- `GET /register`, `POST /register`
- `GET /logout`

Пользователь:
- `POST /book/{room_id}`
- `GET /dashboard`
- `POST /dashboard/booking/cancel/{booking_id}`
- `POST /dashboard/booking/reschedule/{booking_id}`

Админ:
- `GET /admin`
- `POST /admin/room/add`
- `POST /admin/room/edit/{room_id}`
- `POST /admin/room/delete/{room_id}`
- `POST /admin/booking/delete/{booking_id}`
- `POST /admin/user/delete/{user_id}`
- `POST /admin/settings`

## 9. Безопасность
Что реализовано:
- Пароли хешируются bcrypt
- JWT хранится в `HttpOnly` cookie
- Проверки доступа к личным/админ-роутам

Что можно улучшить:
- CSRF-защита для форм
- Ограничение попыток логина (rate limit)
- `secure=True` и `samesite` для cookie в production
- Более строгая валидация входных данных

## 10. Как запускать
Через Docker:
- `docker-compose up -d --build`

Локально (без Docker):
1. Установить зависимости (`requirements.txt`)
2. Настроить `DATABASE_URL`
3. Запустить FastAPI (uvicorn)

## 11. Что показать на презентации (демо-сценарий)
1. Главная: hero, номера, фильтры, языки.
2. Регистрация нового пользователя.
3. Логин и бронирование номера.
4. Dashboard: перенос и отмена брони.
5. Вход админом и управление номером.
6. Переключение EN/RU/UZ и SEO-страница `/hotel-in-tashkent`.

## 12. Краткий pitch (30-40 секунд)
"Это полнофункциональная система бронирования отеля на FastAPI. Пользователь может зарегистрироваться, войти, забронировать номер и управлять бронями в личном кабинете. Администратор управляет номерами, бронированиями и пользователями через отдельную панель. Проект поддерживает три языка, адаптивный интерфейс и SEO-оптимизированную страницу для продвижения."