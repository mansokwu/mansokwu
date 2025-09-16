import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: customButton
    
    property alias text: buttonText.text
    property alias enabled: mouseArea.enabled
    property alias font: buttonText.font
    property color buttonColor: mainWindow.buttonPrimary
    property color hoverColor: mainWindow.buttonPrimaryHover
    property color pressedColor: mainWindow.buttonPrimaryPressed
    property color textColor: mainWindow.buttonText
    property color borderColor: mainWindow.buttonBorder
    property int buttonRadius: 8
    // Progress mode: set 0..100 to show fill, or -1 to disable
    property int progress: -1
    property color progressColor: hoverColor
    property color progressTextColor: textColor
    
    signal clicked()
    
    color: mouseArea.pressed ? pressedColor : 
           mouseArea.containsMouse ? hoverColor : buttonColor
    radius: buttonRadius
    border.color: borderColor
    border.width: 1
    clip: false
    
    // Modern shadow effect
    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        color: "transparent"
        border.color: mainWindow.buttonBorder
        border.width: 1
        radius: buttonRadius + 1
        opacity: mouseArea.containsMouse ? 0.15 : 0
        z: -1
        
        Behavior on opacity {
            NumberAnimation { 
                duration: 100
                easing.type: Easing.OutQuad
            }
        }
    }
    
    // Progress fill overlay
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: progress >= 0 ? Math.round(parent.width * Math.max(0, Math.min(100, progress)) / 100) : 0
        color: progressColor
        opacity: 0.6
        radius: buttonRadius
        visible: progress >= 0
    }
    
    Text {
        id: buttonText
        anchors.centerIn: parent
        color: progress >= 0 ? progressTextColor : textColor
        font.weight: 600
        font.pixelSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    // Simple text shadow simulation
    Text {
        anchors.centerIn: parent
        anchors.horizontalCenterOffset: 1
        anchors.verticalCenterOffset: 1
        color: "#000000"
        opacity: 0.3
        font.weight: 600
        font.pixelSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        text: buttonText.text
        z: -1
    }
    
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
    Behavior on scale {
        NumberAnimation { 
            duration: 80
            easing.type: Easing.OutQuad
        }
    }
    
    // Scale effect on hover
    scale: mouseArea.containsMouse ? 1.01 : 1.0
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: customButton.clicked()
    }
}
