#####
# Helpers for /uploads/request-signature
#####

def generate_clean_filename(filename):
  timestamp = filename_timestamp()
  cleanFilename = clean_filename(filename)
  shortHash = generate_random_hash()[0:5]
  return "{0}_{1}_{2}".format(timestamp, shortHash, cleanFilename)

def generate_random_hash():
    rand_uuid_str = "{0}".format(uuid.uuid1()).encode()
    return hashlib.sha256(rand_uuid_str).hexdigest()

def is_valid_uniqueid(uqid):
	pattern = re.compile("^([a-z0-9]){64}$")
	return str(pattern.match(uqid)) != "None"
