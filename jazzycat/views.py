from django.http import HttpResponse, Http404
from django.contrib.models import User
from jazzycat.models import SSHPublicKey, SimplePermission
from nappingcat import auth
from django.utils import simplejson
import paramiko

def register(request):
    username = request.POST.get('username', None)
    key = request.POST.get('key', None)
    email = request.POST.get('email', None)

    if username is None:
        email_part, rest = email.rsplit('.', 1)
        username = email_part.replace('@', '.')

    if len(User.objects.filter(username=username)) > 0:
        return HttpResponse(simplejson.dumps({
            'error':"the username '%s' is already taken" % username
        }), mimetype="text/json", status_code=409)

    auth.add_user(nappingcat_request, username)
    auth.add_key_to_user(nappingcat_request, username, key, target=) 

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('127.0.0.1', username='git')
    stdin, stdout, stderr = client.exec_command("add-user %s" % username)
    for stream in stdin, stdout, stderr:
        stream.channel.shutdown(2)
        stream.close()

    stdin, stdout, stderr = client.exec_command("add-key-to-user %s" % username)
    stdin.write(key)
    stdin.flush()
    stdin.channel.shutdown(2)    
    results = stderr.read()

    return HttpResponse(simplejson.dumps({
        'success':"You successfully registered the username '%s'"%username,
    }, status_code=200, mimetype="text/json")

