import os, json

# Constructs and writes the zappa_settings.json object used by zappa command in deploy.sh

zappa_settings = {
    "PLACEHOLDER_STAGE_NAME": {
        "app_function": "main.app",
        "profile_name": None,
        "project_name": "coa-forms-api",
        "runtime": "python3.7",
        "log_level": "ERROR",
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

config["s3_bucket"] = os.getenv("S3_UPLOADS_BUCKET")
config["role_name"] = f"coa-forms-api-{os.getenv('ZAPPA_STAGE')}".replace('_','-')[:64] # AWS IAM roles must be under 64 characters

vars_to_add = [
    "DEPLOYMENT_MODE",
    "S3_UPLOADS_BUCKET",
    "DYNAMO_DB_TABLE",
    "EMAIL_OPO",
    "EMAIL_APD",
    "EMAIL_OPO_REPLYTO",
    "EMAIL_SMOKE_TEST",
    "EMAIL_DAY_LABOR",
    "EMAIL_DAY_LABOR_REPLYTO"
]
config["environment_variables"] = {v: os.getenv(v, "") for v in vars_to_add}

zappa_settings_file = os.path.join(os.path.dirname(__file__), '../../zappa_settings.json')
with open(zappa_settings_file, 'w', encoding='utf-8') as outfile:
    json.dump(zappa_settings, outfile, ensure_ascii=False, indent=4)
