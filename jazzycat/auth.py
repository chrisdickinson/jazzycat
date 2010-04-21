from nappingcat.auth import AuthBackend
from nappingcat.exceptions import NappingCatRejected
from django.contrib.auth.models import User
from jazzycat.models import SSHPublicKey, SimplePermission
import os 

PERMISSION_GLUE = "::"

class DjangoAuth(AuthBackend):
    def __init__(self, *args, **kwargs):
        super(DjangoAuth, self).__init__(*args, **kwargs)
        os.environ['DJANGO_SETTINGS_MODULE'] = dict(self.settings.items('djangoauth'))['django_settings']

    def has_permission(self, username, permission):
        return len(SimplePermission.objects.filter(
            user__username=username,
            permission_string=PERMISSION_GLUE.join(permission)
        ))

    def add_permission(self, username, permission):
        try:
            SimplePermission.objects.create(
                user=User.objects.get(username=username),
                permission_string=PERMISSION_GLUE.join(permission)
            )
        except User.DoesNotExist:
            raise NappingCatRejected("%s isn't a user!" % username)

    def remove_permission(self, username, permission):
        SimplePermission.objects.delete(
            user__username=username,
            permission_string=PERMISSION_GLUE.join(permission)
        )

    def add_user(self, username):
        User.objects.create_user(
            username,
            '%s@localhost'%username
        )

    def add_key_to_user(self, user, key):
        try:
            SSHPublicKey.objects.create(
                user=User.objects.get(username=user)
                key=key
            )
        except User.DoesNotExist:
            return False

    def get_users(self):
        return [u.username for u in User.objects.all()]

    def get_key(self, user):
        return [k.key for k in SSHPublicKey.objects.filter(user__username=user)]
