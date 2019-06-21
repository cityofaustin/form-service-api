#!/usr/bin/env bash

########################################
# Declare Constants
########################################
set -a # exports all assigned variables

if [ "$CIRCLE_BRANCH" == "production" ]; then
  DEPLOYMENT_MODE="production"
  ZAPPA_STAGE="production"
elif [ "$CIRCLE_BRANCH" == "master" ]; then
  DEPLOYMENT_MODE="staging"
  ZAPPA_STAGE="staging"
else # for PR builds
  CIRCLE_BRANCH="test-branch" # TODO: remove
  DEPLOYMENT_MODE="local" # dev
  ZAPPA_STAGE=$(echo "pr_$CIRCLE_BRANCH" | sed 's/-/_/g') # zappa only allows _ in stage name
fi
