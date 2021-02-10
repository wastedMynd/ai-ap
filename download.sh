#!/bin/bash

echo "starting ai-ap application"

# shellcheck disable=SC2164
pushd ~/PycharmProjects/ai-ap/

./venv/bin/python ./index.py

# shellcheck disable=SC2164
popd
