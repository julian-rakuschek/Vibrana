# ------------------------------
#     Frontend Build
# ------------------------------
FROM node:20-alpine as build
WORKDIR /app
COPY ./web/frontend/package*.json ./
RUN npm i --silent --force
COPY ./web/frontend .
RUN npm run build


# -------------------------------------------
#     Backend Build
# src: https://stackoverflow.com/a/57886655
# -------------------------------------------
FROM python:3.12-bookworm

RUN apt-get update && apt-get install --no-install-suggests --no-install-recommends --yes pipx

ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="${PYTHONPATH}:/app"
WORKDIR /app

RUN pipx install poetry
RUN pipx inject poetry poetry-plugin-bundle

COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml
RUN poetry install --no-dev
RUN poetry add gunicorn

COPY ./parser ./parser
COPY ./web ./web
COPY ./algorithms ./algorithms
COPY --from=build /app ./web/frontend

EXPOSE 5000
CMD ["poetry", "run", "gunicorn", "--timeout", "10000", "-w", "4", "-b", "0.0.0.0:5000", "web.backend.main:app"]
