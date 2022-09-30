import sys
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abs_cd.settings')

application = get_wsgi_application()

if __name__ == "__main__":
    import bjoern

    if len(sys.argv) > 2:
        bjoern.run(application, sys.argv[1], int(sys.argv[2]))
    else:
        bjoern.run(application, "0.0.0.0", 8000)
