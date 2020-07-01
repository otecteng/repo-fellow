FROM python:3.7-alpine AS fellow_base


RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        libffi-dev \
        mysql-dev \
        python3-dev \
        libxml2-dev \
        libxslt-dev \
        make \
        bash \
    && rm -rf /var/cache/apk/* \
    && mkdir -p /app

ENV INSTALL_PATH /app

WORKDIR $INSTALL_PATH

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


FROM fellow_base

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
COPY . .

ENTRYPOINT [ "/docker-entrypoint.sh" ]