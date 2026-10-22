import sys
from django.apps import AppConfig


class CdManagerConfig(AppConfig):
    name = 'cd_manager'

    def ready(self):
        if (not any("manage.py" in e for e in sys.argv)) or ("runserver" in sys.argv):
            from cd_manager.models import Package
            Package.objects.filter(build_status__in=("BUILDING", "PREPARING", "WAITING")).update(
                build_status="NOT_BUILT")
