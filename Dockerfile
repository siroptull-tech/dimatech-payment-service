FROM python:3.11-slim

WORKDIR /app

# gcc is needed to compile bcrypt if a pre-built wheel is unavailable
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["sh", "entrypoint.sh"]
