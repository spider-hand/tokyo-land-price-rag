FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .

EXPOSE 8000
CMD [".venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
