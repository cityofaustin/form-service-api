import os, sys, json

# source env file from /src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
import env

# Constructs and writes the zappa_settings.json object used by zappa command in deploy.sh

zappa_settings = {
    "PLACEHOLDER_STAGE_NAME": {
        "app_function": "init.app",
        "profile_name": None,
        "project_name": "coa-forms-api",
        "runtime": "python3.6",
        "s3_bucket": "PLACEHOLDER_S3_BUCKET",
        "environment_variables": {
        },
        "extra_permissions": [{
            "Effect": "Allow",
            "Action": ["ses:*"],
            "Resource": "*"
        }]
    }
}

config = zappa_settings[os.getenv("ZAPPA_STAGE")] = zappa_settings.pop("PLACEHOLDER_STAGE_NAME")

config["s3_bucket"] = env.S3_UPLOADS_BUCKET
config["environment_variables"] = {
    "DEPLOYMENT_MODE": env.DEPLOYMENT_MODE,
    "S3_UPLOADS_BUCKET": env.S3_UPLOADS_BUCKET,
    "DYNAMO_DB_TABLE": env.DYNAMO_DB_TABLE,
    "EMAIL_OPO": env.EMAIL_OPO,
    "EMAIL_APD": env.EMAIL_APD,
    "EMAIL_OPO_REPLYTO": env.EMAIL_OPO_REPLYTO,
    "EMAIL_SMOKE_TEST": env.EMAIL_SMOKE_TEST
}

zappa_settings_file = os.path.join(os.path.dirname(__file__), '../../zappa_settings.json')
with open(zappa_settings_file, 'w', encoding='utf-8') as outfile:
    json.dump(zappa_settings, outfile, ensure_ascii=False, indent=4)
