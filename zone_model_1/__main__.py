# coding:utf-8
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from zone_model_1.common.config import cfg
from zone_model_1.main_window import MainWindow

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--execute',
        help='Automatically execute all widgets in the input file. Require filepath.',
        action='store_true')
    parser.add_argument(
        '--qianjishen',
        help=argparse.SUPPRESS,  # Run in debug mode
        action='store_true')
    parser.add_argument(
        'filepath', type=str, nargs='?', help='Full input path in *.fse format', default=None)

    args = parser.parse_args()

    # enable dpi scale
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    app.aboutToQuit.connect(app.deleteLater)

    # internationalization
    # locale = cfg.get(cfg.language).value
    # translator = FluentTranslator(locale)
    # galleryTranslator = QTranslator()
    # galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

    # app.installTranslator(translator)
    # app.installTranslator(galleryTranslator)

    # create main window
    w = MainWindow(debug=args.qianjishen)
    w.show()

    sys.exit(app.exec())
