import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_pkgname(value):
    # as of writing the longest pkgname is
    # python-opentelemetry-exporter-otlp-proto-common (46 chars)
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9@_+][a-zA-Z0-9@._+-]{0,49}', value):
        raise ValidationError(
            _('Use 1 to 50 ASCII letters, digits, @, ., _, + or -; names cannot start with . or -.'),
            code='invalid_package_name',
        )
