# Используйте официальный образ Python как базовый образ
FROM python:3.11-slim

# Установите рабочую директорию в контейнере
WORKDIR /app

# Скопируйте файл requirements.txt в рабочую директорию
COPY requirements.txt .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте остальной исходный код в рабочую директорию
COPY . .

# Определите переменные окружения для подключения к базе данных
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=132465
ENV DB_HOST=db
ENV DB_PORT=5432

# Укажите команду для запуска приложения
CMD ["python", "main.py"]
