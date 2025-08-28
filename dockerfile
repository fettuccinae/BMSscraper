FROM python:3.11-slim

# dependencies babe
RUN apt-get update \
    && apt-get install -y \
        git libnss3 libnspr4 \
        libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 \
        libxkbcommon0 libxcomposite1 libxrandr2 libgbm1 libxdamage1 \
        libpango-1.0-0 libcairo2 \
        libasound2t64 chromium\
        && rm -rf /var/lib/apt/lists/*

# dir and pip
WORKDIR /code/webapp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# real shit
COPY . /code/webapp/

CMD gunicorn -w 1 --threads 4 --bind 0.0.0.0:8080 --log-level debug "webserver:create_app()"
