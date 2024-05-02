#!/bin/bash
args=("$@")

ansible-playbook -i ./inventory.yml ./server.yml -l development --vault-password-file=./vault_passwords/development --vault-password-file=./vault_passwords/default ${args}