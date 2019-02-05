#!/usr/bin/env bash

#
# Colors
#

    RED='\033[0;31m'
    NC='\033[0m' # No Color


#
# Prints error message and stops deployment by returing exit 1
# $1 (string) - Error message to display
# Example: helper_halt_deployment "File not found"
#

function helper_halt_deployment {
    echo -e "\n\n--------------------------------------------------------------"
    echo -e "${RED}FATAL ERROR:${NC}"
    echo -e "${1}"
    echo -e "--------------------------------------------------------------\n\n"
    travis_terminate 1;
}

#
# Simply builds a noticeable header when parsing logs.
# This should help determine when our commands begin execution,
# and what branch is being affected by current deployment.
#

function print_header {
    echo ""
    echo ""
    echo "--------------------------------------------------------------"
    echo "   $1"
    echo "--------------------------------------------------------------"
    echo "  TRAVIS_BRANCH:              ${TRAVIS_BRANCH}"
    echo "  TRAVIS_PULL_REQUEST:        ${TRAVIS_PULL_REQUEST}"
    echo "  TRAVIS_PULL_REQUEST_BRANCH: ${TRAVIS_PULL_REQUEST_BRANCH}"
    echo ""
}

#
# Identify 'Production' or 'Staging' branches
#

DEPLOYMENT_MODE="not-available"

#
# We need the branch
#

if [ "${TRAVIS_BRANCH}" == "" ]; then
  helper_halt_deployment "Branch name not defined in variable TRAVIS_BRANCH."
fi;


#
# We need AWS permissions
#

if [ "${AWS_ACCESS_KEY_ID}" == "" ] || [ "${AWS_DEFAULT_REGION}" == "" ] || [ "${AWS_SECRET_ACCESS_KEY}" == "" ]; then
  helper_halt_deployment "Halting deployment, please check your AWS API keys."
fi;


#
# We will need to determine the deployment mode (environment, ie. production or staging)
#

if [ "${TRAVIS_BRANCH}" == "production" ]; then
  DEPLOYMENT_MODE="PRODUCTION"
elif [ "${TRAVIS_BRANCH}" == "master" ]; then
  DEPLOYMENT_MODE="STAGING"
else
  helper_halt_deployment "TRAVIS_BRANCH: '${TRAVIS_BRANCH}' cannot be deployed to staging or production."
fi;


echo "Working with deployment mode: ${DEPLOYMENT_MODE}"

function to_uppercase {
  echo $1 | awk '{print toupper($0)}'

}

function to_lowercase {
  echo $1 | awk '{print tolower($0)}'
}

function resolve_function_name {
  ZAPPA_DEPLOYMENT_MODE=$(to_lowercase $DEPLOYMENT_MODE)
  echo
}

function resolve_bucket {
  if [ "${DEPLOYMENT_MODE}" == "PRODUCTION" ]; then
    echo $AWS_BUCKET_NAME_PRODUCTION;
  else
    echo $AWS_BUCKET_NAME_STAGING;
  fi;
}

function backend_set_env_vars {

  print_header "Setting up environment variables for: ${DEPLOYMENT_MODE}"


  AWS_BUCKET_NAME=$(resolve_bucket)
  ZAPPA_DEPLOYMENT_MODE=$(to_lowercase $DEPLOYMENT_MODE)
  AWS_FUNCTION_NAME="police-monitor-${ZAPPA_DEPLOYMENT_MODE}"

  echo "DEPLOYMENT_MODE: ${DEPLOYMENT_MODE}"
  echo "KNACK_APPLICATION_ID: ${KNACK_APPLICATION_ID}"
  echo "KNACK_API_KEY: 123-123..."
  echo "PM_LOGTABLE: ${PM_LOGTABLE}"
  echo "AWS_BUCKET_NAME: ${AWS_BUCKET_NAME}"
  echo "AWS_FUNCTION_NAME: ${AWS_FUNCTION_NAME}"

  aws lambda update-function-configuration \
        --function-name $AWS_FUNCTION_NAME \
        --environment "Variables={DEPLOYMENT_MODE=${DEPLOYMENT_MODE},KNACK_APPLICATION_ID=${KNACK_APPLICATION_ID},KNACK_API_KEY=${KNACK_API_KEY},PM_LOGTABLE=${PM_LOGTABLE},AWS_BUCKET_NAME=${AWS_BUCKET_NAME},EMAIL_ADDRESS_USER='${EMAIL_ADDRESS_USER}',EMAIL_ADDRESS_APD='${EMAIL_ADDRESS_APD}',EMAIL_ADDRESS_OPO='${EMAIL_ADDRESS_OPO}'"
}


function backend_create_backup {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
  echo "Deployment Mode: ${DEPLOYMENT_MODE}"
}

#
# Packages the application and deploys to a Lambda Function
#
function backend_build {
  print_header "Building API app for: ${DEPLOYMENT_MODE}"
  ZAPPA_DEPLOYMENT_MODE=$(to_lowercase $DEPLOYMENT_MODE)
  zappa update $ZAPPA_DEPLOYMENT_MODE
}



function backend_postrelease {
  CURRENT_BRANCH=$1
  echo "Nothing to be done for $CURRENT_BRANCH"
  echo "Deployment Mode: ${DEPLOYMENT_MODE}"
}
