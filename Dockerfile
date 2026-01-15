# Используем легкий образ Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . .

# Создаем папку для логов (чтобы она точно была внутри)
RUN mkdir -p data

# Запускаем скрипт
CMD ["python", "-u", "main.py"]