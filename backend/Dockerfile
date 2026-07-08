FROM python:3.13-alpine
RUN apk add --no-cache uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

COPY . /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    apk add --no-cache --virtual .build-deps \
    && uv sync --no-dev --locked --no-install-project \
    && apk del .build-deps

RUN mkdir -p logs

EXPOSE 8000
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
