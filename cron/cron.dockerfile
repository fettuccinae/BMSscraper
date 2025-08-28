FROM alpine:latest

RUN apk add --no-cache bash curl

WORKDIR /code

COPY cron_script.sh /code/cron_script.sh
COPY cronjob /etc/cron.d/cronjob

RUN chmod +x /code/cron_script.sh
RUN chmod 0644 /etc/cron.d/cronjob

RUN crontab /etc/cron.d/cronjob

