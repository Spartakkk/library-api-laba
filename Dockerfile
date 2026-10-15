# Образ приложения (backend)

# 1. Берём готовый образ с Python
FROM python:3.13

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Устанавливаем зависимости. requirements.txt копируем отдельно,
#    чтобы Docker кэшировал этот шаг, пока список библиотек не изменится
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Копируем исходный код (кроме файлов из .dockerignore)
COPY . /app

# 5. Приложение слушает порт 8000
EXPOSE 8000

# 6. При запуске контейнера: применяем миграции, затем запускаем сервер
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
