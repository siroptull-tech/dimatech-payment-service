# Payment API

Асинхронное REST API на Python для работы с пользователями, счетами и платежами.

Стек: **Python 3.11**, **Sanic**, **SQLAlchemy 2.0 (asyncio)**, **PostgreSQL 15**, **Alembic**, **Docker Compose**

---

## Быстрый старт

```bash
docker compose up --build
```

Приложение поднимется на `http://localhost:8000`. Миграции и начальные данные применяются автоматически.

Остановить:
```bash
docker compose down
```

Остановить и удалить данные БД:
```bash
docker compose down -v
```

---

## Тестовые аккаунты

Создаются миграцией при первом запуске:

| Роль | Email | Пароль |
|---|---|---|
| Пользователь | user@example.com | user123 |
| Администратор | admin@example.com | admin123 |

---

## Запуск без Docker

**Требования:** Python 3.11+, PostgreSQL 14+

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Откройте .env и укажите свой DATABASE_URL

alembic upgrade head
sanic app.main:app --host 0.0.0.0 --port 8000 --single-process
```

Пример `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/payment_db
SECRET_KEY=gfdmhghif38yrf9ew0jkf32
JWT_SECRET=change-me-to-a-strong-random-secret-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600
```

---

## API

Все эндпоинты кроме `/health` и `/auth/login` требуют заголовок:
```
Authorization: Bearer <access_token>
```

### Аутентификация

**POST /auth/login**

```json
{ "email": "user@example.com", "password": "user123" }
```

Ответ:
```json
{ "access_token": "...", "token_type": "bearer" }
```

---

### Пользователь

| Метод | Путь | Описание |
|---|---|---|
| GET | /health | Проверка доступности сервиса |
| GET | /user/me | Данные текущего пользователя |
| GET | /user/accounts | Список счетов с балансами |
| GET | /user/payments | История платежей |

---

### Администратор

| Метод | Путь | Описание |
|---|---|---|
| GET | /admin/me | Данные текущего администратора |
| GET | /admin/users | Все пользователи со счетами |
| POST | /admin/users | Создать пользователя |
| PUT | /admin/users/`<id>` | Обновить пользователя |
| DELETE | /admin/users/`<id>` | Удалить пользователя |

**POST /admin/users** — тело запроса:
```json
{ "email": "new@example.com", "password": "pass123", "full_name": "Иван Иванов" }
```

**PUT /admin/users/\<id\>** — все поля опциональны:
```json
{ "email": "new@example.com", "full_name": "Новое Имя", "password": "newpass" }
```

---

### Вебхук платёжной системы

**POST /webhook/payment**

Принимает входящие транзакции от платёжной системы, проверяет подпись, при необходимости создаёт счёт, зачисляет средства.

```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

**Как формируется подпись:**

Берём значения полей `account_id`, `amount`, `transaction_id`, `user_id` в алфавитном порядке ключей, конкатенируем их строковые представления и добавляем `SECRET_KEY`. Считаем SHA256.

```python
import hashlib

data = {
    "account_id": 1,
    "amount": 100,
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
}
SECRET_KEY = "gfdmhghif38yrf9ew0jkf32"

keys = sorted(["account_id", "amount", "transaction_id", "user_id"])
raw = "".join(str(data[k]) for k in keys) + SECRET_KEY
signature = hashlib.sha256(raw.encode()).hexdigest()
```

Повторная отправка той же `transaction_id` возвращает `200 OK` без дублирования — идемпотентность гарантирована.

---

## Структура проекта

```
task_test/
├── app/
│   ├── blueprints/      # auth, user, admin, webhook
│   ├── middleware/      # @require_auth, @require_admin
│   ├── models/          # User, Account, Payment
│   ├── utils/           # JWT, bcrypt, подпись вебхука
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   └── main.py
├── migrations/
│   └── versions/
│       └── 0001_initial_schema_and_seed.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
└── .env.example
```
