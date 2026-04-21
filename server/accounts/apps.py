from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = 'accounts'

    def createGroups(self, sender, **kwargs):
        from django.contrib.auth.models import Group
        for group_name in ['Patients', 'Doctors', 'Receptionists', 'Admins']:
            Group.objects.get_or_create(name=group_name)

    def ready(self):
        post_migrate.connect(self.createGroups)
        