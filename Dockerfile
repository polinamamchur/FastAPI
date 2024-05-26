# Вкажіть базовий образ
FROM python:3.9-slim

# Встановіть робочу директорію
WORKDIR /app

# Скопіюйте файл requirements.txt та встановіть залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопіюйте весь проект в контейнер
COPY . .

# Вкажіть команду для запуску додатка
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
