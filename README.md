# Библиотека API

Лабораторные работы №1 и №2: серверное приложение на FastAPI с PostgreSQL,
запускаемое в Docker.

Приложение ведёт учёт **книг** и **читателей** и позволяет **выдавать книги** читателям и принимать их обратно.

**Стек:** Python, FastAPI (REST API), SQLAlchemy (ORM), Alembic (миграции),
Pydantic (валидация), PostgreSQL (БД), pytest (тесты), Docker + Docker Compose.

## Сущности

```
Book 1 ──< Loan >── 1 Reader
```

| Таблица | Что хранит | Поля |
|---|---|---|
| `books` | книги | название, автор, год, всего экземпляров, свободно экземпляров |
| `readers` | читатели | имя, email (уникальный), телефон |
| `loans` | выдачи книг | книга, читатель, дата выдачи, срок возврата, дата возврата |

## Бизнес-правила

Находятся в файле [app/rules.py](app/rules.py). При нарушении API возвращает код **409**.

1. Книгу можно выдать, только если есть свободный экземпляр.
2. У читателя на руках может быть не больше `MAX_ACTIVE_LOANS` книг (по умолчанию 3).
3. Уже возвращённую книгу нельзя вернуть повторно.
4. Нельзя удалить книгу или читателя, пока есть невозвращённые книги.

## API (14 эндпоинтов)

| Метод | Адрес | Что делает |
|---|---|---|
| GET | `/books` | список книг |
| GET | `/books/{id}` | одна книга |
| POST | `/books` | добавить книгу |
| PATCH | `/books/{id}` | изменить книгу |
| DELETE | `/books/{id}` | удалить книгу |
| GET | `/readers` | список читателей |
| GET | `/readers/{id}` | один читатель |
| POST | `/readers` | добавить читателя |
| PATCH | `/readers/{id}` | изменить читателя |
| DELETE | `/readers/{id}` | удалить читателя |
| GET | `/loans` | список выдач (фильтры `?reader_id=1`, `?active=true`) |
| GET | `/loans/{id}` | одна выдача |
| POST | `/loans` | выдать книгу |
| POST | `/loans/{id}/return` | вернуть книгу |

Итого: 6 GET, 4 POST, 2 PATCH, 2 DELETE.

**Коды ошибок:** 404 — объект не найден, 409 — нарушено бизнес-правило или email уже занят,
422 — неверные входные данные.

## Структура проекта

```
app/
  main.py           точка входа: создаёт приложение и подключает эндпоинты
  config.py         настройки из переменных окружения
  database.py       подключение к БД
  models.py         ORM-модели (таблицы)
  schemas.py        Pydantic-схемы (валидация запросов и формат ответов)
  rules.py          бизнес-правила
  routers/
    books.py        эндпоинты /books
    readers.py      эндпоинты /readers
    loans.py        эндпоинты /loans
alembic/
  env.py            подключение Alembic к БД
  versions/
    0001_create_tables.py     создание таблиц
    0002_add_reader_phone.py  добавление колонки phone (пример изменения схемы)
tests/
  conftest.py           подготовка тестовой БД
  test_unit.py          9 unit-тестов
  test_integration.py   6 integration-тестов
Dockerfile          сборка образа приложения
.dockerignore       что не копировать в образ
compose.yaml        сервисы backend и db, сеть и volume
.env                настройки (переменные окружения)
.env.example        пример настроек
requirements.txt    зависимости Python
```

## Docker

`compose.yaml` описывает:

- сервис **`db`**: PostgreSQL 16, данные хранятся в именованном volume `pgdata`;
- сервис **`backend`**: приложение, собирается из `Dockerfile`, порт 8000;
- сеть **`library-network`**: общая для обоих сервисов, `backend` обращается к БД по имени `db`;
- volume **`pgdata`**: данные БД сохраняются после `docker compose down`.

Настройки передаются через переменные окружения из файла `.env`. При старте `backend` сам
применяет миграции (`alembic upgrade head`) и только после этого запускает сервер.
`backend` стартует только когда `db` готова (healthcheck).

## Команды

### Сборка и запуск

```bash
docker compose up --build
```

Если файла `.env` нет, сначала создайте его из примера: `cp .env.example .env`.

После запуска:
- http://localhost:8000/docs — Swagger, в нём можно вызвать любой эндпоинт;
- http://localhost:8000/books — список книг.

