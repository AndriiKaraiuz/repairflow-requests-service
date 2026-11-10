# RepairFlow — Requests Service

Мікросервіс «Заявки» командного проєкту RepairFlow — системи обробки заявок
на виїзний ремонт.

Дисципліна: «Мікросервісна архітектура та розподілені системи».
Поточний етап — практична робота №2: підготовка архітектури та інфраструктури.
Цей проєкт містить мінімальний застосунок FastAPI з перевіркою доступності.
Бізнес-логіку буде додано в ПЗ3, інтеграцію з RabbitMQ — у ПЗ4.
Застосунок можна запускати локально або разом із PostgreSQL через Docker Compose.
Це самостійна конфігурація для локальної розробки Requests Service;
згодом сервіс буде інтегровано в загальний Docker Compose команди RepairFlow.

## Структура

```text
requests-service/
├── main.py           # Застосунок FastAPI та маршрут /health
├── requirements.txt  # Залежності Python
├── .gitignore        # Винятки для Git
├── Dockerfile        # Збирання образу та запуск застосунку
├── .dockerignore     # Винятки для контексту збирання Docker
├── docker-compose.yml # Застосунок, PostgreSQL, мережа та том даних
├── .env.example      # Приклад змінних середовища без справжніх паролів
├── .env              # Локальні налаштування (виключені з Git і Docker-образу)
└── README.md         # Опис та інструкція запуску
```

## Локальний запуск (Windows PowerShell)

Потрібен Python 3.10 або новіший. Із папки MAD:

```powershell
cd requests-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Команди використовують Python віртуального середовища безпосередньо, тому
активувати середовище та змінювати політику виконання PowerShell не потрібно.

Для Linux/macOS після переходу до папки проєкту:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

Застосунок доступний за адресою http://127.0.0.1:8000.
Зупинити сервер можна сполученням клавіш `Ctrl+C`.

## Запуск через Docker Compose

Потрібен запущений Docker Engine (наприклад, через Docker Desktop).
Із папки `requests-service`:

Локальний `.env` уже створено з окремим випадковим тестовим паролем.
На новому комп’ютері спочатку створіть його із шаблону:

```powershell
Copy-Item .env.example .env
```

Замініть `POSTGRES_PASSWORD` у `.env` власним тестовим паролем із літер і цифр.
Не копіюйте шаблон поверх уже налаштованого `.env`.

Змінні середовища:

| Змінна | Призначення |
| --- | --- |
| `POSTGRES_DB` | Назва бази даних Requests Service |
| `POSTGRES_USER` | Користувач локальної бази |
| `POSTGRES_PASSWORD` | Локальний тестовий пароль |
| `DATABASE_URL` | Рядок підключення застосунку до PostgreSQL |

У `.env` рядок `DATABASE_URL` формується з решти змінних завдяки
підстановці Docker Compose. Хост `postgres` — назва сервісу всередині мережі Compose,
порт бази — `5432`. Порт PostgreSQL не публікується на комп’ютері.
Файл `.env` виключено через `.gitignore` і `.dockerignore`.

Перевірте конфігурацію та запустіть обидва контейнери:

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

`config --quiet` перевіряє конфігурацію без виведення пароля в термінал.
Застосунок використовує `python:3.13-slim`; база — офіційний образ
`postgres:17.6` із зафіксованою версією. Healthcheck запускає `pg_isready`;
Compose запускає застосунок після переходу бази до стану `healthy`.
Uvicorn прослуховує `0.0.0.0:8000` всередині контейнера, на комп’ютері застосунок
доступний за адресою `http://127.0.0.1:8000`.

На етапі ПЗ2 застосунок отримує `DATABASE_URL`, але ще не відкриває підключення
до бази: драйвер, таблиці та бізнес-логіку буде додано пізніше.

Перевірка бази даних:

```powershell
docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Перегляд журналів:

```powershell
docker compose logs --tail 50
```

Зупинити контейнери, зберігши їх для наступного запуску:

```powershell
docker compose stop
docker compose start
```

Видалити контейнери та мережу, зберігши дані PostgreSQL:

```powershell
docker compose down
```

Дані зберігаються в іменованому томі `requests-postgres-data`, який зберігається
після перезапуску та `docker compose down`. Команда `docker compose down -v`
видаляє цей том разом із даними; для звичайної зупинки її не використовуйте.
Налаштування `POSTGRES_*` створюють користувача та базу лише під час першої
ініціалізації порожнього тому: зміна пароля в `.env` сама собою не змінює
пароль користувача у вже наявній базі.

## Перевірка

Відкрийте http://127.0.0.1:8000/health у браузері або виконайте в іншому вікні
PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Маршрут `GET /health` повертає HTTP 200 і JSON:

```json
{"status": "ok"}
```

Це перевірка доступності застосунку; підключення до бази даних не перевіряється.
Інтерактивна документація API: http://127.0.0.1:8000/docs.
