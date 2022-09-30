import sys
from django.apps import AppConfig


class CdManagerConfig(AppConfig):
    name = 'cd_manager'

    def ready(self):
        if (not any("manage.py" in e for e in sys.argv)) or ("runserver" in sys.argv):
            from cd_manager.models import Package
            pkgs = Package.objects.filter(build_status="BUILDING").union(
            Package.objects.filter(build_status="PREPARING"),
            Package.objects.filter(build_status="WAITING"))
            for pkg in pkgs:
                pkg.build_status = "NOT_BUILT"
                pkg.save()
