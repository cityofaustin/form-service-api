#!/usr/bin/env bash
set -e
CD=`dirname $BASH_SOURCE`
source $CD/helpers.sh

function print_var {
  echo "$1: [${!1}]"
}

echo "########"
echo "Here's what's stored in CircleCI:"
echo "########"
echo "::Common::"
print_var "AWS_DEFAULT_REGION"
print_var "S3_UPLOADS_BUCKET_PROD"
print_var "S3_UPLOADS_BUCKET_STAGING"
print_var "EMAIL_SMOKE_TEST_PROD"
print_var "EMAIL_SMOKE_TEST_STAGING"
echo "::OPO::"
print_var "EMAIL_OPO_PROD"
print_var "EMAIL_OPO_STAGING"
print_var "EMAIL_APD_PROD"
print_var "EMAIL_APD_STAGING"
print_var "EMAIL_REPLYTO_PROD"
print_var "EMAIL_REPLYTO_STAGING"
echo ""
echo ""
echo "########"
echo "Here's what your app is actually using:"
echo "########"
python3 $CD/print_app_vars.py