Чтобы запустить в фоне, добавьте `-d`: `docker compose up --build -d`.

### Остановка

```bash
docker compose down        # остановить и удалить контейнеры, данные в volume СОХРАНЯЮТСЯ
docker compose down -v     # то же + удалить volume с данными (БД станет пустой)
```

### Просмотр

```bash
docker compose ps                  # какие контейнеры запущены
docker compose logs backend        # логи приложения (видно применение миграций)
docker volume ls                   # список volume
docker network ls                  # список сетей
```

## Проверка

### 1. Запуск с пустой БД

```bash
docker compose down -v             # удаляем старые данные
docker compose up --build -d
docker compose logs backend
```

В логах видно, что миграции создали таблицы в пустой БД:

```
Running upgrade  -> 0001, Создание таблиц books, readers, loans
Running upgrade 0001 -> 0002, Добавление телефона читателю
Uvicorn running on http://0.0.0.0:8000
```

### 2. CRUD

Откройте http://localhost:8000/docs и выполните по порядку («Try it out» → «Execute»):

1. `POST /books` с телом `{"title": "Мастер и Маргарита", "author": "Михаил Булгаков", "total_copies": 1}` — ответ 201.
2. `POST /readers` с телом `{"name": "Анна Смирнова", "email": "anna@mail.ru"}` — 201.
3. `POST /readers` с телом `{"name": "Пётр Иванов", "email": "petr@mail.ru"}` — 201.
4. `GET /books` — книга в списке.
5. `PATCH /books/1` с телом `{"year": 1966}` — 200, год изменился.
6. `POST /loans` с телом `{"book_id": 1, "reader_id": 1}` — 201, книга выдана.
7. `POST /loans` с телом `{"book_id": 1, "reader_id": 2}` — **409**, нет свободных экземпляров.
8. `DELETE /readers/1` — **409**, у читателя есть книга.
9. `DELETE /readers/2` — 204, удалён.

### 3. Тесты

```bash
docker compose exec backend pytest -v
```

Тесты создают для себя отдельную временную базу и не трогают данные в PostgreSQL.

### 4. Сохранность данных после перезапуска (volume НЕ удаляем)

```bash
docker compose down                # без -v!
docker compose up -d
```

Откройте http://localhost:8000/books: записи на месте. То же можно проверить прямо в БД:

```bash
docker compose exec db psql -U library -d library -c "SELECT * FROM books;"
```

## Миграции

Таблицы создаются и изменяются только миграциями Alembic (папка `alembic/versions`).
В Docker они применяются автоматически при старте `backend`. Вручную:

```bash
docker compose exec backend alembic current     # какая миграция применена
docker compose exec backend alembic history     # список миграций
docker compose exec backend alembic downgrade -1  # откатить последнюю
docker compose exec backend alembic upgrade head  # применить все
```

## Запуск без Docker

Нужны установленные **Python 3.12+** и **PostgreSQL**.

### 1. Создать базу данных (один раз)

Откройте pgAdmin или `psql` под пользователем `postgres` и выполните:

```sql
CREATE USER library WITH PASSWORD 'library';
CREATE DATABASE library OWNER library;
```

### 2. Установить зависимости (один раз)

```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
# source .venv/bin/activate        # Linux / macOS
pip install -r requirements.txt
```

### 3. Применить миграции

```bash
alembic upgrade head
```

### 4. Запустить сервер

```bash
uvicorn app.main:app --reload
```

Документация API: http://localhost:8000/docs. Остановить сервер: `Ctrl+C`.

### 5. Тесты

```bash
pytest -v
```

Для тестов PostgreSQL не нужен: каждый тест создаёт временную SQLite-базу.

### Важно

- **Файл `.env` при таком запуске не используется.** Его читает только Docker Compose.
  Приложение берёт настройки по умолчанию из `app/config.py`: база `library` на
  `localhost:5432`, пользователь `library`, пароль `library`. Поэтому на шаге 1
  создаётся именно такой пользователь.
- Чтобы подключиться к другой базе, задайте переменную окружения перед запуском:
  ```powershell
  $env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@localhost:5432/DBNAME"
  ```
- **Порт 8000 должен быть свободен.** Если запущен Docker-вариант, сначала выполните
  `docker compose down` или запустите сервер на другом порту: `uvicorn app.main:app --port 8001`.
