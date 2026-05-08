FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p models static templates

EXPOSE 8000

CMD ["python", "mlops_platform.py"]