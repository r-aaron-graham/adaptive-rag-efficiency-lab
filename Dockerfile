FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY benchmark.py dataset-v1.json ./
USER 10001:10001
CMD ["python", "benchmark.py"]
