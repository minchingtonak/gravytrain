#!/usr/bin/env bash

if ! docker network ls | grep 'caddy'; then
    docker network create caddy
    echo 'Created docker network 'caddy' :)'
fi

terraform apply # -auto-approve

echo 'Deployed infra :)'
