FROM python:3.10.12-bullseye as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.5.1

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock README.md ./
COPY cgroups_exporter ./cgroups_exporter

RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root --no-dev && \
    poetry build

FROM python:3.10.12-slim-bullseye as final

COPY --from=builder /app/dist/*.whl .

RUN pip install *.whl
RUN rm *.whl

CMD ["/usr/local/bin/cgroups-exporter"]

EXPOSE 9753
