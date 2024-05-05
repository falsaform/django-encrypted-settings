set positional-arguments := true

_default:
    @just --list --unsorted

poetry *args:
    docker compose exec development poetry {{ args }}

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

# hello world
bash *args:
    docker compose exec development bash {{args}}

test *args:
    #!/bin/bash
    docker compose run --entrypoint "poetry run pytest {{args}}" development

test-ansible *args:
    #!/bin/bash
    docker compose run development 'bash -c "cd src/tests/ansible && ./test.sh {{ args }}"'

black *args:
    just poetry run black .

encrypt *args:
    just bash eyaml encrypt {{ args }}

decrypt *args:
    just bash eyaml decrypt {{ args }}

dump *args:
    just bash eyaml dump {{ args }}
