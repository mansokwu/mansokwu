import QtQuick 2.15

Rectangle {
    id: customTabButton
    
    property alias text: labelText.text
    property bool checked: false
    property color checkedColor: mainWindow.buttonPrimary
    property color hoverColor: mainWindow.buttonPrimaryHover
    property color pressedColor: mainWindow.buttonPrimaryPressed
    property color textColor: mainWindow.buttonTextSecondary
    property color checkedTextColor: mainWindow.buttonText
    
    signal clicked()
    
    color: checked ? checkedColor : 
           mouseArea.pressed ? pressedColor : 
           mouseArea.containsMouse ? hoverColor : "transparent"
    radius: 6
    
    // Modern border effect
    border.color: checked ? mainWindow.buttonBorderHover : "transparent"
    border.width: checked ? 1 : 0
    
    // Responsive animations
    Behavior on color {
        ColorAnimation { 
            duration: 100
            easing.type: Easing.OutQuad
        }
    }
    Behavior on border.color {
        ColorAnimation { 
            duration: 100
            easing.type: Easing.OutQuad
        }
    }
    Behavior on border.width {
        NumberAnimation { 
            duration: 100
            easing.type: Easing.OutQuad
        }
    }
    
    Text {
        id: labelText
        anchors.centerIn: parent
        color: checked ? checkedTextColor : textColor
        font.weight: checked ? 700 : 600
        font.pixelSize: 13
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        
        // Responsive text animations
        Behavior on color {
            ColorAnimation { 
                duration: 100
                easing.type: Easing.OutQuad
            }
        }
        Behavior on font.weight {
            NumberAnimation { 
                duration: 100
                easing.type: Easing.OutQuad
            }
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            customTabButton.checked = true
            customTabButton.clicked()
        }
    }
}


