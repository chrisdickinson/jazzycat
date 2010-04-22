from django.conf import settings
from django.contrib.models import User
from django.http import HttpResponse, Http404
from django.utils import simplejson
from jazzycat.auth import PERMISSION_GLUE
import paramiko

def register(request, django_settings=settings):
    """
        by no means should you ever use this code.
        not even if you're really really drunk, and your friend is all
        "c'mon bro just one time it won't hurt yeahhh do it". it's a bad
        idea to use this code production-wise, period.

        and if you do use it and somehow it burns your lovely little repo
        server down into a cinder-y shadow of its former self, 
            A) you deserve it
            B) not my fault
            C) quit listening to your friend, esp. if he calls you "bro"

        love,
            chris
    """
    if request.method != 'POST':
        raise Http404()

    username = request.POST.get('username', None)
    key = request.POST.get('key', None)
    email = request.POST.get('email', None)

    if username is None:
        email_part, rest = email.rsplit('.', 1)
        username = email_part.replace('@', '.')

    if len(User.objects.filter(username=username)) > 0:
        return HttpResponse(simplejson.dumps({
            'error':"the username '%s' is already taken" % username
        }), mimetype="text/json", status=409)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(django_settings.JAZZYCAT_HOST, username=django_settings.JAZZYCAT_USERNAME)
    stdin, stdout, stderr = client.exec_command("add-user %s" % username)
    for stream in stdin, stdout, stderr:
        stream.channel.shutdown(2)
        stream.close()

    stdin, stdout, stderr = client.exec_command("add-key-to-user %s" % username)
    stdin.write(key)
    stdin.flush()
    stdin.channel.shutdown(2)    
    results = stderr.read()

    for permission in django_settings.JAZZYCAT_AUTO_PERMISSIONS:
        stdin, stdout, stderr = client.exec_command("add-permission %s '%s'" % (username, PERMISSION_GLUE.join(permission))
        stdin.close(); stdout.close(); stderr.close()

    return HttpResponse(simplejson.dumps({
        'success':"You successfully registered the username '%s'"%username,
        'results':results,
    }, status=200, mimetype="text/json")

