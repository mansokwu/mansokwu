import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: navButton
    property string text: ""
    property string icon: ""
    property bool selected: false
    property bool comingSoon: false
    property bool hovered: false
    
    signal clicked()
    
    height: 48
    Layout.fillWidth: true
    color: selected ? mainWindow.buttonPrimary : (hovered ? mainWindow.buttonPrimaryHover : "transparent")
    radius: 10
    border.width: selected ? 1 : 0
    border.color: selected ? mainWindow.buttonBorderHover : "transparent"
    
    // Smooth transitions
    Behavior on color {
        ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
    }
    Behavior on border.width {
        NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
    }
    Behavior on border.color {
        ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onClicked: navButton.clicked()
        cursorShape: Qt.PointingHandCursor
        
        onEntered: {
            navButton.hovered = true
        }
        onExited: {
            navButton.hovered = false
        }
    }
    
    RowLayout {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12
        
        // Icon - can be either emoji text or SVG image
        Item {
            width: 18
            height: 18
            
            Text {
                id: emojiIcon
                text: navButton.icon
                font.pixelSize: 18
                opacity: comingSoon ? 0.7 : 1.0
                visible: !navButton.icon.startsWith("file://")
                anchors.centerIn: parent
            }
            
            Image {
                id: svgIcon
                source: navButton.icon.startsWith("file://") ? navButton.icon : ""
                width: 18
                height: 18
                fillMode: Image.PreserveAspectFit
                smooth: true
                sourceSize.width: 18
                sourceSize.height: 18
                opacity: comingSoon ? 0.7 : 1.0
                visible: navButton.icon.startsWith("file://")
                anchors.centerIn: parent
            }
        }
        
        Text {
            text: navButton.text
            color: comingSoon ? mainWindow.buttonTextSecondary : (selected ? mainWindow.buttonText : (hovered ? mainWindow.buttonText : mainWindow.buttonTextSecondary))
            font.weight: selected ? 700 : 600
            font.pixelSize: 13
            font.letterSpacing: 0.2
            Layout.fillWidth: true
        }
    }
}