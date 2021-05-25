import logging
from cd_manager.models import Package
from cd_manager.alpm import ALPMHelper


logger = logging.getLogger(__name__)


def check_for_new_commits():
    logger.info("Start checking for new commits in all repos.")
    try:
        for pkg in Package.objects.all():
            if pkg.pkgbuild_repo_status_check():
                pkg.build()
                # TODO: Speed up process by already excluding dependencies after pkg was built
    except BaseException:
        logger.exception("Cronjob checking for new commits in all repos failed:")


def update_pacmandbs():
    logger.info("Updating pacman databases.")
    ALPMHelper().update_syncdbs()
