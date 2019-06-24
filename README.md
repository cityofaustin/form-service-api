# coa-forms-api
This is the backend for [coa-forms](https://github.com/cityofaustin/coa-forms), the Office of Design and Delivery's form service. It is deployed on AWS Lambda with Zappa and it is written in Python and Flask.

To run the server, you will need to make some environment preparations as well as installing some dependencies.

## 1. Set up Environment Variables:
Here is a list of our required Environment variables.

`local_env.example` provides a reference of what environment variables you'll need for local development. If you want, you can `cp local_env.example local_env.sh` and fill in your preferred environment variable settings there. Or you can source them from your ~/.bash_profile.

For new environment variables to be accessed on a deployed Zappa instance through `os.getenv()`, you must add them to the `vars_to_add` list in `.circleci/scripts/build_zappa_settings.py` as well as `.circleci/scripts/env.sh`.

Common:
  - DEPLOYMENT_MODE
    - tells code which environment the code is being displayed in
  - DYNAMO_DB_TABLE
    - currently only used to cache case_numbers, we don't store any form submission data.
  - S3_UPLOADS_BUCKET
    - name of the bucket where attachments/media files from coa-forms will be stored. Also used as a temp directory to store zappa build artifacts.
  - EMAIL_SMOKE_TEST
    - dev email address to send to if you're debugging (overwrites EMAIL_OPO/EMAIL_APD)

OPO Specific:
  - EMAIL_OPO
    - email address sent to Office of Police Oversight for opo "complaint" form
  - EMAIL_APD
    - email address sent to Austin Police Department for opo "thanks"
  - EMAIL_OPO_REPLYTO
    - replyto email address for both opo forms

Local Only:
  - S3_KEY
    - AWS credentials, could be stored in ~/.aws/credentials rather than explicit env var
  - S3_SECRET
    - AWS credentials, could be stored in ~/.aws/credentials rather than explicit env var


## 2. First, set up the virtual env:

You can use pipenv
```
pipenv shell
pipenv install
```
Or virtualenv (https://virtualenv.pypa.io/en/latest/installation/)
```
virtualenv pmenv
source pmenv/bin/activate
```

## 3. Run Locally:
```
python main.py
```

or if you have nodemon installed:
```
nodemon --exec python3 main.py
```

Or optionally, for convenience of environment variable sourcing:
```
sh run-local.sh
```

# Adding New Forms

Common views are routes that are used by any form, common templates are the base styles and structure used by any form, all services should be compatible with any form.

These are the 3 steps required to add a new form to the coa-forms-api.

#### 1. Add a View
Each form has a view in src/views/your_form.py, which contains a /submit route. This is where any data transformations happen before building an email template.
#### 2. Add templates
Construct the templates in src/templates/your_form/* to build emails for outlook, non-outlook clients, and text.
#### 3. Register your View
Import and register your flask blueprint in src/app.py

# Deployment to AWS Lambda

You may want to familiarize with the zappa documentation. First, the function needs to be deployed once, and updated constantly thereafter. Also, you should upload different environments (production, dev, etc). For this particular project we will be using TravisCI to manage our deployments.

[Zappa Documentation](https://github.com/Miserlou/Zappa)

```
zappa deploy dev (done only once, the first time)
zappa update dev (re-reploy & update code)
zappa undeploy dev (to remove service)
```

# Templates

Flask uses the `Jinja2` template engine to generate dynamic html pages, we use this same engine to render our html and txt emails. Most of the templates are used for emails, since we don't really need the backend-api to render any client-facing html code.

For documentation, visit: (http://jinja.pocoo.org/docs/2.10/)[http://jinja.pocoo.org/docs/2.10/]

#### Custom Functions & Custom Variables

The Jinja2 engine allows defining custom functions and global variables. We defined a couple custom functions and variables that help us with translations specifically. These functions are defined in regular python, and then incorporated in global variables:

For example, we first define our translate function:

```
def translate(key):
	"""
		This function finds a key in the TRANSLATION_DICT and returns it's value:

		From a sample.yml file:
		-------
		phone_key:
			en: "Phone"
			es: "Teléfono"
		any_other_key:
			en: "Value in English"
			es: "Value in Spanish"
			ar: "Value in Arabic"
			xx: "..."
	"""
    global TRANSLATION_DICT
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
```



Now we make it part of our functions available to the template render engine:

```
template_configs = {
      ...
      "t": t,
      ...
  }
```

And then we use them in the template:

```
<div class="form-confirmation">
      {% if language_code() == 'es' %}
          <p>Muchas gracias por compartir su experiencia con nosotros, esto nos ayuda a servirles mejor a usted y a su comunidad.</p>

          <p class="blue">Su número de confirmación es: <span class="form-data-casenumber">{{casenumber}}</span></p>
      {% else %}
          <p>Thank you for sharing your experience with us. This helps us better serve you and your community.</p>

          <p class="blue">Your confirmation number is: <span class="form-data-casenumber">{{casenumber}}</span></p>
      {% endif %}
    </div>
```

Another example:

```
<div>
      <div class='form-data-section_title'>{{t('tell_us_about_the_officers')}}</div>
      <div class='form-data-section'>
          {% for officer in data['officers'] %}
          <div class='form-data-section_item'>
            <span>{{t('officer')}} #{{loop.index}}:</span>
            <ul>
              <li>{{t('name')}}: {{officer['name'] or 'N/A' }}</li>
              <li>{{t('description')}}: {{officer['physicalDescription'] or 'N/A' }}</li>
              <li>{{t('race')}}: {{officer['race'] or 'N/A' }}</li>
              <li>{{t('gender')}}: {{officer['gender'] or 'N/A' }}</li>
              <li>{{t('badge_number')}}: {{officer['badgeNumber'] or 'N/A' }}</li>
              <li>{{t('uniformed')}}: {{officer['uniformed'] or 'N/A' }}</li>
              <li>{{t('transportation')}}: {{officer['transportation'] or 'N/A' }}</li>
            </ul>
          </div>
          {% endfor %}
      </div>
    </div>
```



#### E-Mail

The e-mail templates are found in the `src/templates` directory.

Inside that directory, there are also three sub-directories: `common`, `complaint` and `thanks`, one for each of the current OPO forms. You should be able to create as many other directories as you need, depending on the number of templates you need to generate.

- Common: this directory should contain shared html elements/components that will be used in all the other templates, in this case, complaint and thanks share a number of components and they are stored in `common`.
- Complaint, Thanks: Contain the html specific for those templates. The complaint directory contains specific language that pertains to a complaint, and thanks contains language specific for that type of response.

The templates use shared components by using Jinya's include method, ie:

```
{% include 'templates/common/head.html' %}
```

# Translations

The translations are put into a yaml file, and it follows a basic syntax. The file is loaded in-memory into a dictionary in python, and from there the translations will be available to the entire application.

The first step is to load the yaml file, for that there is this method:

```
# load a given language
    load_translation('templates/email/officepoliceoversight/language.yaml',
        section=submission_type,
        language=currentLangCode)
```



The first parameter is the yaml file you wish to load, in this case we are loading a translations file for our emails located in `templates/email/officepoliceoversight/language.yaml`. The second is value is called `section` and it contains the section within the yaml file (see syntax below), if the section is not found or does not exist, its value will default to `common`. The `language` parameter is the language code that needs to be rendered (see syntax below), this parameter will contain strings such as `en` (for English), `es` for Spanish, and you can come up with any additional codes you want (ie. `ar, vi` for Arabic or Vietnamese respectively).

Sample syntax:

```
common:
  referrer:
    en: "Referrer"
    es: "Referente"
  gender:
    en: "Gender"
    es: "Genero"
  race:
    en: "Race"
    es: "Raza"
  zipcode:
    en: "Zip Code"
    es: "Codigo de Area"
complaint:
  emailSubject:
    en: "Your complaint was submitted successfully."
    es: "Correo electrónico de confirmación de la queja."
  title:
    en: "Your complaint was submitted successfully."
    es: "Hemos recibido su queja."
thanks:
  title:
    en: "Confirmation for Thanks"
    es: "¡Su nota de agradecimiento fue enviada!"
  emailSubject:
    en: "Your thank you was submitted successfully!"
    es: "Confirmación de agradecimiento"
```

The syntax:

```
common:
	key:
		language_code_a: "Value"
		language_code_b: "Value"
		...: "..."
section_a:
	key:
		language_code_a: "Value"
		language_code_b: "Value"
		...: "..."
section_b:
	key:
		language_code_a: "Value"
		language_code_b: "Value"
		...: "..."
```

Common is a required section, if not present the translate function is going to crash. The common section is there to help reduce redundancy, it was meant to have common words and phrases that will be shared across all sections. You can have as many sections as needed, these should be specific to a group.

The translate method will try to find the section you specified, if it can't find the key in the specified section, then it will try to find it on the common section, otherwise it will fail and return an empty string.
