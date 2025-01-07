from typing import Union

from PySide6 import QtCore, QtWidgets, QtGui
from qfluentwidgets import (
    SettingCardGroup, SwitchSettingCard, OptionsSettingCard, HyperlinkCard, PrimaryPushSettingCard,
    PushSettingCard, ScrollArea, ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard, InfoBar, setTheme,
    setThemeColor, SettingCard, OptionsConfigItem, qconfig, FluentIcon, LineEdit, TitleLabel, PlainTextEdit
)

from zone_model_1.common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from zone_model_1.common.style_sheet import StyleSheet
from zone_model_1.project_info import __display_name__


class LineEditSettingCard(SettingCard):
    """ Setting card with a combo box """

    def __init__(
            self, config_item: OptionsConfigItem, icon: Union[str, QtGui.QIcon, FluentIcon], title, content=None,
            parent=None
    ):
        super().__init__(icon, title, content, parent)
        self.config_item = config_item
        self.line_edit = LineEdit(self)
        self.line_edit.setFixedWidth(300)
        self.hBoxLayout.addWidget(self.line_edit, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.line_edit.setText(qconfig.get(config_item))
        self.line_edit.editingFinished.connect(self._handle_text_changed)
        config_item.valueChanged.connect(self.setValue)

    @QtCore.Slot()
    def _handle_text_changed(self):
        qconfig.set(self.config_item, self.line_edit.text())

    def setValue(self, value):
        self.line_edit.setText(value)
        qconfig.set(self.config_item, value)


class PasswordLineEditSettingCard(SettingCard):
    """ Setting card with a combo box """

    def __init__(self, config_item: OptionsConfigItem, icon: Union[str, QtGui.QIcon, FluentIcon], title, content=None,
                 parent=None):
        super().__init__(icon, title, content, parent)
        self.config_item = config_item
        self.password_line_edit = PlainTextEdit(self)
        self.password_line_edit.setFixedWidth(330)
        self.hBoxLayout.addWidget(self.password_line_edit, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.setContentsMargins(16, 10, 10, 10)
        self.hBoxLayout.addSpacing(16)
        self.password_line_edit.setPlainText(qconfig.get(config_item))
        self.password_line_edit.textChanged.connect(self._handle_text_changed)
        self.setMinimumHeight(87)
        config_item.valueChanged.connect(self.setValue)

    @QtCore.Slot()
    def _handle_text_changed(self):
        try:
            self.config_item.blockSignals(True)
            qconfig.set(self.config_item, self.password_line_edit.toPlainText())
        finally:
            self.config_item.blockSignals(False)

    def setValue(self, value):
        self.password_line_edit.setPlainText(value)
        qconfig.set(self.config_item, value)


class SettingInterface(ScrollArea):
    """ Setting interface """
    update_knack_docs_database_finished = QtCore.Signal()
    update_knack_team_database_finished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.worker_employee_data = None
        self.worker_templates_data = None
        self.state_tool_tip_for_database_download = None
        self.w_scroll = QtWidgets.QWidget()
        self.expand_layout = ExpandLayout(self.w_scroll)

        # setting label
        self.setting_label = TitleLabel("Settings", self)

        self.openai_account_group = SettingCardGroup('OpenAI API', self.w_scroll)
        self.openai_api_key_card = PasswordLineEditSettingCard(
            cfg.openai_api_key, '', 'API Key', 'API key to access GPT models from OpenAI'
        )
        self.openai_account_group.addSettingCard(self.openai_api_key_card)

        # database
        self.database_group = SettingCardGroup('Database', self.w_scroll)
        self.database_auto_update_card = SwitchSettingCard(
            FluentIcon.UPDATE, 'Update Database',
            'Check for updates when application starts',
            cfg.database_auto_update,
        )
        self.database_reset = PushSettingCard(
            'Reset', '', 'Database Manual Reset & Download',
            f'Manually reset cached report template data and download from server (last updated: {cfg.database_docs_last_update.value})'
        )
        self.database_group.addSettingCard(self.database_auto_update_card)
        self.database_group.addSettingCard(self.database_reset)

        # personalization
        self.personal_group = SettingCardGroup('Preferences', self.w_scroll)
        self.theme_card = OptionsSettingCard(
            cfg.themeMode, FluentIcon.BRUSH, self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[self.tr('Light'), self.tr('Dark'), self.tr('Use system setting')],
            parent=self.personal_group
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor, FluentIcon.PALETTE, self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personal_group
        )
        self.zoom_card = OptionsSettingCard(
            cfg.dpiScale, FluentIcon.ZOOM, self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("Use system setting")],
            parent=self.personal_group
        )
        self.language_card = ComboBoxSettingCard(
            cfg.language, FluentIcon.LANGUAGE, self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English (UK)', self.tr('Use system setting')],
            parent=self.personal_group
        )
        self.language_card.hide()

        # update software
        self.update_software_group = SettingCardGroup(self.tr("Update"), self.w_scroll)
        self.update_on_start_card = SwitchSettingCard(
            FluentIcon.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.update_software_group
        )
        self.update_on_start_card.setChecked(False)
        self.update_on_start_card.setDisabled(True)

        # application
        self.about_group = SettingCardGroup(self.tr('About'), self.w_scroll)
        self.help_card = HyperlinkCard(
            HELP_URL, self.tr('Open help page'), FluentIcon.HELP, self.tr('Help'),
            self.tr(F'Discover new features and learn useful tips about {__display_name__}'),
            self.about_group
        )
        self.feedback_card = PrimaryPushSettingCard(
            self.tr('Provide feedback'), FluentIcon.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr(f'Help us improve {__display_name__} by providing feedback'),
            self.about_group
        )

        self.about_card = PrimaryPushSettingCard(
            self.tr('Check update'), FluentIcon.INFO, self.tr('About'),
            # '© ' + self.tr('Copyright ') +
            (f"{YEAR}, {AUTHOR}. "
             f"{self.tr('Version')} {VERSION}"),
            self.about_group
        )

        self.update_software_group.hide()
        self.update_on_start_card.hide()
        self.about_card.button.hide()
        self.help_card.hide()
        self.feedback_card.hide()

        self.__init_widget()

        # self.handle_update_knack_team_database_requested()
        # self.handle_update_knack_docs_database_requested()

    def __init_widget(self):
        self.resize(1000, 800)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.w_scroll)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.w_scroll.setObjectName('scrollWidget')
        self.setting_label.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__init_layout()
        self.__connect_signal_to_slot()

    def __init_layout(self):
        self.setting_label.move(36, 30)

        # add cards to group
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.zoom_card)
        self.personal_group.addSettingCard(self.language_card)

        self.update_software_group.addSettingCard(self.update_on_start_card)

        self.about_group.addSettingCard(self.help_card)
        self.about_group.addSettingCard(self.feedback_card)
        self.about_group.addSettingCard(self.about_card)

        # add setting card group to layout
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(36, 10, 36, 0)
        self.expand_layout.addWidget(self.openai_account_group)
        self.expand_layout.addWidget(self.database_group)
        self.expand_layout.addWidget(self.personal_group)
        self.expand_layout.addWidget(self.update_software_group)
        self.expand_layout.addWidget(self.about_group)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'), self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    @QtCore.Slot()
    def __handle_download_folder_card_clicked(self):
        """ download folder card clicked slot """
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), "/")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)  # self.downloadFolderCard.setContent(folder)

    def __connect_signal_to_slot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # personalization
        self.theme_card.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.theme_color_card.colorChanged.connect(lambda c: setThemeColor(c))

        # about
        self.feedback_card.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(FEEDBACK_URL)))
