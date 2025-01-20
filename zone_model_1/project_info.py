import logging
import pathlib
import sys
from enum import Enum
from os import path, getenv, makedirs

# make root directory of this app which will be used 1. when running the app; 2. pyinstaller at compiling the app.
__home__ = path.realpath(path.dirname(__file__))
while path.basename(__home__).lower() == path.basename(path.dirname(__home__)).lower():
    if len(__home__) == len(path.dirname(__home__)):
        raise ValueError
    else:
        __home__ = path.dirname(__home__)

# setup logger
logger = logging.getLogger('gui')
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(
    logging.Formatter(fmt='{levelname:5.5s} [{module:5.5s}:{lineno:04d}] {message:s}', style='{'))
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)

__version__ = "0.1"
__display_name__ = "Zone Model 1"  # display name
__dev_name__ = "zone_model_1"  # dev name

if sys.platform == 'win32':
    _path_appdata = path.join(path.realpath(getenv('APPDATA')), __dev_name__)
elif sys.platform == 'linux':
    _path_appdata = path.join(path.expanduser('~'), 'local', 'share')
elif sys.platform == "darwin":
    _path_appdata = path.join(path.expanduser('~'), 'Library', 'Application Support', __dev_name__)
else:
    raise NotImplementedError('Unidentified platform. This program supports Windows, macOS and Linux.')

if not path.exists(_path_appdata):
    logger.debug(f'AppData path does not exist, making directory...')
    makedirs(_path_appdata)
else:
    logger.debug(f'AppData path: {_path_appdata}')


class AppData(Enum):
    config = 'config.json'
    employees = 'employees.json'
    case_studies = 'case_studies.json'
    database_docs = 'db_docs.json'
    dir_template_files = 'templates'
    dir_team_photos = 'team_photos'
    dir_case_study_photos = 'case_study_photos'

    work_packages = 'work_packages.json'
    work_packages_folder = 'work_packages'

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(_path_appdata) / self.value
