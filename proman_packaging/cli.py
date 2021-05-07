# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

# import atexit
import json
import logging
import os
import site
from typing import Optional
from urllib.parse import urljoin

from distlib.locators import PyPIJSONLocator

from . import config as cfg
from .config import Config
from .distributions import LocalDistributionPath, show_package_metadata
from .package_manager import PackageManager
from .source_tree import LockManager, SourceTreeManager

logger = logging.getLogger(__name__)

# Load configuration files
source_tree_cfg = Config(filepath=cfg.pyproject_path, writable=True)
lock_cfg = Config(filepath=cfg.lock_path, writable=True)

# Load source trees
source_tree_mgr = SourceTreeManager(source_tree_cfg)
lock_mgr = LockManager(lock_cfg)

print(site.ENABLE_USER_SITE)
print(site.USER_SITE)
print(site.USER_BASE)
print(site.getusersitepackages())

# Setup distribution paths
local_distribution = LocalDistributionPath()
local_distribution.create_pypackages_pth()
# local_distribution.load_pypackages()

# TODO: is ephemeral pkgutil or site load with cleanup on exit
# atexit.register(local_distribution.remove_path)

# TODO setup proxy capability
# setup repository
locator = PyPIJSONLocator(urljoin(cfg.INDEX_URL, 'pypi'))

# Setup package manager
package_manager = PackageManager(
    source_tree=source_tree_mgr,
    lock=lock_mgr,
    distribution=local_distribution,
    locator=locator,
    force=False,
    update=False,
    options={}
)


def init(name: str) -> None:
    '''Initialize a new project.'''
    if not os.path.isfile(source_tree_cfg.filepath):
        source_tree_cfg['tool'] = {
            'proman': {
                'authors': ['Jesse P. Johnson'],
                'name': name,
                'description': 'Description for the project',
                'version': '0.1.0',
                'dependencies': {},
                'dev-dependencies': {}
            }
            # 'build-system': {
            #     'requires': ["build"],
            #     'build-backend': 'build.api:main'
            # }
        }
        source_tree_cfg.dump(writable=True)
    else:
        print('project is already initialized')


def info(name: str, output: str = None) -> None:
    '''Get package info.'''
    info = package_manager.get_package_info(name)
    print(json.dumps(info, indent=2))


def download(name: str, dest: str = '.') -> None:
    '''Download packages.'''
    package_manager.download_package(name, dest)


def install(
    name: Optional[str],
    dev: bool = False,
    python: Optional[str] = None,
    platform: Optional[str] = None,
    optional: bool = False,
    prerelease: bool = False,
) -> None:
    '''Install package and dependencies.

    Parameters
    ----------
    name: str
        name of package to be installed
    dev: bool
        add package as a development dependency
    python: str
        version of Python allowed
    prerelease: bool
        allow prerelease version of package
    optional: bool
        optional package that is not required
    platform: str
        restrict package to specific platform

    '''
    if name and name.startswith('-'):
        print('error: not a valid install argument')
    else:
        package_manager.install(
            name, dev, python, platform, optional, prerelease
        )


def uninstall(name: Optional[str]) -> None:
    '''Uninstall packages.'''
    if name and name.startswith('-'):
        print('error: not a valid install argument')
    else:
        package_manager.uninstall(name)


def upgrade(
    name: Optional[str],
    force: bool = False,
) -> None:
    '''Install package and dependencies.

    Parameters
    ----------
    name: str
        name of package to be installed
    force: bool
        force changes

    '''
    if name and name.startswith('-'):
        print('error: not a valid install argument')
    else:
        package_manager.upgrade(name, force)


def list(versions: bool = True) -> None:
    '''List installed packages.'''
    if versions:
        for k in local_distribution.packages:
            print(k.name.ljust(25), k.version.ljust(15))
    else:
        print('\n'.join(local_distribution.package_names))


def show(name: str) -> None:
    '''Show information about installed packages.'''
    for key, val in show_package_metadata(name).items():
        print("{k} {v}".format(k=key, v=val))


# def check() -> None:
#     '''Verify installed packages have compatible dependencies.'''
#     pass


def config() -> None:
    '''Manage distributions and global configuration.'''
    ...


def search(
    name: str,
    version: Optional[str] = None,
    stable_version: Optional[str] = None,
    author: Optional[str] = None,
    author_email: Optional[str] = None,
    maintainer: Optional[str] = None,
    maintainer_email: Optional[str] = None,
    home_page: Optional[str] = None,
    license: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    platform: Optional[str] = None,
    download_url: Optional[str] = None,
    classifiers: Optional[str] = None,
    project_url: Optional[str] = None,
    docs_url: Optional[str] = None,
    operation: Optional[str] = None,
) -> None:
    '''Search PyPI for packages.'''
    packages = package_manager.search(
        query={
            'name': name,
            'version': version,
            'stable_version': stable_version,
            'author': author,
            'author_email': author_email,
            'maintainer': maintainer,
            'maintainer_email': maintainer_email,
            'home_page': home_page,
            'license': license,
            'summary': summary,
            'description': description,
            'keywords': keywords,
            'platform': platform,
            'download_url': download_url,
            'classifiers': classifiers,
            'project_url': project_url,
            'docs_url': docs_url,
        },
        operation=operation,
    )
    for package in packages:
        print(
            package['name'].ljust(25),  # type: ignore
            package['version'].ljust(15),  # type: ignore
            package['summary'],  # type: ignore
        )


# def build() -> None:
#     '''Build wheels from your requirements.'''
#     pass
