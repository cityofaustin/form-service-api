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
  DEPLOYMENT_MODE="production"
elif [ "${TRAVIS_BRANCH}" == "master" ]; then
  DEPLOYMENT_MODE="staging"
else
  helper_halt_deployment "TRAVIS_BRANCH: '${TRAVIS_BRANCH}' cannot be deployed to staging or production."
fi;




function backend_create_backup {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
}


function backend_create_backup {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
}


function backend_build {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
  #zappa update $DEPLOYMENT_MODE
}



function backend_release {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
}




function backend_migrate {
  CURRENT_BRANCH=$1

  echo "Nothing to be done for $CURRENT_BRANCH"
}
