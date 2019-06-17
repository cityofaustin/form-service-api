from jinja2 import Environment, FileSystemLoader, Undefined, Template
import os, yaml

from flask import url_for
import env

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
jinja_env = Environment(undefined=SilentUndefined,loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates/')))
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
            print("translate() Form Type: '{0}', Key: '{1}', Language: '{2}' -- NOT FOUND".format(form_type, key, language_code))

        return ""
    return t

def render_email_template(form_type, **kwargs):
    template_filepath = "src/templates/form_type"
    template_file = os.path.basename(template_filepath)
    template = jinja_env.get_template(template_filepath)
    return(template.render(**kwargs))

def send_email(form_type, language_code, recipient, case_number, data, media_files, smoke_test=False):
    # Build a translation function for our form and language
    t = translation_factory(form_type, language_code)

    template_configs = {
        "casenumber": case_number,
        "data": data,
        "attachment_urls": media_files,
        "api_endpoint": url_for('file_download_uri', path='', _external=True),
        "t": t,
        "language_code": language_code,
        "basename": os.path.basename
    }

    # Render HTML template
    htmlTemplate = render_email_template(f"src/templates/{form_type}/template.html", **template_configs)

    # Render TXT template (for non-html compatible services)
    txtTemplate = render_email_template(f"src/templates/{form_type}/template.txt", **template_configs)

    emailConfig = {
        "charset": "UTF-8",
        "html": htmlTemplate,
        "text": txtTemplate,
        "subject": t('emailSubject'),
        # "source": EMAIL_ADDRESS_SENDER, # Who sends the email # TODO: eliminate??
        "source": env.EMAIL_ADDRESS_REPLYTO, # What it looks like in reply-to.
        "recipient": recipient, # "no-reply@austintexas.io"
    }

    if (smoke_test):
        emailConfig["recipient"] = env.SMOKE_TEST_EMAIL

    # Try to submit, capture status
    try:
        response = env.ses_client.send_email(
            Destination={
                'ToAddresses': [
                    emailConfig['recipient'],
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': emailConfig['charset'],
                        'Data': emailConfig['html'],
                    },
                    'Text': {
                        'Charset': emailConfig['charset'],
                        'Data': emailConfig['text'],
                    },
                },
                'Subject': {
                    'Charset': emailConfig['charset'],
                    'Data': emailConfig['subject'],
                },
            },
            Source=emailConfig['source']
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    except Exception as e:
        raise e
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")
