# RepairFlow — Requests Service

Микросервис «Заявки» командного проекта RepairFlow — системы обработки заявок
на выездной ремонт.

Дисциплина: «Мікросервісна архітектура та розподілені системи».
Текущий этап — практическая работа №2: подготовка архитектуры и инфраструктуры.
Этот проект содержит минимальное приложение FastAPI с проверкой доступности.
Бизнес-логика будет добавлена в ПЗ3, интеграция с RabbitMQ — в ПЗ4.
Приложение можно запускать локально или вместе с PostgreSQL через Docker Compose.
Это самостоятельная конфигурация для локальной разработки Requests Service;
позже сервис будет интегрирован в общий Docker Compose команды RepairFlow.

## Структура

```text
requests-service/
├── main.py           # Приложение FastAPI и маршрут /health
├── requirements.txt  # Зависимости Python
├── .gitignore        # Исключения для Git
├── Dockerfile        # Сборка образа и запуск приложения
├── .dockerignore     # Исключения для контекста сборки Docker
├── docker-compose.yml # Приложение, PostgreSQL, сеть и том данных
├── .env.example      # Пример переменных окружения без настоящих паролей
├── .env              # Локальные настройки (исключены из Git и Docker-образа)
└── README.md         # Описание и инструкция запуска
```

## Локальный запуск (Windows PowerShell)

Требуется Python 3.10 или новее. Из папки MAD:

```powershell
cd requests-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Команды используют Python виртуального окружения напрямую, поэтому активировать
окружение и менять политику выполнения PowerShell не нужно.

Для Linux/macOS после перехода в папку проекта:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

Приложение доступно по адресу http://127.0.0.1:8000.
Остановить сервер можно сочетанием `Ctrl+C`.

## Запуск через Docker Compose

Требуется работающий Docker Engine (например, через Docker Desktop).
Из папки `requests-service`:

Локальный `.env` уже создан с отдельным случайным тестовым паролем.
На новом компьютере сначала создайте его из шаблона:

```powershell
Copy-Item .env.example .env
```

Замените `POSTGRES_PASSWORD` в `.env` своим тестовым паролем из букв и цифр.
Не копируйте шаблон поверх уже настроенного `.env`.

Переменные окружения:

| Переменная | Назначение |
| --- | --- |
| `POSTGRES_DB` | Имя базы данных Requests Service |
| `POSTGRES_USER` | Пользователь локальной базы |
| `POSTGRES_PASSWORD` | Локальный тестовый пароль |
| `DATABASE_URL` | Строка подключения приложения к PostgreSQL |

В `.env` строка `DATABASE_URL` формируется из остальных переменных благодаря
подстановке Docker Compose. Хост `postgres` — имя сервиса внутри сети Compose,
порт базы — `5432`. Порт PostgreSQL на компьютер не публикуется.
Файл `.env` исключён через `.gitignore` и `.dockerignore`.

Проверьте конфигурацию и запустите оба контейнера:

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

`config --quiet` проверяет конфигурацию без вывода пароля в терминал.
Приложение использует `python:3.13-slim`; база — официальный образ
`postgres:17.6` с закреплённой версией. Healthcheck запускает `pg_isready`;
Compose запускает приложение после перехода базы в состояние `healthy`.
Uvicorn слушает `0.0.0.0:8000` внутри контейнера, на компьютере приложение
доступно по адресу `http://127.0.0.1:8000`.

На этапе ПЗ2 приложение получает `DATABASE_URL`, но ещё не открывает подключение
к базе: драйвер, таблицы и бизнес-логика будут добавлены позднее.

Проверка базы данных:

```powershell
docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Просмотр логов:

```powershell
docker compose logs --tail 50
```

Остановить контейнеры, сохранив их для следующего запуска:

```powershell
docker compose stop
docker compose start
```

Удалить контейнеры и сеть, сохранив данные PostgreSQL:

```powershell
docker compose down
```

Данные хранятся в именованном томе `requests-postgres-data`, который сохраняется
после перезапуска и `docker compose down`. Команда `docker compose down -v`
удаляет этот том вместе с данными; для обычной остановки её не используйте.
Настройки `POSTGRES_*` создают пользователя и базу только при первой
инициализации пустого тома: изменение пароля в `.env` само по себе не меняет
пароль пользователя в уже существующей базе.

## Проверка

Откройте http://127.0.0.1:8000/health в браузере или выполните в другом окне
PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Маршрут `GET /health` возвращает HTTP 200 и JSON:

```json
{"status": "ok"}
```

Это проверка доступности приложения; подключение к базе данных не проверяется.
Интерактивная документация API: http://127.0.0.1:8000/docs.
