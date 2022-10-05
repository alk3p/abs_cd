import os
import shutil
import logging
import glob
import subprocess
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from cd_manager.alpm import ALPMHelper
from cd_manager.recursion_helper import Recursionlimit
from makepkg.makepkg import PackageSystem
from datetime import timedelta
from git import Repo
from git.exc import GitCommandError


logger = logging.getLogger(__name__)

REPO_REMOVE_BIN = "/usr/bin/repo-remove"


class Package(models.Model):
    BuildStatus = models.TextChoices(
        'BuildStatus', 'SUCCESS FAILED NOT_BUILT BUILDING')
    name = models.CharField(max_length=100, primary_key=True)
    version = models.CharField(max_length=80)
    desc = models.TextField(null=True, blank=True)
    repo_url = models.CharField(max_length=100)
    build_status = models.CharField(choices=BuildStatus.choices,
                                    default='NOT_BUILT', max_length=10)
    build_date = models.DateTimeField(null=True, blank=True)
    build_output = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def pkgbuild_repo_status_check(self):
        # Returns True if repo changed
        package_src = os.path.join(settings.PKGBUILDREPOS_PATH, self.name)
        if not os.path.exists(package_src):
            Repo.clone_from(self.repo_url, package_src)
            return True
        else:
            def redownload():
                shutil.rmtree(package_src)
                return self.pkgbuild_repo_status_check()

            try:
                repo = Repo(path=package_src)
                assert not repo.bare
                remote = repo.remote("origin")
                assert remote.exists()
                matched_url = None
                for url in remote.urls:
                    if url == self.repo_url:
                        matched_url = url
                assert matched_url
                head_before = repo.head.object.hexsha
                remote.pull()
                if head_before != repo.head.object.hexsha:
                    return True
            except AssertionError:
                return redownload()
            except GitCommandError as e:
                logger.warning(package_src + "\n" + e.stderr)
                return redownload()
        return False

    def run_cd(self):
        self.pkgbuild_repo_status_check()
        PackageSystem().build(self)

    def build(self, force_rebuild=False, built_packages=[], repo_status_check=True):
        # As the dependency graph is not necessarily acyclic we have to make sure to check each node
        # only once. Otherwise this might end up in an endless loop (meaning we will hit the
        # recursion limit)
        if self.name in built_packages:
            return built_packages
        built_packages.append(self.name)

        if repo_status_check:
            self.pkgbuild_repo_status_check()
        deps = ALPMHelper().get_deps(pkgname=self.name, rundeps=True, makedeps=True)
        with Recursionlimit(2000):
            for wanted_dep in deps:
                wanted_dep = ALPMHelper.parse_dep_req(wanted_dep)
                query = Package.objects.filter(name__icontains=wanted_dep.name)
                if len(query) == 0:
                    continue
                dep_pkgobj = None
                for potdep in query:
                    potdep.pkgbuild_repo_status_check()  # For case only latest version of potdep satifies wanted_dep
                    if ALPMHelper.satifies_ver_req(wanted_dep, potdep.name):
                        dep_pkgobj = potdep
                        logger.debug(f"{potdep.name} satifies dependency requirement {wanted_dep.depends_entry} \
                                       of {self.name}.")
                        break
                if not dep_pkgobj:
                    logger.debug(f"No package satisfiying {wanted_dep.depends_entry} in local database. \
                                   Trying next dependency of {self.name}")
                    continue
                one_week_ago = timezone.now() - timedelta(days=7)
                if dep_pkgobj.build_status != 'SUCCESS' or \
                   dep_pkgobj.build_date < one_week_ago or \
                   force_rebuild:
                    built_packages = dep_pkgobj.build(force_rebuild=force_rebuild, built_packages=built_packages,
                                                      repo_status_check=False)
                else:
                    logger.info(
                        f"Successful build of dependency {dep_pkgobj.name} is newer than 7 days. Skipping rebuild.")
        self.run_cd()
        return built_packages

    def rebuildtree(self, built_packages=[]):
        self.build(force_rebuild=True, built_packages=built_packages)


@receiver(pre_delete, sender=Package)
def remove_pkgbuild_and_archpkg(sender, instance, using, **kwargs):
    package_src = os.path.join(settings.PKGBUILDREPOS_PATH, instance.name)
    if os.path.exists(package_src):
        srcinfo = ALPMHelper.get_srcinfo(instance.name).getcontent()
        packages = srcinfo['pkgname']
        pkg_version = srcinfo['pkgver'] + '-' + srcinfo['pkgrel']
        if 'epoch' in srcinfo:
            pkg_version = srcinfo['epoch'] + ':' + pkg_version
        logger.debug(f"Removing git repo of {instance.name}: {package_src}")
        shutil.rmtree(package_src)
    else:
        packages = [instance.name]
        pkg_version = None
    for pkg in packages:
        try:
            logger.debug(f"Trying to remove {pkg} from local repo database")
            repo_add_output = subprocess.run([REPO_REMOVE_BIN, '-q', '-R', 'abs_cd-local.db.tar.zst', pkg],
                                             stderr=subprocess.PIPE, cwd=settings.PACMANREPO_PATH) \
                                             .stderr.decode('UTF-8').strip('\n')
            if repo_add_output:
                logger.warning(repo_add_output)
        except subprocess.CalledProcessError as e:
            logger.warning(e.sdout + "\n This is itentional if the package was never built.")
        if pkg_version:
            for file in glob.iglob(f"/repo/{pkg}-{pkg_version}-*.pkg.tar.*"):
                logger.debug(f"Deleting {file}")
                os.remove(file)
