set positional-arguments := true

_default:
    @just --list --unsorted

build +args:
    docker compose build {{args}}

up +args:
    docker compose up {{args}}

bash:
    docker compose exec dev bash

test:
    #!/bin/bash
    docker compose run --entrypoint "poetry run pytest" dev
