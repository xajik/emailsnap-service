FROM apache/superset:4.0.2

USER root

RUN pip install mysqlclient sqlalchemy gunicorn

USER superset

ENTRYPOINT /bin/bash -c \
    "superset fab create-admin \
        --username ${SUPERSET_ADMIN_USERNAME} \
        --firstname Superset \
        --lastname Admin \
        --email ${SUPERSET_ADMIN_EMAIL} \
        --password ${SUPERSET_ADMIN_PASSWORD} && \
    superset db upgrade && \
    superset init && \
    superset run -p 8088 --with-threads --reload --debugger --host=0.0.0.0"
