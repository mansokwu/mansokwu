import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: customCheckBox
    
    property alias text: labelText.text
    property bool checked: false
    property color checkedColor: mainWindow.success
    property color uncheckedColor: mainWindow.border
    property color borderColor: mainWindow.border
    property color textColor: mainWindow.textPrimary
    
    signal clicked()
    
    Row {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8
        
        Rectangle {
            id: indicator
            width: 20
            height: 20
            radius: 4
            border.color: borderColor
            border.width: 1
            color: customCheckBox.checked ? checkedColor : "transparent"
            
            Rectangle {
                width: 12
                height: 12
                anchors.centerIn: parent
                radius: 2
                color: "white"
                visible: customCheckBox.checked
            }
        }
        
        Text {
            id: labelText
            anchors.verticalCenter: indicator.verticalCenter
            font.pixelSize: 13
            font.weight: 500
            color: textColor
        }
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            customCheckBox.checked = !customCheckBox.checked
            customCheckBox.clicked()
        }
    }
}
