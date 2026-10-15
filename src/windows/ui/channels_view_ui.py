# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'channels_view.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QGroupBox, QLabel, QLayout,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Channels_View(object):
    def setupUi(self, Channels_View):
        if not Channels_View.objectName():
            Channels_View.setObjectName(u"Channels_View")
        Channels_View.resize(290, 328)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Channels_View.sizePolicy().hasHeightForWidth())
        Channels_View.setSizePolicy(sizePolicy)
        Channels_View.setMinimumSize(QSize(290, 290))
        Channels_View.setMaximumSize(QSize(290, 16777215))
        Channels_View.setStyleSheet(u"")
        self.verticalLayout_scroll = QVBoxLayout(Channels_View)
        self.verticalLayout_scroll.setObjectName(u"verticalLayout_scroll")
        self.verticalLayout_scroll.setContentsMargins(0, 0, 0, 0)
        self.scroll_channels = QScrollArea(Channels_View)
        self.scroll_channels.setObjectName(u"scroll_channels")
        self.scroll_channels.setStyleSheet(u"QScrollArea, QScrollArea > QWidget > QWidget {\n"
"	background: transparent;\n"
"}")
        self.scroll_channels.setFrameShape(QFrame.NoFrame)
        self.scroll_channels.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_channels.setWidgetResizable(True)
        self.scroll_channels_contents = QWidget()
        self.scroll_channels_contents.setObjectName(u"scroll_channels_contents")
        self.verticalLayout = QVBoxLayout(self.scroll_channels_contents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 10, 5, 5)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.label_4 = QLabel(self.scroll_channels_contents)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(108, 18))
        self.label_4.setMaximumSize(QSize(16777215, 18))
        self.label_4.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.spinbox_diameter = QDoubleSpinBox(self.scroll_channels_contents)
        self.spinbox_diameter.setObjectName(u"spinbox_diameter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(2)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.spinbox_diameter.sizePolicy().hasHeightForWidth())
        self.spinbox_diameter.setSizePolicy(sizePolicy2)
        self.spinbox_diameter.setMinimumSize(QSize(20, 0))
        self.spinbox_diameter.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_diameter.setDecimals(3)
        self.spinbox_diameter.setMinimum(0.300000000000000)

        self.gridLayout.addWidget(self.spinbox_diameter, 0, 1, 1, 1)

        self.label = QLabel(self.scroll_channels_contents)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMinimumSize(QSize(0, 18))
        self.label.setMaximumSize(QSize(16777215, 18))
        self.label.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.sb_needle_length = QDoubleSpinBox(self.scroll_channels_contents)
        self.sb_needle_length.setObjectName(u"sb_needle_length")
        sizePolicy2.setHeightForWidth(self.sb_needle_length.sizePolicy().hasHeightForWidth())
        self.sb_needle_length.setSizePolicy(sizePolicy2)
        self.sb_needle_length.setMinimumSize(QSize(20, 0))
        self.sb_needle_length.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_needle_length.setDecimals(3)
        self.sb_needle_length.setMaximum(350.000000000000000)

        self.gridLayout.addWidget(self.sb_needle_length, 1, 1, 1, 1)

        self.label_2 = QLabel(self.scroll_channels_contents)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(0, 18))
        self.label_2.setMaximumSize(QSize(16777215, 18))
        self.label_2.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.sb_threading_dept = QDoubleSpinBox(self.scroll_channels_contents)
        self.sb_threading_dept.setObjectName(u"sb_threading_dept")
        sizePolicy2.setHeightForWidth(self.sb_threading_dept.sizePolicy().hasHeightForWidth())
        self.sb_threading_dept.setSizePolicy(sizePolicy2)
        self.sb_threading_dept.setMinimumSize(QSize(20, 0))
        self.sb_threading_dept.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_threading_dept.setDecimals(3)
        self.sb_threading_dept.setMaximum(350.000000000000000)

        self.gridLayout.addWidget(self.sb_threading_dept, 2, 1, 1, 1)

        self.label_3 = QLabel(self.scroll_channels_contents)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(0, 18))
        self.label_3.setMaximumSize(QSize(16777215, 18))
        self.label_3.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.sb_threading_diameter = QDoubleSpinBox(self.scroll_channels_contents)
        self.sb_threading_diameter.setObjectName(u"sb_threading_diameter")
        sizePolicy2.setHeightForWidth(self.sb_threading_diameter.sizePolicy().hasHeightForWidth())
        self.sb_threading_diameter.setSizePolicy(sizePolicy2)
        self.sb_threading_diameter.setMinimumSize(QSize(20, 0))
        self.sb_threading_diameter.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.sb_threading_diameter.setDecimals(3)
        self.sb_threading_diameter.setMaximum(350.000000000000000)

        self.gridLayout.addWidget(self.sb_threading_diameter, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.btn_apply_settings = QPushButton(self.scroll_channels_contents)
        self.btn_apply_settings.setObjectName(u"btn_apply_settings")
        sizePolicy2.setHeightForWidth(self.btn_apply_settings.sizePolicy().hasHeightForWidth())
        self.btn_apply_settings.setSizePolicy(sizePolicy2)
        self.btn_apply_settings.setMinimumSize(QSize(20, 33))
        self.btn_apply_settings.setMaximumSize(QSize(16777215, 16777215))
        self.btn_apply_settings.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout.addWidget(self.btn_apply_settings)

        self.label_5 = QLabel(self.scroll_channels_contents)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(10, 13))
        self.label_5.setMaximumSize(QSize(270, 13))
        self.label_5.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.verticalLayout.addWidget(self.label_5)

        self.listwidget_channels = QListWidget(self.scroll_channels_contents)
        self.listwidget_channels.setObjectName(u"listwidget_channels")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(2)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.listwidget_channels.sizePolicy().hasHeightForWidth())
        self.listwidget_channels.setSizePolicy(sizePolicy3)
        self.listwidget_channels.setMinimumSize(QSize(251, 50))
        self.listwidget_channels.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([u"MS Shell Dlg 2"])
        font.setPointSize(8)
        self.listwidget_channels.setFont(font)
        self.listwidget_channels.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.listwidget_channels.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.verticalLayout.addWidget(self.listwidget_channels)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SetFixedSize)
        self.btn_set_tandem = QPushButton(self.scroll_channels_contents)
        self.btn_set_tandem.setObjectName(u"btn_set_tandem")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(2)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_set_tandem.sizePolicy().hasHeightForWidth())
        self.btn_set_tandem.setSizePolicy(sizePolicy4)
        self.btn_set_tandem.setMinimumSize(QSize(240, 33))
        self.btn_set_tandem.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_4.addWidget(self.btn_set_tandem)

        self.btn_enable = QPushButton(self.scroll_channels_contents)
        self.btn_enable.setObjectName(u"btn_enable")
        sizePolicy4.setHeightForWidth(self.btn_enable.sizePolicy().hasHeightForWidth())
        self.btn_enable.setSizePolicy(sizePolicy4)
        self.btn_enable.setMinimumSize(QSize(240, 33))
        self.btn_enable.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_4.addWidget(self.btn_enable)


        self.verticalLayout.addLayout(self.verticalLayout_4)

        self.group_selected_channel = QGroupBox(self.scroll_channels_contents)
        self.group_selected_channel.setObjectName(u"group_selected_channel")
        self.group_selected_channel.setStyleSheet(u"QGroupBox, QLabel {\n"
"	color: rgb(0, 0, 0);\n"
"}\n"
"QDoubleSpinBox, QLineEdit, QComboBox {\n"
"	background-color: rgb(255, 255, 255);\n"
"	color: rgb(0, 0, 0);\n"
"}\n"
"QPushButton {\n"
"	color: rgb(0, 0, 0);\n"
"	background-color: rgb(199, 219, 237);\n"
"	border: 0px solid;\n"
"	min-height: 33px;\n"
"}\n"
"QPushButton:hover {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(48, 88, 162);\n"
"}\n"
"QPushButton:pressed {\n"
"	color: rgb(250,250,250);\n"
"	background-color: rgb(28, 44, 81);\n"
"}\n"
"QPushButton:disabled {\n"
"	color: rgb(150, 150, 150);\n"
"}")
        self.gridLayout_selected_channel = QGridLayout(self.group_selected_channel)
        self.gridLayout_selected_channel.setObjectName(u"gridLayout_selected_channel")
        self.label_channel_diameter = QLabel(self.group_selected_channel)
        self.label_channel_diameter.setObjectName(u"label_channel_diameter")

        self.gridLayout_selected_channel.addWidget(self.label_channel_diameter, 0, 0, 1, 1)

        self.sb_channel_diameter = QDoubleSpinBox(self.group_selected_channel)
        self.sb_channel_diameter.setObjectName(u"sb_channel_diameter")
        self.sb_channel_diameter.setDecimals(3)

        self.gridLayout_selected_channel.addWidget(self.sb_channel_diameter, 0, 1, 1, 1)

        self.btn_apply_channel_diameter = QPushButton(self.group_selected_channel)
        self.btn_apply_channel_diameter.setObjectName(u"btn_apply_channel_diameter")

        self.gridLayout_selected_channel.addWidget(self.btn_apply_channel_diameter, 1, 0, 1, 2)

        self.btn_clear_channel_diameter = QPushButton(self.group_selected_channel)
        self.btn_clear_channel_diameter.setObjectName(u"btn_clear_channel_diameter")

        self.gridLayout_selected_channel.addWidget(self.btn_clear_channel_diameter, 2, 0, 1, 2)

        self.le_template_name = QLineEdit(self.group_selected_channel)
        self.le_template_name.setObjectName(u"le_template_name")

        self.gridLayout_selected_channel.addWidget(self.le_template_name, 3, 0, 1, 1)

        self.btn_save_template = QPushButton(self.group_selected_channel)
        self.btn_save_template.setObjectName(u"btn_save_template")

        self.gridLayout_selected_channel.addWidget(self.btn_save_template, 3, 1, 1, 1)

        self.cb_needle_templates = QComboBox(self.group_selected_channel)
        self.cb_needle_templates.setObjectName(u"cb_needle_templates")

        self.gridLayout_selected_channel.addWidget(self.cb_needle_templates, 4, 0, 1, 1)

        self.btn_apply_template = QPushButton(self.group_selected_channel)
        self.btn_apply_template.setObjectName(u"btn_apply_template")

        self.gridLayout_selected_channel.addWidget(self.btn_apply_template, 4, 1, 1, 1)

        self.label_template_status = QLabel(self.group_selected_channel)
        self.label_template_status.setObjectName(u"label_template_status")
        self.label_template_status.setWordWrap(True)

        self.gridLayout_selected_channel.addWidget(self.label_template_status, 5, 0, 1, 2)


        self.verticalLayout.addWidget(self.group_selected_channel)

        self.scroll_channels.setWidget(self.scroll_channels_contents)

        self.verticalLayout_scroll.addWidget(self.scroll_channels)


        self.retranslateUi(Channels_View)

        QMetaObject.connectSlotsByName(Channels_View)
    # setupUi

    def retranslateUi(self, Channels_View):
        Channels_View.setWindowTitle(QCoreApplication.translate("Channels_View", u"Form", None))
        self.label_4.setText(QCoreApplication.translate("Channels_View", u"Channels Diameter", None))
        self.spinbox_diameter.setSuffix(QCoreApplication.translate("Channels_View", u" mm", None))
        self.label.setText(QCoreApplication.translate("Channels_View", u"Dead Space", None))
        self.sb_needle_length.setSuffix(QCoreApplication.translate("Channels_View", u" mm", None))
        self.label_2.setText(QCoreApplication.translate("Channels_View", u"Threading Depth", None))
        self.sb_threading_dept.setSuffix(QCoreApplication.translate("Channels_View", u" mm", None))
        self.label_3.setText(QCoreApplication.translate("Channels_View", u"Threading Diameter", None))
        self.sb_threading_diameter.setSuffix(QCoreApplication.translate("Channels_View", u" mm", None))
        self.btn_apply_settings.setText(QCoreApplication.translate("Channels_View", u"Apply", None))
        self.label_5.setText(QCoreApplication.translate("Channels_View", u"Channels", None))
        self.btn_set_tandem.setText(QCoreApplication.translate("Channels_View", u"Set as Tandem", None))
        self.btn_enable.setText(QCoreApplication.translate("Channels_View", u"Disable", None))
        self.group_selected_channel.setTitle(QCoreApplication.translate("Channels_View", u"Selected Channel", None))
        self.label_channel_diameter.setText(QCoreApplication.translate("Channels_View", u"Channel Diameter", None))
        self.sb_channel_diameter.setSuffix(QCoreApplication.translate("Channels_View", u" mm", None))
        self.btn_apply_channel_diameter.setText(QCoreApplication.translate("Channels_View", u"Apply to Channel", None))
        self.btn_clear_channel_diameter.setText(QCoreApplication.translate("Channels_View", u"Use Channels Diameter", None))
        self.le_template_name.setPlaceholderText(QCoreApplication.translate("Channels_View", u"Template name", None))
        self.btn_save_template.setText(QCoreApplication.translate("Channels_View", u"Save as Template", None))
        self.btn_apply_template.setText(QCoreApplication.translate("Channels_View", u"Apply Template", None))
    # retranslateUi

