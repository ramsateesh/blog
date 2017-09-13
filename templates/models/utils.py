import re
import random
import hashlib
import hmac
from string import letters

secret = 'k@P@1@m@n3kuDu'

#hash tools
def make_secure_val(val):
    val = str(val)
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def get_user_id_from_cookie(cookie):
    if cookie is None:
        return None
    (id, hash) = cookie.split("|")
    if cookie == make_secure_val(id):
        return id
    else:
        return None

# User Registration Validations
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

# Password related Functionality
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)
