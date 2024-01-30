# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rtsp_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(545, 59)
        self.label_rtsp = QLabel(Form)
        self.label_rtsp.setObjectName(u"label_rtsp")
        self.label_rtsp.setGeometry(QRect(0, 10, 141, 41))
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(14)
        self.label_rtsp.setFont(font)
        self.label_rtsp.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.label_rtsp.setAlignment(Qt.AlignCenter)
        self.lineEdit_inaddress = QLineEdit(Form)
        self.lineEdit_inaddress.setObjectName(u"lineEdit_inaddress")
        self.lineEdit_inaddress.setGeometry(QRect(140, 10, 311, 41))
        font1 = QFont()
        font1.setFamilies([u"Consolas"])
        font1.setPointSize(12)
        self.lineEdit_inaddress.setFont(font1)
        self.lineEdit_inaddress.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.lineEdit_inaddress.setMaxLength(100)
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(460, 10, 81, 41))
        font2 = QFont()
        font2.setPointSize(11)
        self.pushButton.setFont(font2)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_rtsp.setText(QCoreApplication.translate("Form", u"Rtsp address:", None))
        self.lineEdit_inaddress.setText("")
        self.pushButton.setText(QCoreApplication.translate("Form", u"Confirm", None))
    # retranslateUi

