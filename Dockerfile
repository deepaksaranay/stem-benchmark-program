FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY benchmark benchmark
COPY tasks tasks
COPY data data
COPY reports reports

# Run as a non-root user; only the reports folder needs to be writable
RUN useradd --system --uid 10001 runner && chown -R 10001 /app/reports
USER 10001

ENTRYPOINT ["python", "-m", "benchmark"]
CMD ["validate-tasks"]
