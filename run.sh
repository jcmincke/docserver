#!/bin/bash

cd ./docserver/docserver

echo "$PWD"

flask --app main run --host=0.0.0.0  --port=8001