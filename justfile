set positional-arguments := true

_default:
    @just --list --unsorted

poetry *args:
    docker compose exec dev poetry {{ args }}

build *args:
    docker compose build {{args}}

build-package:
    #!/usr/bin/env bash
    docker compose run publish-package bash -c "pip install poetry && poetry build"

publish-package:
    #!/usr/bin/env bash
    docker compose run publish-package bash -c "pip install poetry && poetry build && poetry publish"

up *args:
    docker compose up {{args}}

bash *args:
    docker compose exec dev bash {{args}}

test *args:
    just poetry run pytest {{args}} dev

black *args:
    just poetry run black .
