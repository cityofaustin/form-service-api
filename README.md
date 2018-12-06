# Police Monitor Server
This is the police monitor form server for AWS Lambda, it has been written in Python, Flask, and its function is to integrate a form with Knack.

To run the server, you will need to make some environment preparations as well as installing some dependencies.

First the Knack environment Variables, then for AWS, in this order:

## 1. Set up Environment Variables:

First, for Knack:

```
export KNACK_APPLICATION_ID="..."
export KNACK_API_KEY="..."
```

Then, for AWS:

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

You will need to install flask for our API, Zappa for deployment, boto for aws s3 integration, Pillow for file management, and knackpy for Knack integration:

```
pip install flask flask-cors zappa boto3 Pillow knackpy
pip freeze > requirements.txt
```



## 4. Run Locally:

After completing all previous steps, you can now launch the server locally:

```
python main.py
```


## 5. Deployment to AWS Lambda

This step is not necessary, it is taken care of by Travis-CI, but for development purposes you can deploy this application using zappa like this:

```
zappa update dev
```
