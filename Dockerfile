FROM python:3.14.4-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY server/ ./server/
COPY ui/ ./ui/
COPY jinja-templates/ ./jinja-templates/
COPY schema/ ./schema/
COPY commands/ ./commands/
COPY midtempo-framework/ ./midtempo-framework/
COPY pyproject.toml .

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
