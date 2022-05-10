FROM python:3.10-slim-bullseye as build-stage

WORKDIR /requestko-project

RUN apt-get update -y && \
    pip3 install --user 'poetry<2.0.0' && \
    /bin/bash -c "ln -fs $HOME/.local/bin/poetry /usr/bin/poetry" && \
    poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

RUN poetry export -f requirements.txt --output ./requirements.txt --without-hashes

RUN ls -all

FROM python:3.10-slim-bullseye as prod-stage

WORKDIR /requestko-project

COPY --from=build-stage /requestko-project/requirements.txt ./
COPY requestko ./requestko
COPY logging.ini ./

RUN apt-get update -y && \
    pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "requestko.app:app", "--host", "0.0.0.0", "--port", "80"]