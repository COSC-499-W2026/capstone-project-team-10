# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_view.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QGridLayout,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Export_View(object):
    def setupUi(self, Export_View):
        if not Export_View.objectName():
            Export_View.setObjectName(u"Export_View")
        Export_View.resize(433, 415)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Export_View.sizePolicy().hasHeightForWidth())
        Export_View.setSizePolicy(sizePolicy)
        Export_View.setMinimumSize(QSize(0, 290))
        Export_View.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(Export_View)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 10, 5, 5)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.label_2 = QLabel(Export_View)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.cb_tandem_shown = QCheckBox(Export_View)
        self.cb_tandem_shown.setObjectName(u"cb_tandem_shown")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cb_tandem_shown.sizePolicy().hasHeightForWidth())
        self.cb_tandem_shown.setSizePolicy(sizePolicy2)
        self.cb_tandem_shown.setLayoutDirection(Qt.RightToLeft)
        self.cb_tandem_shown.setStyleSheet(u"background-color: rgb(240, 245, 250);")
        self.cb_tandem_shown.setChecked(False)

        self.gridLayout.addWidget(self.cb_tandem_shown, 0, 1, 1, 1)

        self.label = QLabel(Export_View)
        self.label.setObjectName(u"label")
        self.label.setEnabled(True)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.cb_collet_preview_reference_sheet = QCheckBox(Export_View)
        self.cb_collet_preview_reference_sheet.setObjectName(u"cb_collet_preview_reference_sheet")
        sizePolicy2.setHeightForWidth(self.cb_collet_preview_reference_sheet.sizePolicy().hasHeightForWidth())
        self.cb_collet_preview_reference_sheet.setSizePolicy(sizePolicy2)
        self.cb_collet_preview_reference_sheet.setLayoutDirection(Qt.RightToLeft)
        self.cb_collet_preview_reference_sheet.setAutoFillBackground(False)
        self.cb_collet_preview_reference_sheet.setStyleSheet(u"background-color: rgb(240, 245, 250);")
        self.cb_collet_preview_reference_sheet.setChecked(True)

        self.gridLayout.addWidget(self.cb_collet_preview_reference_sheet, 1, 1, 1, 1)

        self.label_3 = QLabel(Export_View)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.sb_needle_collet_od = QDoubleSpinBox(Export_View)
        self.sb_needle_collet_od.setObjectName(u"sb_needle_collet_od")
        sizePolicy2.setHeightForWidth(self.sb_needle_collet_od.sizePolicy().hasHeightForWidth())
        self.sb_needle_collet_od.setSizePolicy(sizePolicy2)
        self.sb_needle_collet_od.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"")
        self.sb_needle_collet_od.setDecimals(3)

        self.gridLayout.addWidget(self.sb_needle_collet_od, 2, 1, 1, 1)

        self.label_4 = QLabel(Export_View)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.sb_tandem_collet_outer_od = QDoubleSpinBox(Export_View)
        self.sb_tandem_collet_outer_od.setObjectName(u"sb_tandem_collet_outer_od")
        sizePolicy2.setHeightForWidth(self.sb_tandem_collet_outer_od.sizePolicy().hasHeightForWidth())
        self.sb_tandem_collet_outer_od.setSizePolicy(sizePolicy2)
        self.sb_tandem_collet_outer_od.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"")
        self.sb_tandem_collet_outer_od.setDecimals(3)

        self.gridLayout.addWidget(self.sb_tandem_collet_outer_od, 3, 1, 1, 1)

        self.label_5 = QLabel(Export_View)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setStyleSheet(u"background-color: rgb(240, 245, 250);\n"
"color: rgb(0, 0, 0);")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.sb_tandem_collet_inner_od = QDoubleSpinBox(Export_View)
        self.sb_tandem_collet_inner_od.setObjectName(u"sb_tandem_collet_inner_od")
        sizePolicy2.setHeightForWidth(self.sb_tandem_collet_inner_od.sizePolicy().hasHeightForWidth())
        self.sb_tandem_collet_inner_od.setSizePolicy(sizePolicy2)
        self.sb_tandem_collet_inner_od.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"")
        self.sb_tandem_collet_inner_od.setDecimals(3)

        self.gridLayout.addWidget(self.sb_tandem_collet_inner_od, 4, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.label_tandem_hole_warning = QLabel(Export_View)
        self.label_tandem_hole_warning.setObjectName(u"label_tandem_hole_warning")
        self.label_tandem_hole_warning.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.label_tandem_hole_warning.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_tandem_hole_warning)

        self.btn_export_mesh = QPushButton(Export_View)
        self.btn_export_mesh.setObjectName(u"btn_export_mesh")
        sizePolicy2.setHeightForWidth(self.btn_export_mesh.sizePolicy().hasHeightForWidth())
        self.btn_export_mesh.setSizePolicy(sizePolicy2)
        self.btn_export_mesh.setMinimumSize(QSize(240, 33))
        self.btn_export_mesh.setMaximumSize(QSize(16777215, 33))
        self.btn_export_mesh.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout.addWidget(self.btn_export_mesh)

        self.btn_export_template_reference = QPushButton(Export_View)
        self.btn_export_template_reference.setObjectName(u"btn_export_template_reference")
        sizePolicy2.setHeightForWidth(self.btn_export_template_reference.sizePolicy().hasHeightForWidth())
        self.btn_export_template_reference.setSizePolicy(sizePolicy2)
        self.btn_export_template_reference.setMinimumSize(QSize(240, 33))
        self.btn_export_template_reference.setMaximumSize(QSize(16777215, 33))
        self.btn_export_template_reference.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout.addWidget(self.btn_export_template_reference)

        self.btn_export_shapes = QPushButton(Export_View)
        self.btn_export_shapes.setObjectName(u"btn_export_shapes")
        sizePolicy2.setHeightForWidth(self.btn_export_shapes.sizePolicy().hasHeightForWidth())
        self.btn_export_shapes.setSizePolicy(sizePolicy2)
        self.btn_export_shapes.setMinimumSize(QSize(240, 33))
        self.btn_export_shapes.setMaximumSize(QSize(16777215, 33))
        self.btn_export_shapes.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout.addWidget(self.btn_export_shapes)

        self.verticalSpacer = QSpacerItem(267, 4338, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_export_current_config = QPushButton(Export_View)
        self.btn_export_current_config.setObjectName(u"btn_export_current_config")
        sizePolicy2.setHeightForWidth(self.btn_export_current_config.sizePolicy().hasHeightForWidth())
        self.btn_export_current_config.setSizePolicy(sizePolicy2)
        self.btn_export_current_config.setMinimumSize(QSize(240, 33))
        self.btn_export_current_config.setMaximumSize(QSize(16777215, 33))
        self.btn_export_current_config.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout.addWidget(self.btn_export_current_config)


        self.retranslateUi(Export_View)

        QMetaObject.connectSlotsByName(Export_View)
    # setupUi

    def retranslateUi(self, Export_View):
        Export_View.setWindowTitle(QCoreApplication.translate("Export_View", u"Form", None))
        Export_View.setWindowFilePath("")
        self.label_2.setText(QCoreApplication.translate("Export_View", u"Show Tandem", None))
        self.cb_tandem_shown.setText("")
        self.label.setText(QCoreApplication.translate("Export_View", u"Show Collet Spacings", None))
        self.cb_collet_preview_reference_sheet.setText("")
        self.label_3.setText(QCoreApplication.translate("Export_View", u"Needle Collet Spacing Tol.", None))
        self.label_4.setText(QCoreApplication.translate("Export_View", u"Tandem Outer Spacing Tol.", None))
        self.label_5.setText(QCoreApplication.translate("Export_View", u"Tandem Inner Spacing Tol.", None))
        self.btn_export_mesh.setText(QCoreApplication.translate("Export_View", u"Export Mesh", None))
        self.btn_export_template_reference.setText(QCoreApplication.translate("Export_View", u"Export Reference Sheet", None))
        self.btn_export_shapes.setText(QCoreApplication.translate("Export_View", u"Export Shape(s)", None))
        self.btn_export_current_config.setText(QCoreApplication.translate("Export_View", u"Export Current Settings as Config", None))
    # retranslateUi

