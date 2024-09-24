FROM python:3.11.10-alpine3.19

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    pkgconfig \
    mariadb-connector-c-dev \
    mysql-client \
    poppler-utils \
    curl \
    unzip

RUN apk add --no-cache \
    fontconfig \
    ttf-dejavu \
    ttf-freefont \
    ttf-liberation \
    ghostscript-fonts
    
RUN mkdir -p /usr/share/fonts/google/Roboto /usr/share/fonts/google/Noto \
    && curl -L -o /usr/share/fonts/google/Roboto/Roboto-Regular.ttf https://github.com/google/fonts/raw/main/apache/roboto/Roboto%5Bwdth,wght%5D.ttf \
    && curl -L -o /usr/share/fonts/google/Noto/NotoSans-Regular.ttf https://noto-website-2.storage.googleapis.com/pkgs/NotoSans-unhinted.zip \
    && fc-cache -f -v

RUN fc-cache -f -v

RUN pip install poetry gunicorn && poetry install --no-dev

EXPOSE 80

COPY scripts scripts

CMD ["poetry", "run", "gunicorn", "app.main:app", "-c", "scripts/gunicorn_conf.py", "--reload"]
