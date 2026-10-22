import os

from django.conf import settings
from django.core.exceptions import ValidationError

from cd_manager.validators import validate_pkgname


def pkgbuild_repos_path(name):
    """Return a direct child of the package root, never a package symlink."""
    validate_pkgname(name)
    root = os.path.realpath(settings.PKGBUILDREPOS_PATH)
    path = os.path.join(root, name)
    if os.path.islink(path):
        raise ValidationError('Package repository directories must not be symbolic links.', code='invalid_package_path')
    return path


def pkgbuild_repos_host_path(name):
    pkgbuild_repos_path(name)
    return os.path.join(settings.PKGBUILDREPOS_HOST_PATH, name)
