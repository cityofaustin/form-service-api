from jinja2 import Environment, FileSystemLoader, Undefined, Template
import os, yaml

from env import *

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

def translate(key):
    section = TRANSLATION_DICT["___default_section___"]
    language = TRANSLATION_DICT["___default_language___"]

    try:
        return TRANSLATION_DICT['common'][key][language]
    except:
        """ Not found in common words, trying section """

    try:
        return TRANSLATION_DICT[section][key][language]
    except:
        print("translate() Section: '{0}', Key: '{1}', Language: '{2}' -- NOT FOUND".format(section, key, language))

    return ""

def get_language_code():
    try:
        return TRANSLATION_DICT["___default_language___"]
    except:
        return "en"

# Parse translations in language.yaml into python dictionary
language_file = os.path.join(os.path.dirname(__file__), '../language.yaml')
with open(language_file) as stream:
    TRANSLATION_DICT = yaml.load(stream, Loader=yaml.FullLoader)

# Add functions and configs to use in jinja templates
forms_dir = os.path.join(os.path.dirname(__file__), '../forms')
form_paths = [os.path.join(os.path.dirname(__file__), f'../forms/{f}') for f in os.listdir(forms_dir)]
jinja_env = Environment(undefined=SilentUndefined,loader=FileSystemLoader(form_paths))

jinja_env.filters['basename'] = os.path.basename #TODO: why does jinja need this?
jinja_env.globals['t'] = translate
jinja_env.globals['language_code'] = get_language_code
#
# def send_opo_email(submission_type, language_code, recipient, caseNumResp, data, mediaFiles):
#     # We load the language of the recipient, for opo or apd must default to english.
#     currentLangCode = language_code if is_recipient(recipient) else "en"
#
#     # load given language
#     load_translation('templates/email/officepoliceoversight/language.yaml',
#         section=submission_type,
#         language=currentLangCode)
#
#     # Now we specify the destination email, and translated subject
#     emailConfig = None
#     emailConfig = emailConfigDefault.copy()
#     emailConfig['recipient'] = recipient
#     emailConfig['subject'] = translate('emailSubject')
#
#     # Render HTML template
#     htmlTemplate = render_email_template("email/officepoliceoversight/" + submission_type + "/template.html",
#         casenumber=caseNumResp,
#         data=data,
#         attachment_urls=mediaFiles,
#         api_endpoint=url_for('file_download_uri', path='', _external=True)
#     )
#
#     # Render TXT template (for non-html compatible services)
#     txtTemplate = render_email_template("email/officepoliceoversight/" + submission_type + "/template.txt",
#         casenumber=caseNumResp,
#         data=data,
#         attachment_urls=mediaFiles,
#         api_endpoint=url_for('file_download_uri', path='', _external=True)
#     )
#
#     emailConfig['html'] = htmlTemplate
#     emailConfig['text'] = txtTemplate
#
#     # Try to submit, capture status
#     try:
#         response = sendEmail(emailConfig)
#     except Exception as e:
#         raise e
