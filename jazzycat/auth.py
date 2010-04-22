from nappingcat.auth import AuthBackend
from nappingcat.exceptions import NappingCatRejected
import os 

PERMISSION_GLUE = "::"

class DjangoAuth(AuthBackend):
    def __init__(self, *args, **kwargs):
        super(DjangoAuth, self).__init__(*args, **kwargs)
        os.environ['DJANGO_SETTINGS_MODULE'] = dict(self.settings.items('djangoauth'))['django_settings']
        from django.contrib.auth.models import User
        from jazzycat.models import SSHPublicKey, SimplePermission
        self.User, self.SSHPublicKey, self.SimplePermission = User, SSHPublicKey, SimplePermission

    def has_permission(self, username, permission):
        return len(self.SimplePermission.objects.filter(
            user__username=username,
            permission_string=PERMISSION_GLUE.join(permission)
        ))

    def add_permission(self, username, permission):
        try:
            self.SimplePermission.objects.create(
                user=self.User.objects.get(username=username),
                permission_string=PERMISSION_GLUE.join(permission)
            )
        except self.User.DoesNotExist:
            raise NappingCatRejected("%s isn't a user!" % username)

    def remove_permission(self, username, permission):
        self.SimplePermission.objects.delete(
            user__username=username,
            permission_string=PERMISSION_GLUE.join(permission)
        )

    def add_user(self, username):
        self.User.objects.create_user(
            username,
            '%s@localhost'%username
        )

    def add_key_to_user(self, user, key):
        try:
            self.SSHPublicKey.objects.create(
                user=self.User.objects.get(username=user)
                key=key
            )
        except self.User.DoesNotExist:
            return False

    def get_users(self):
        return [u.username for u in self.User.objects.all()]

    def get_keys(self, user):
        return [k.key for k in self.SSHPublicKey.objects.filter(user__username=user)]
