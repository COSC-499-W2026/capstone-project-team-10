# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cylinder_view.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QLabel, QLayout, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Cylinder_View(object):
    def setupUi(self, Cylinder_View):
        if not Cylinder_View.objectName():
            Cylinder_View.setObjectName(u"Cylinder_View")
        Cylinder_View.resize(290, 376)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Cylinder_View.sizePolicy().hasHeightForWidth())
        Cylinder_View.setSizePolicy(sizePolicy)
        Cylinder_View.setMinimumSize(QSize(290, 290))
        Cylinder_View.setMaximumSize(QSize(16777215, 600))
        Cylinder_View.setStyleSheet(u"background-color: rgb(250,250,250);")
        self.verticalLayout = QVBoxLayout(Cylinder_View)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 10, 5, 5)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_units = QLabel(Cylinder_View)
        self.label_units.setObjectName(u"label_units")
        self.label_units.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_units, 5, 0, 1, 1)

        self.combobox_units = QComboBox(Cylinder_View)
        self.combobox_units.addItem("")
        self.combobox_units.addItem("")
        self.combobox_units.setObjectName(u"combobox_units")
        self.combobox_units.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.combobox_units, 5, 1, 1, 1)

        self.label = QLabel(Cylinder_View)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.spinbox_diameter = QDoubleSpinBox(Cylinder_View)
        self.spinbox_diameter.setObjectName(u"spinbox_diameter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(2)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.spinbox_diameter.sizePolicy().hasHeightForWidth())
        self.spinbox_diameter.setSizePolicy(sizePolicy2)
        self.spinbox_diameter.setMinimumSize(QSize(135, 0))
        self.spinbox_diameter.setMaximumSize(QSize(16777215, 16777215))
        self.spinbox_diameter.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.spinbox_diameter, 0, 1, 1, 1)

        self.label_2 = QLabel(Cylinder_View)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.spinbox_length = QDoubleSpinBox(Cylinder_View)
        self.spinbox_length.setObjectName(u"spinbox_length")
        sizePolicy2.setHeightForWidth(self.spinbox_length.sizePolicy().hasHeightForWidth())
        self.spinbox_length.setSizePolicy(sizePolicy2)
        self.spinbox_length.setMinimumSize(QSize(135, 0))
        self.spinbox_length.setMaximumSize(QSize(16777215, 16777215))
        self.spinbox_length.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_length.setDecimals(0)
        self.spinbox_length.setMinimum(60)
        self.spinbox_length.setMaximum(300)

        self.gridLayout.addWidget(self.spinbox_length, 1, 1, 1, 1)

        self.label_4 = QLabel(Cylinder_View)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.spinbox_base_thickness = QDoubleSpinBox(Cylinder_View)
        self.spinbox_base_thickness.setObjectName(u"spinbox_base_thickness")
        sizePolicy2.setHeightForWidth(self.spinbox_base_thickness.sizePolicy().hasHeightForWidth())
        self.spinbox_base_thickness.setSizePolicy(sizePolicy2)
        self.spinbox_base_thickness.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_base_thickness.setDecimals(0)
        self.spinbox_base_thickness.setMaximum(99.000000000000000)

        self.gridLayout.addWidget(self.spinbox_base_thickness, 2, 1, 1, 1)

        self.label_5 = QLabel(Cylinder_View)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.spinbox_base_height = QDoubleSpinBox(Cylinder_View)
        self.spinbox_base_height.setObjectName(u"spinbox_base_height")
        sizePolicy2.setHeightForWidth(self.spinbox_base_height.sizePolicy().hasHeightForWidth())
        self.spinbox_base_height.setSizePolicy(sizePolicy2)
        self.spinbox_base_height.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_base_height.setDecimals(0)
        self.spinbox_base_height.setMaximum(99.000000000000000)
        self.spinbox_base_height.setSingleStep(1)
        self.spinbox_base_height.setValue(0)

        self.gridLayout.addWidget(self.spinbox_base_height, 3, 1, 1, 1)

        self.label_3 = QLabel(Cylinder_View)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.cb_add_base = QCheckBox(Cylinder_View)
        self.cb_add_base.setObjectName(u"cb_add_base")
        sizePolicy2.setHeightForWidth(self.cb_add_base.sizePolicy().hasHeightForWidth())
        self.cb_add_base.setSizePolicy(sizePolicy2)
        self.cb_add_base.setMinimumSize(QSize(100, 0))
        self.cb_add_base.setMaximumSize(QSize(1000, 16777215))
        self.cb_add_base.setLayoutDirection(Qt.RightToLeft)
        self.cb_add_base.setStyleSheet(u"QCheckBox {\n"
"    background-color: rgb(240, 245, 250);\n"
"}\n"
"")
        self.cb_add_base.setIconSize(QSize(16, 16))
        self.cb_add_base.setChecked(False)

        self.gridLayout.addWidget(self.cb_add_base, 4, 1, 1, 1)

        self.label_add_notch = QLabel(Cylinder_View)
        self.label_add_notch.setObjectName(u"label_add_notch")
        self.label_add_notch.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_add_notch, 6, 0, 1, 1)

        self.cb_add_notch = QCheckBox(Cylinder_View)
        self.cb_add_notch.setObjectName(u"cb_add_notch")
        self.cb_add_notch.setLayoutDirection(Qt.RightToLeft)
        self.cb_add_notch.setStyleSheet(u"QCheckBox {\n"
"    background-color: rgb(240, 245, 250);\n"
"}\n"
"")
        self.cb_add_notch.setChecked(True)

        self.gridLayout.addWidget(self.cb_add_notch, 6, 1, 1, 1)

        self.label_notch_angle = QLabel(Cylinder_View)
        self.label_notch_angle.setObjectName(u"label_notch_angle")
        self.label_notch_angle.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_notch_angle, 7, 0, 1, 1)

        self.spinbox_notch_angle = QDoubleSpinBox(Cylinder_View)
        self.spinbox_notch_angle.setObjectName(u"spinbox_notch_angle")
        self.spinbox_notch_angle.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_notch_angle.setDecimals(1)
        self.spinbox_notch_angle.setMinimum(0.000000000000000)
        self.spinbox_notch_angle.setMaximum(359.899999999999977)
        self.spinbox_notch_angle.setSingleStep(1.000000000000000)
        self.spinbox_notch_angle.setValue(0.000000000000000)
        self.spinbox_notch_angle.setWrapping(True)

        self.gridLayout.addWidget(self.spinbox_notch_angle, 7, 1, 1, 1)

        self.label_notch_width = QLabel(Cylinder_View)
        self.label_notch_width.setObjectName(u"label_notch_width")
        self.label_notch_width.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_notch_width, 8, 0, 1, 1)

        self.spinbox_notch_width = QDoubleSpinBox(Cylinder_View)
        self.spinbox_notch_width.setObjectName(u"spinbox_notch_width")
        self.spinbox_notch_width.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_notch_width.setDecimals(1)
        self.spinbox_notch_width.setMinimum(0.500000000000000)
        self.spinbox_notch_width.setMaximum(10.000000000000000)
        self.spinbox_notch_width.setSingleStep(0.100000000000000)
        self.spinbox_notch_width.setValue(2.000000000000000)

        self.gridLayout.addWidget(self.spinbox_notch_width, 8, 1, 1, 1)

        self.label_notch_depth = QLabel(Cylinder_View)
        self.label_notch_depth.setObjectName(u"label_notch_depth")
        self.label_notch_depth.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_notch_depth, 9, 0, 1, 1)

        self.spinbox_notch_depth = QDoubleSpinBox(Cylinder_View)
        self.spinbox_notch_depth.setObjectName(u"spinbox_notch_depth")
        self.spinbox_notch_depth.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_notch_depth.setDecimals(1)
        self.spinbox_notch_depth.setMinimum(0.500000000000000)
        self.spinbox_notch_depth.setMaximum(5.000000000000000)
        self.spinbox_notch_depth.setSingleStep(0.100000000000000)
        self.spinbox_notch_depth.setValue(1.800000000000000)

        self.gridLayout.addWidget(self.spinbox_notch_depth, 9, 1, 1, 1)

        self.label_notch_height = QLabel(Cylinder_View)
        self.label_notch_height.setObjectName(u"label_notch_height")
        self.label_notch_height.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_notch_height, 10, 0, 1, 1)

        self.spinbox_notch_height = QDoubleSpinBox(Cylinder_View)
        self.spinbox_notch_height.setObjectName(u"spinbox_notch_height")
        self.spinbox_notch_height.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);")
        self.spinbox_notch_height.setDecimals(0)
        self.spinbox_notch_height.setMinimum(1.000000000000000)
        self.spinbox_notch_height.setMaximum(60.000000000000000)
        self.spinbox_notch_height.setSingleStep(1.000000000000000)
        self.spinbox_notch_height.setValue(10.000000000000000)

        self.gridLayout.addWidget(self.spinbox_notch_height, 10, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.btn_apply_settings = QPushButton(Cylinder_View)
        self.btn_apply_settings.setObjectName(u"btn_apply_settings")
        sizePolicy2.setHeightForWidth(self.btn_apply_settings.sizePolicy().hasHeightForWidth())
        self.btn_apply_settings.setSizePolicy(sizePolicy2)
        self.btn_apply_settings.setMinimumSize(QSize(240, 33))
        self.btn_apply_settings.setMaximumSize(QSize(1000, 16777215))
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

        self.verticalSpacer = QSpacerItem(280, 270, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

#if QT_CONFIG(shortcut)
        self.label_units.setBuddy(self.combobox_units)
        self.label.setBuddy(self.spinbox_diameter)
        self.label_2.setBuddy(self.spinbox_length)
        self.label_3.setBuddy(self.cb_add_base)
        self.label_add_notch.setBuddy(self.cb_add_notch)
        self.label_notch_angle.setBuddy(self.spinbox_notch_angle)
        self.label_notch_width.setBuddy(self.spinbox_notch_width)
        self.label_notch_depth.setBuddy(self.spinbox_notch_depth)
        self.label_notch_height.setBuddy(self.spinbox_notch_height)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Cylinder_View)

        QMetaObject.connectSlotsByName(Cylinder_View)
    # setupUi

    def retranslateUi(self, Cylinder_View):
        Cylinder_View.setWindowTitle(QCoreApplication.translate("Cylinder_View", u"Form", None))
        self.label_units.setText(QCoreApplication.translate("Cylinder_View", u"Units", None))
        self.combobox_units.setItemText(0, QCoreApplication.translate("Cylinder_View", u"mm", None))
        self.combobox_units.setItemText(1, QCoreApplication.translate("Cylinder_View", u"cm", None))

        self.label.setText(QCoreApplication.translate("Cylinder_View", u"Cylinder Diameter", None))
        self.spinbox_diameter.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_2.setText(QCoreApplication.translate("Cylinder_View", u"Cylinder Length", None))
        self.spinbox_length.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_4.setText(QCoreApplication.translate("Cylinder_View", u"Collar Thickness", None))
        self.spinbox_base_thickness.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_5.setText(QCoreApplication.translate("Cylinder_View", u"Collar Height", None))
        self.spinbox_base_height.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_3.setText(QCoreApplication.translate("Cylinder_View", u"Add Collar", None))
        self.cb_add_base.setText("")
        self.label_add_notch.setText(QCoreApplication.translate("Cylinder_View", u"Add Notch", None))
        self.cb_add_notch.setText("")
        self.label_notch_angle.setText(QCoreApplication.translate("Cylinder_View", u"Notch Angle", None))
        self.spinbox_notch_angle.setSuffix(QCoreApplication.translate("Cylinder_View", u"\u00b0", None))
        self.label_notch_width.setText(QCoreApplication.translate("Cylinder_View", u"Notch Width", None))
        self.spinbox_notch_width.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_notch_depth.setText(QCoreApplication.translate("Cylinder_View", u"Notch Depth", None))
        self.spinbox_notch_depth.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.label_notch_height.setText(QCoreApplication.translate("Cylinder_View", u"Notch Height", None))
        self.spinbox_notch_height.setSuffix(QCoreApplication.translate("Cylinder_View", u" mm", None))
        self.btn_apply_settings.setText(QCoreApplication.translate("Cylinder_View", u"Apply Settings", None))
    # retranslateUi

