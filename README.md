# Police Monitor Server
This is the police monitor form server for AWS Lambda, it has been written in Python and Flask.

To run the server, you will need to make some environment preparations as well as installing some dependencies.

## 1. Set up Environment Variables:

For AWS:

```
export AWS_BUCKET_NAME="..."
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

After these five variables have been set up, you can then start with your development environment:



## 2. First, set up the virtual env:

If you don't have virtualenv, be sure to follow these steps to install it: https://virtualenv.pypa.io/en/latest/installation/

Once you make sure virtualenv is up and running, then set your dev environment with these two commands:


```
virtualenv pmenv
source pmenv/bin/activate
```



## 3. Dependencies

You will need to install flask for our API, Zappa for deployment, boto for aws s3 integration, Pillow for file management:

```
pip install flask flask-cors zappa boto3 Pillow
pip freeze > requirements.txt
```



## 4. Run Locally:

After completing all previous steps, you can now launch the server locally:

```
python main.py
```


## 5. Deployment to AWS Lambda

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
#
# Make the 'translate' function and 'get_language_code' functions available
# alias as 't' and 'language_code' respectively.
#
OPO_ENV.globals['t'] = translate
OPO_ENV.globals['language_code'] = get_language_code
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

The e-mail templates are found in the `templates/email/officeofpoliceoversight` directory. This having in mind future growth for other departments.

Inside that directory, there are also three sub-directories: `common`, `complaint` and `thanks`, one for each of the current OPO forms. You should be able to create as many other directories as you need, depending on the number of templates you need to generate.

- Common: this directory should contain shared html elements/components that will be used in all the other templates, in this case, complaint and thanks share a number of components and they are stored in `common`.
- Complaint, Thanks: Contain the html specific for those templates. The complaint directory contains specific language that pertains to a complaint, and thanks contains language specific for that type of response.

The templates use shared components by using Jinya's include method, ie:

```
{% include 'email/officepoliceoversight/common/head.html' %}
```

# Translations

The translations are put into a yaml file, and it follows a basic syntax. The file is loaded in-memory into a dicctionary in python, and from there the translations will be available to the entire application.

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
