import time

from PyQt5 import QtGui, QtCore

from ui.room_item import Ui_Form
from PyQt5.QtWidgets import QWidget

class Room_Item(QWidget,Ui_Form):
    def __init__(self,parent=None,room_data=None):
        super(Room_Item,self).__init__(parent)
        self.setupUi(self)
        self.data = room_data
        self.setRoomInfo()

    def setRoomInfo(self):
        self.room_name.setText('{}({})'.format(self.data['naturalName'], self.data['roomName']))
        self.description.setText("<a style='color:#BCBCBC'>{}</a>".format(self.data['description']))
        timeStamp = int(self.data['creationDate']) / 1000
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        self.create_time.setText("<a style='color:#BCBCBC'>{}</a>".format(otherStyleTime))
        members = len(self.data['owners']) + len(self.data['admins']) + len(self.data['members'])
        memberCounter = "<a style='color:#BCBCBC'>{}/{}</a>".format(members, ('∞' if self.data['maxUsers']==0 else self.data['maxUsers']))
        self.member.setText(memberCounter)