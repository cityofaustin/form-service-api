import re, datetime, uuid, hashlib

#####
# Helpers for /uploads/request-signature
#####

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def get_file_name(filename):
    return filename.rsplit('.', 1)[0].lower()

def generate_clean_filename(filename):
    timestamp = filename_timestamp()
    fileExt = get_file_extension(filename)
    fileName = get_file_name(filename)
    clean_filename = re.sub(r'\W+', '', fileName)
    clean_filename = "{0}.{1}".format(clean_filename, fileExt)
    shortHash = generate_random_hash()[0:5]
    return "{0}_{1}_{2}".format(timestamp, shortHash, clean_filename)

def is_valid_uniqueid(uqid):
	pattern = re.compile("^([a-z0-9]){64}$")
	return str(pattern.match(uqid)) != "None"

#####
# Time
#####

def getCurrentDateTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def filename_timestamp():
  now = datetime.datetime.now()
  return now.strftime("%m%d%Y%H%M%S")

#####
# Random Number Generator
#####

def generate_random_hash():
    rand_uuid_str = "{0}".format(uuid.uuid1()).encode()
    return hashlib.sha256(rand_uuid_str).hexdigest()

#####
# Debug
#####

# If description starts with "DEBUG" or "debug", then the submission is a smoke test.
# OPO/APD emails will be sent to dev email address
def is_smoke_test(data):
    try:
        return re.match("^DEBUG", data['description'], re.IGNORECASE)
    except:
        return False
