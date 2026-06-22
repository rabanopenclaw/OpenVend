FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system --gid 10001 openvend \
    && adduser --system --uid 10001 --ingroup openvend openvend

WORKDIR /app

COPY services/contacts/pyproject.toml ./pyproject.toml
COPY services/contacts/app ./app
COPY services/contacts/alembic.ini ./alembic.ini
COPY services/contacts/alembic ./alembic

RUN pip install --no-cache-dir .

USER openvend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
