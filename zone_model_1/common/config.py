# coding:utf-8
import sys
from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import (
    qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, OptionsValidator, Theme, ConfigSerializer,
)

from ..project_info import AppData, __version__


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    ENGLISH = QLocale(QLocale.Language.English, QLocale.Country.UnitedKingdom)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # folders
    # musicFolders = ConfigItem("Folders", "LocalMusic", [], FolderListValidator())
    # downloadFolder = ConfigItem("Folders", "Download", "app/download", FolderValidator())

    # main window
    # micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True
    )
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(),
        restart=True
    )

    # Material
    # blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())

    openai_api_key = ConfigItem('OpenAI', 'api_key', '')
    database_auto_update = ConfigItem('Database', 'auto_update', True, BoolValidator())
    database_team_last_update = ConfigItem('Database', 'team_last_update', 'never', )
    database_docs_last_update = ConfigItem('Database', 'docs_last_update', 'never', )

    office_location_index = ConfigItem('MainWindow', 'office_location_index', 0)


YEAR = 2024
AUTHOR = "Yan Fu"
VERSION = __version__
HELP_URL = "https://wiki.ofrconsultants.com"
REPO_URL = "https://wiki.ofrconsultants.com"
EXAMPLE_URL = "https://wiki.ofrconsultants.com"
FEEDBACK_URL = "https://wiki.ofrconsultants.com"
RELEASE_URL = "https://wiki.ofrconsultants.com"
ZH_SUPPORT_URL = "https://wiki.ofrconsultants.com"
EN_SUPPORT_URL = "https://wiki.ofrconsultants.com"

cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(AppData.config.path, cfg)
