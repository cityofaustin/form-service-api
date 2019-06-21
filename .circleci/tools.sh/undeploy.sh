#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`

# Creates a basic zappa_settings.json that is used just to delete your build

stage=$1
project_name="coa-forms-api"

if [ "$stage" == "production" ] || [ "$stage" == "master" ]; then
  echo "Failsafe: don't delete that stack"; exit 1
fi

jq -n "{\"$stage\": {\"project_name\": \"$project_name\"}}" > $CD/../../zappa_settings.json
zappa undeploy $stage
