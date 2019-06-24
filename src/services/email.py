import os, yaml, boto3
from jinja2 import Environment, FileSystemLoader, Undefined, Template
from flask import url_for
from botocore.exceptions import ClientError

if(os.getenv("DEPLOYMENT_MODE") == "local"):
    # Initialize S3 Client
    ses_client = boto3.client('ses', region_name=os.getenv("DEFALUT_REGION"), aws_access_key_id=os.getenv("S3_KEY"), aws_secret_access_key=os.getenv("S3_SECRET"))
else:
    # We should already have access to these resources
    ses_client = boto3.client('ses', region_name=os.getenv("DEFALUT_REGION"))

# Parse translations in language.yaml into python dictionary
language_file = os.path.join(os.path.dirname(__file__), '../language.yaml')
with open(language_file) as stream:
    translations = yaml.load(stream, Loader=yaml.FullLoader)

# ignore undefined errors within jinja
class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
    def _new(*args, **kwargs):
        return SilentUndefined()
    __call__ = __getitem__ = __getattr__ = _new
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __lt__ = __le__ = \
        __gt__ = __ge__ = __int__ = __float__ = __complex__ = __pow__ = \
        __rpow__ = _fail_with_undefined_error

# Initialize jinja templating environment
jinja_env = Environment(
    undefined=SilentUndefined,
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates/'))
)
jinja_env.filters['basename'] = os.path.basename

# Builds a translation function for your form and language
def translation_factory(form_type, language_code):
    def t(key):
        try:
            return translations['common'][key][language_code]
        except:
            """ Not found in common words, trying section """

        try:
            return translations[form_type][key][language_code]
        except:
            if key:
                print("translate() Form Type: '{0}', Key: '{1}', Language: '{2}' -- NOT FOUND".format(form_type, key, language_code))

        return ""
    return t

def render_email_template(template_filepath, **kwargs):
    template = jinja_env.get_template(template_filepath)
    return template.render(**kwargs)

def send_email(form_type, language_code, email_recipient, email_source, case_number, data, media_files):
    # Build a translation function for our form and language
    t = translation_factory(form_type, language_code)

    template_configs = {
        "case_number": case_number,
        "data": data,
        "attachment_urls": media_files,
        "api_endpoint": url_for('common.file_download_uri', path='', _external=True),
        "t": t,
        "basename": os.path.basename
    }

    # Render HTML template
    htmlTemplate = render_email_template(f"{form_type}/template.html", **template_configs)

    # Render TXT template (for non-html compatible services)
    txtTemplate = render_email_template(f"{form_type}/template.txt", **template_configs)

    email_config = {
        "charset": "UTF-8",
        "html": htmlTemplate,
        "text": txtTemplate,
        "subject": t('emailSubject'),
        "source": email_source, # What it looks like in reply-to.
        "recipient": email_recipient
    }

    # Try to submit, capture status
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [
                    email_config['recipient'],
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': email_config['charset'],
                        'Data': email_config['html'],
                    },
                    'Text': {
                        'Charset': email_config['charset'],
                        'Data': email_config['text'],
                    },
                },
                'Subject': {
                    'Charset': email_config['charset'],
                    'Data': email_config['subject'],
                },
            },
            Source=email_config['source']
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        raise e
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")
