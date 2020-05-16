#!/bin/bash
set -e

for TEMPLATE in scorpio/config.py.deploy \
  appspec.yml.deploy
  deploy_scripts/*.deploy
do
  envsubst < "$TEMPLATE" > echo "$TEMPLATE" | sed -e 's/\(\.deploy\)*$//g'
  rm $TEMPLATE
done
