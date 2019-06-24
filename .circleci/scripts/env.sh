#!/usr/bin/env bash

########################################
# Declare Constants
########################################
set -a # exports all assigned variables

if [ "$CIRCLE_BRANCH" == "production" ]; then
  # Common
  DEPLOYMENT_MODE="production"
  ZAPPA_STAGE="production"
  DYNAMO_DB_TABLE="coa-forms-prod"
  S3_UPLOADS_BUCKET="$S3_UPLOADS_BUCKET_PROD"
  EMAIL_SMOKE_TEST="$EMAIL_SMOKE_TEST_PROD"
  # OPO
  EMAIL_OPO="$EMAIL_OPO_PROD"
  EMAIL_APD="$EMAIL_APD_PROD"
  EMAIL_OPO_REPLYTO="$EMAIL_REPLYTO_PROD"
elif [ "$CIRCLE_BRANCH" == "master" ]; then
  # Common
  DEPLOYMENT_MODE="staging"
  ZAPPA_STAGE="staging"
  DYNAMO_DB_TABLE="coa-forms-dev"
  S3_UPLOADS_BUCKET="$S3_UPLOADS_BUCKET_STAGING"
  EMAIL_SMOKE_TEST="$EMAIL_SMOKE_TEST_STAGING"
  # OPO
  EMAIL_OPO="$EMAIL_OPO_STAGING"
  EMAIL_APD="$EMAIL_APD_STAGING"
  EMAIL_OPO_REPLYTO="$EMAIL_REPLYTO_STAGING"
else # for PR builds
  # Common
  DEPLOYMENT_MODE="dev"
  ZAPPA_STAGE=$(echo "pr_$CIRCLE_BRANCH" | sed 's/-/_/g') # zappa only allows _ in stage name
  DYNAMO_DB_TABLE="coa-forms-dev"
  S3_UPLOADS_BUCKET="coa-forms-uploads-pr"
  EMAIL_SMOKE_TEST="$EMAIL_SMOKE_TEST_STAGING"
  # OPO
  EMAIL_OPO="$EMAIL_OPO_STAGING"
  EMAIL_APD="$EMAIL_APD_STAGING"
  EMAIL_OPO_REPLYTO="$EMAIL_REPLYTO_STAGING"
fi

DEFALUT_REGION=${AWS_DEFAULT_REGION:-"us-east-1"}
