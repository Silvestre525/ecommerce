FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y netcat-traditional && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean

COPY . .

COPY entrypoint.sh /entrypoint.sh
COPY wait-for-postgres.sh /wait-for-postgres.sh


RUN chmod +x /entrypoint.sh && chmod +x /wait-for-postgres.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
