FROM python:3.10-slim-bullseye

ENV PYTHONBUFFERED=1  \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.2.2

RUN pip3 install "poetry==${POETRY_VERSION}"


WORKDIR /code

COPY pyproject.toml /code/

RUN poetry config virtualenvs.create false 
RUN poetry install --no-dev --no-interaction --no-ansi


COPY ./src /code/src

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80" ]








