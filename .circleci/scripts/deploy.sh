#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`
source $CD/helpers.sh

# Dynamically construct the zappa settings for our app
python3 $CD/build_zappa_settings.py

set +e
# Check if lambda function already exists.
# set +e temporarily allows us to throw errors.
# If `get-function` returns a 255 error, then we know that our lambda does not exist and needs to be deployed.
ZAPPA_FUNCTION=$(echo "coa-forms-api-$ZAPPA_STAGE" | sed 's/_/-/g')
$(aws lambda get-function --function-name $ZAPPA_FUNCTION > /dev/null)
result=$?
set -e
if [ "$result" == 0 ]; then
  if [ "$DEPLOYMENT_MODE" == "dev" ] && [ -z "$CIRCLE_PR_NUMBER" ]; then
    echo "Skipping Deploy Step. Only deploying PRs for dev branches."
    exit 0
  fi
  # Update zappa lambda if it exists
  zappa update $ZAPPA_STAGE
else
  # Deploy new lambda function if it doesn't exist
  zappa deploy $ZAPPA_STAGE
fi
