# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tandem_view.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Tandem_View(object):
    def setupUi(self, Tandem_View):
        if not Tandem_View.objectName():
            Tandem_View.setObjectName(u"Tandem_View")
        Tandem_View.resize(290, 502)
        Tandem_View.setMinimumSize(QSize(290, 290))
        Tandem_View.setMaximumSize(QSize(290, 16777215))
        Tandem_View.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(Tandem_View)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.layout_tandem_channel = QHBoxLayout()
        self.layout_tandem_channel.setObjectName(u"layout_tandem_channel")
        self.label_tandem_channel = QLabel(Tandem_View)
        self.label_tandem_channel.setObjectName(u"label_tandem_channel")
        self.label_tandem_channel.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.layout_tandem_channel.addWidget(self.label_tandem_channel)

        self.cb_tandem_channel = QComboBox(Tandem_View)
        self.cb_tandem_channel.setObjectName(u"cb_tandem_channel")
        self.cb_tandem_channel.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")

        self.layout_tandem_channel.addWidget(self.cb_tandem_channel)


        self.verticalLayout_5.addLayout(self.layout_tandem_channel)

        self.label_tandem_channel_warning = QLabel(Tandem_View)
        self.label_tandem_channel_warning.setObjectName(u"label_tandem_channel_warning")
        self.label_tandem_channel_warning.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.label_tandem_channel_warning.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.label_tandem_channel_warning)

        self.ab = QTabWidget(Tandem_View)
        self.ab.setObjectName(u"ab")
        self.ab.setMinimumSize(QSize(0, 290))
        self.ab.setStyleSheet(u"QTabWidget::pane {\n"
"	border: 1px solid rgb(199, 219, 237); /* visible border */\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background: rgb(235, 235, 235);\n"
"    padding: 5px;\n"
"	color: rgb(0, 0, 0); /* black text */\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background: white;\n"
"}\n"
"\n"
"QTabBar::tab:!selected {\n"
"    margin-top: 2px; /* makes selected tab look connected */\n"
"}\n"
"")
        self.Import = QWidget()
        self.Import.setObjectName(u"Import")
        self.verticalLayout_3 = QVBoxLayout(self.Import)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(10, 10, 10, 10)
        self.btn_import = QPushButton(self.Import)
        self.btn_import.setObjectName(u"btn_import")
        self.btn_import.setMinimumSize(QSize(100, 33))
        self.btn_import.setMaximumSize(QSize(16777215, 16777215))
        self.btn_import.setStyleSheet(u"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_import)

        self.btn_clear_import = QPushButton(self.Import)
        self.btn_clear_import.setObjectName(u"btn_clear_import")
        self.btn_clear_import.setMinimumSize(QSize(100, 33))
        self.btn_clear_import.setMaximumSize(QSize(16777215, 16777215))
        self.btn_clear_import.setStyleSheet(u"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_clear_import)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(self.Import)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(70, 25))
        self.label_2.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.sb_height_offset = QDoubleSpinBox(self.Import)
        self.sb_height_offset.setObjectName(u"sb_height_offset")
        self.sb_height_offset.setMinimumSize(QSize(20, 0))
        self.sb_height_offset.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_height_offset.setMinimum(-100.000000000000000)
        self.sb_height_offset.setMaximum(100.000000000000000)

        self.gridLayout_2.addWidget(self.sb_height_offset, 0, 1, 1, 1)

        self.label = QLabel(self.Import)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        self.tandem_rotation = QDoubleSpinBox(self.Import)
        self.tandem_rotation.setObjectName(u"tandem_rotation")
        self.tandem_rotation.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.tandem_rotation.setMinimum(-360.000000000000000)
        self.tandem_rotation.setMaximum(360.000000000000000)

        self.gridLayout_2.addWidget(self.tandem_rotation, 1, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.btn_apply_import = QPushButton(self.Import)
        self.btn_apply_import.setObjectName(u"btn_apply_import")
        self.btn_apply_import.setEnabled(True)
        self.btn_apply_import.setMinimumSize(QSize(0, 33))
        self.btn_apply_import.setMaximumSize(QSize(3000, 33))
        self.btn_apply_import.setStyleSheet(u"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}")

        self.verticalLayout_3.addWidget(self.btn_apply_import)

        self.label_5 = QLabel(self.Import)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")
        self.label_5.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.ab.addTab(self.Import, "")
        self.Generate = QWidget()
        self.Generate.setObjectName(u"Generate")
        self.verticalLayout_6 = QVBoxLayout(self.Generate)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.label_7 = QLabel(self.Generate)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)

        self.sb_tandem_height = QDoubleSpinBox(self.Generate)
        self.sb_tandem_height.setObjectName(u"sb_tandem_height")
        self.sb_tandem_height.setStyleSheet(u"background-color: rgb(255, 255, 250);\n"
"color: rgb(0, 0, 0);")
        self.sb_tandem_height.setDecimals(3)
        self.sb_tandem_height.setMinimum(10.000000000000000)
        self.sb_tandem_height.setMaximum(500.000000000000000)
        self.sb_tandem_height.setValue(10.000000000000000)

        self.gridLayout.addWidget(self.sb_tandem_height, 0, 1, 1, 1)

        self.label_8 = QLabel(self.Generate)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)

        self.sp_channel_diameter = QDoubleSpinBox(self.Generate)
        self.sp_channel_diameter.setObjectName(u"sp_channel_diameter")
        self.sp_channel_diameter.setMaximumSize(QSize(16777215, 16777215))
        self.sp_channel_diameter.setStyleSheet(u"background-color: rgb(255, 255, 250);\n"
"color: rgb(0, 0, 0);")
        self.sp_channel_diameter.setDecimals(3)
        self.sp_channel_diameter.setMinimum(0.500000000000000)

        self.gridLayout.addWidget(self.sp_channel_diameter, 1, 1, 1, 1)

        self.label_4 = QLabel(self.Generate)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.sp_stopper_diameter = QDoubleSpinBox(self.Generate)
        self.sp_stopper_diameter.setObjectName(u"sp_stopper_diameter")
        self.sp_stopper_diameter.setStyleSheet(u"background-color: rgb(255, 255, 250);\n"
"color: rgb(0, 0, 0);")
        self.sp_stopper_diameter.setDecimals(3)
        self.sp_stopper_diameter.setMinimum(0.500000000000000)

        self.gridLayout.addWidget(self.sp_stopper_diameter, 2, 1, 1, 1)

        self.label_12 = QLabel(self.Generate)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_12, 3, 0, 1, 1)

        self.sp_bend_angle = QDoubleSpinBox(self.Generate)
        self.sp_bend_angle.setObjectName(u"sp_bend_angle")
        self.sp_bend_angle.setStyleSheet(u"background-color: rgb(255, 255, 250);\n"
"color: rgb(0, 0, 0);")
        self.sp_bend_angle.setDecimals(3)

        self.gridLayout.addWidget(self.sp_bend_angle, 3, 1, 1, 1)

        self.label_6 = QLabel(self.Generate)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.sb_bend_radius = QDoubleSpinBox(self.Generate)
        self.sb_bend_radius.setObjectName(u"sb_bend_radius")
        self.sb_bend_radius.setStyleSheet(u"background-color: rgb(255, 255, 250);\n"
"color: rgb(0, 0, 0);")
        self.sb_bend_radius.setDecimals(3)
        self.sb_bend_radius.setMinimum(10.000000000000000)
        self.sb_bend_radius.setMaximum(1000.000000000000000)

        self.gridLayout.addWidget(self.sb_bend_radius, 4, 1, 1, 1)

        self.label_9 = QLabel(self.Generate)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMinimumSize(QSize(0, 18))
        self.label_9.setMaximumSize(QSize(16777215, 18))
        self.label_9.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_9, 5, 0, 1, 1)

        self.sb_threading_depth = QDoubleSpinBox(self.Generate)
        self.sb_threading_depth.setObjectName(u"sb_threading_depth")
        self.sb_threading_depth.setMinimumSize(QSize(20, 0))
        self.sb_threading_depth.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_threading_depth.setDecimals(3)
        self.sb_threading_depth.setMaximum(350.000000000000000)

        self.gridLayout.addWidget(self.sb_threading_depth, 5, 1, 1, 1)

        self.label_10 = QLabel(self.Generate)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(0, 18))
        self.label_10.setMaximumSize(QSize(16777215, 18))
        self.label_10.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_10, 6, 0, 1, 1)

        self.sb_threading_diameter = QDoubleSpinBox(self.Generate)
        self.sb_threading_diameter.setObjectName(u"sb_threading_diameter")
        self.sb_threading_diameter.setMinimumSize(QSize(20, 0))
        self.sb_threading_diameter.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_threading_diameter.setDecimals(3)
        self.sb_threading_diameter.setMaximum(350.000000000000000)

        self.gridLayout.addWidget(self.sb_threading_diameter, 6, 1, 1, 1)

        self.label_3 = QLabel(self.Generate)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)

        self.tandem_rotation_2 = QDoubleSpinBox(self.Generate)
        self.tandem_rotation_2.setObjectName(u"tandem_rotation_2")
        self.tandem_rotation_2.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.tandem_rotation_2.setDecimals(3)
        self.tandem_rotation_2.setMinimum(-360.000000000000000)
        self.tandem_rotation_2.setMaximum(360.000000000000000)

        self.gridLayout.addWidget(self.tandem_rotation_2, 7, 1, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout)

        self.btn_apply = QPushButton(self.Generate)
        self.btn_apply.setObjectName(u"btn_apply")
        self.btn_apply.setMinimumSize(QSize(240, 33))
        self.btn_apply.setMaximumSize(QSize(16777215, 16777215))
        self.btn_apply.setStyleSheet(u"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}")

        self.verticalLayout_6.addWidget(self.btn_apply)

        self.btn_clear_generate = QPushButton(self.Generate)
        self.btn_clear_generate.setObjectName(u"btn_clear_generate")
        self.btn_clear_generate.setMinimumSize(QSize(240, 33))
        self.btn_clear_generate.setMaximumSize(QSize(16777215, 16777215))
        self.btn_clear_generate.setStyleSheet(u"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}")

        self.verticalLayout_6.addWidget(self.btn_clear_generate)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

        self.ab.addTab(self.Generate, "")

        self.verticalLayout_5.addWidget(self.ab)


        self.retranslateUi(Tandem_View)

        self.ab.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Tandem_View)
    # setupUi

    def retranslateUi(self, Tandem_View):
        Tandem_View.setWindowTitle(QCoreApplication.translate("Tandem_View", u"Form", None))
        self.label_tandem_channel.setText(QCoreApplication.translate("Tandem_View", u"Tandem Channel", None))
        self.btn_import.setText(QCoreApplication.translate("Tandem_View", u"Import", None))
        self.btn_clear_import.setText(QCoreApplication.translate("Tandem_View", u"Clear Tandem", None))
        self.label_2.setText(QCoreApplication.translate("Tandem_View", u"Height Offset", None))
        self.sb_height_offset.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label.setText(QCoreApplication.translate("Tandem_View", u"Rotation", None))
        self.tandem_rotation.setSuffix(QCoreApplication.translate("Tandem_View", u"\u00b0", None))
        self.btn_apply_import.setText(QCoreApplication.translate("Tandem_View", u"Apply Import Settings", None))
        self.label_5.setText(QCoreApplication.translate("Tandem_View", u"Model Filepath: None", None))
        self.ab.setTabText(self.ab.indexOf(self.Import), QCoreApplication.translate("Tandem_View", u"Import", None))
        self.label_7.setText(QCoreApplication.translate("Tandem_View", u"Tandem Height", None))
        self.sb_tandem_height.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_8.setText(QCoreApplication.translate("Tandem_View", u"Channel Diameter", None))
        self.sp_channel_diameter.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_4.setText(QCoreApplication.translate("Tandem_View", u"Stopper Diameter", None))
        self.sp_stopper_diameter.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_12.setText(QCoreApplication.translate("Tandem_View", u"Bend Angle", None))
        self.sp_bend_angle.setSuffix(QCoreApplication.translate("Tandem_View", u"\u00b0", None))
        self.label_6.setText(QCoreApplication.translate("Tandem_View", u"Bend Radius", None))
        self.sb_bend_radius.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_9.setText(QCoreApplication.translate("Tandem_View", u"Threading Depth", None))
        self.sb_threading_depth.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_10.setText(QCoreApplication.translate("Tandem_View", u"Threading Diameter", None))
        self.sb_threading_diameter.setSuffix(QCoreApplication.translate("Tandem_View", u" mm", None))
        self.label_3.setText(QCoreApplication.translate("Tandem_View", u"Rotation", None))
        self.tandem_rotation_2.setSuffix(QCoreApplication.translate("Tandem_View", u"\u00b0", None))
        self.btn_apply.setText(QCoreApplication.translate("Tandem_View", u"Generate Tandem", None))
        self.btn_clear_generate.setText(QCoreApplication.translate("Tandem_View", u"Clear Tandem", None))
        self.ab.setTabText(self.ab.indexOf(self.Generate), QCoreApplication.translate("Tandem_View", u"Generate", None))
    # retranslateUi

