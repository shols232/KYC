FROM python:3.10.0
LABEL maintainer="Akinsola Ademola <akinsolaademolatemitope@gmail.com>"

# Update packages
RUN apt-get update

ARG POETRY_INSTALL_OPTIONS="--no-dev"
ARG DJANGO_SETTINGS_MODULE="core.settings"
ARG GROUP_ID="1000"
ARG USER_ID="1000"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
ENV PATH="/home/user/.local/bin:${PATH}"

# Create a non root user and group so that we don't run the container as root
RUN addgroup --gid $GROUP_ID user && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

# Copy files into container giving user ownership on them (so that we can run collect static).
COPY --chown=user:user . /django

WORKDIR /django
USER user

# Install requirements
RUN pip install poetry && poetry config experimental.new-installer false && poetry install $POETRY_INSTALL_OPTIONS

# Run collectstatic
WORKDIR /django/src
RUN poetry run python manage.py collectstatic --noinput
WORKDIR /django

# Make root the owner of /django, and give users read/execute permissions over it (but not write), and all permissions
# over the logs folder.
USER root
RUN chown -R root:root /django && chmod 755 -R /django

# Set "user" as the system user again
USER user