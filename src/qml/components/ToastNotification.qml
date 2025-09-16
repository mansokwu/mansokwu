import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: toast
    width: 280
    height: 48
    radius: 8
    color: mainWindow.cardBg
    border.color: mainWindow.border
    border.width: 1
    
    // Subtle shadow effect
    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        radius: parent.radius + 1
        color: "transparent"
        border.color: mainWindow.shadowDark
        border.width: 1
        z: -1
        opacity: 0.3
    }
    
    // Properties
    property string message: ""
    property string type: "info" // info, success, warning, error
    property int duration: 3000
    property bool isVisible: false
    
    // Animation properties
    property real slideDistance: 80
    
    // State management
    state: isVisible ? "visible" : "hidden"
    
    states: [
        State {
            name: "visible"
            PropertyChanges {
                target: toast
                opacity: 1
                x: parent.width - width - 20
            }
        },
        State {
            name: "hidden"
            PropertyChanges {
                target: toast
                opacity: 0
                x: parent.width + 20
            }
        }
    ]
    
    transitions: [
        Transition {
            from: "hidden"
            to: "visible"
            ParallelAnimation {
                NumberAnimation {
                    target: toast
                    property: "opacity"
                    duration: 250
                    easing.type: Easing.OutQuart
                }
                NumberAnimation {
                    target: toast
                    property: "x"
                    duration: 250
                    easing.type: Easing.OutQuart
                }
            }
        },
        Transition {
            from: "visible"
            to: "hidden"
            ParallelAnimation {
                NumberAnimation {
                    target: toast
                    property: "opacity"
                    duration: 200
                    easing.type: Easing.InQuart
                }
                NumberAnimation {
                    target: toast
                    property: "x"
                    duration: 200
                    easing.type: Easing.InQuart
                }
            }
        }
    ]
    
    // Content
    Row {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10
        
        // Icon
        Rectangle {
            width: 24
            height: 24
            radius: 12
            color: getIconColor()
            anchors.verticalCenter: parent.verticalCenter
            
            Text {
                anchors.centerIn: parent
                text: getIconText()
                color: "#ffffff"
                font.pixelSize: 12
                font.weight: 600
            }
        }
        
        // Message
        Text {
            text: toast.message
            color: mainWindow.textPrimary
            font.pixelSize: 13
            font.weight: 500
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width - 50 // Account for icon and spacing
            wrapMode: Text.WordWrap
            elide: Text.ElideRight
        }
    }
    
    // Auto-hide timer
    Timer {
        id: hideTimer
        interval: toast.duration
        running: toast.isVisible
        onTriggered: {
            toast.hide()
        }
    }
    
    // Functions
    function show(msg, toastType, toastDuration) {
        message = msg
        type = toastType || "info"
        duration = toastDuration || 3000
        isVisible = true
    }
    
    function hide() {
        isVisible = false
    }
    
    function getIconColor() {
        switch(type) {
            case "success": return mainWindow.success
            case "warning": return mainWindow.warning
            case "error": return mainWindow.error
            case "info": 
            default: return mainWindow.accent
        }
    }
    
    function getIconText() {
        switch(type) {
            case "success": return "✓"
            case "warning": return "!"
            case "error": return "✕"
            case "info": 
            default: return "i"
        }
    }
}