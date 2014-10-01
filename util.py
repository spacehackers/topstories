# safe_float, json, jsonp copied from @natronics: https://github.com/open-notify/Open-Notify-API/blob/master/util.py
import os
import smtplib
from functools import wraps
from flask import jsonify, request, current_app
from functools import wraps
from flask import request, Response

from email.mime.text import MIMEText
MAILGUN_SMTP_LOGIN = os.getenv('MAILGUN_SMTP_LOGIN')
MAILGUN_SMTP_PASSWORD = os.getenv('MAILGUN_SMTP_PASSWORD')

def send_email(subject, body, to):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "foo@samples.mailgun.org"
    msg['To'] = to
    s = smtplib.SMTP('smtp.mailgun.org', 587)
    s.login(MAILGUN_SMTP_LOGIN, MAILGUN_SMTP_PASSWORD)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()



def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.environ['ADMIN_USER'] and password == os.environ['ADMIN_PASS']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def safe_float(s, range, default=False):
    try:
        f = float(s)
    except:
        return default

    if f > range[1]:
        return default
    if f < range[0]:
        return default

    return f


# json endpoint decorator
def json(func):
    """Returning a object gets JSONified"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        return jsonify(func(*args, **kwargs)[0]), func(*args, **kwargs)[1]
    return decorated_function

# from farazdagi on github
#   https://gist.github.com/1089923
def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs)[0].data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype), func(*args, **kwargs)[1]
        else:
            return func(*args, **kwargs)
    return decorated_function

# from aisipos on github
#   https://gist.github.com/aisipos/1094140
def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args,**kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function
