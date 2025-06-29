# Берем за основу slim версию питона 3.12
FROM python:3.13-slim AS build

# Устанавливаем рабочую папку, название может быть любое
WORKDIR /app

# Устанавлием poetry
RUN pip install poetry

# Копируем poetry.toml и poetry.lock в контейнер
COPY pyproject.toml poetry.lock ./

# Настроим poetry чтобы не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --no-interaction --no-root

# Копируем весь проект в контейнер
COPY . .

# Команда для запуска бота
CMD ["python", "-m", "main"]