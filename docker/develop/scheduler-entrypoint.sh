#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

cd src

# Wait for RabbitMQ to be available
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' rabbitmq:15672)" != "200" ]]; do sleep 5; done

poetry run celery -A core beat -s /home/user/celerybeat-schedule -l debug
