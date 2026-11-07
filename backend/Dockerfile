FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
# Apply migrations, optionally load demo data (SEED_DEMO_DATA=true), then serve.
CMD ["sh", "-c", "python -m alembic upgrade head && if [ \"$SEED_DEMO_DATA\" = \"true\" ]; then python -m app.seed; fi && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
