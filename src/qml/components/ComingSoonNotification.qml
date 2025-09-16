import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: notification
    width: 260
    height: 70
    radius: 10
    color: "transparent"
    border.color: "transparent"
    border.width: 0
    
    // Animation properties
    property string message: "Coming Soon"
    property string icon: "✨"
    
    // Animation states
    states: [
        State {
            name: "hidden"
            PropertyChanges {
                target: notification
                opacity: 0
                scale: 0.8
                x: notification.parent ? notification.parent.width : 0
                y: -notification.height
            }
        },
        State {
            name: "visible"
            PropertyChanges {
                target: notification
                opacity: 1
                scale: 1.0
                x: notification.parent ? notification.parent.width - notification.width - 32 : 0
                y: 32
            }
        }
    ]
    
    transitions: [
        Transition {
            from: "hidden"
            to: "visible"
            SequentialAnimation {
                ParallelAnimation {
                    NumberAnimation {
                        target: notification
                        property: "opacity"
                        duration: 250
                        easing.type: Easing.OutCubic
                    }
                    NumberAnimation {
                        target: notification
                        property: "scale"
                        duration: 250
                        easing.type: Easing.OutBack
                    }
                    NumberAnimation {
                        target: notification
                        property: "x"
                        duration: 250
                        easing.type: Easing.OutCubic
                    }
                    NumberAnimation {
                        target: notification
                        property: "y"
                        duration: 250
                        easing.type: Easing.OutCubic
                    }
                }
            }
        },
        Transition {
            from: "visible"
            to: "hidden"
            ParallelAnimation {
                NumberAnimation {
                    target: notification
                    property: "opacity"
                    duration: 200
                    easing.type: Easing.InCubic
                }
                NumberAnimation {
                    target: notification
                    property: "scale"
                    duration: 200
                    easing.type: Easing.InCubic
                }
                NumberAnimation {
                    target: notification
                    property: "x"
                    duration: 200
                    easing.type: Easing.InCubic
                }
                NumberAnimation {
                    target: notification
                    property: "y"
                    duration: 200
                    easing.type: Easing.InCubic
                }
            }
        }
    ]
    
    // Content
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10
        
        // Icon with pulse animation
        Rectangle {
            id: iconContainer
            width: 32
            height: 32
            radius: 16
            color: "#3fb950"
            Layout.alignment: Qt.AlignVCenter
            
            
            Text {
                anchors.centerIn: parent
                text: notification.icon
                font.pixelSize: 16
                color: "white"
            }
            
            // Pulse animation
            SequentialAnimation on opacity {
                running: notification.state === "visible"
                loops: Animation.Infinite
                NumberAnimation {
                    to: 0.6
                    duration: 1000
                    easing.type: Easing.InOutQuad
                }
                NumberAnimation {
                    to: 1.0
                    duration: 1000
                    easing.type: Easing.InOutQuad
                }
            }
        }
        
        // Text content
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 42
            radius: 8
            color: "transparent"
            opacity: 1.0
            border.width: 0
            Layout.alignment: Qt.AlignVCenter
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 2
                
                Text {
                    text: notification.message
                    color: "#f0f6fc"
                    font.weight: 600
                    font.pixelSize: 14
                    font.letterSpacing: 0.3
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "Coming Soon"
                    color: "#8b949e"
                    font.pixelSize: 11
                    font.weight: 400
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
    }
    
    // Auto-hide timer
    Timer {
        id: hideTimer
        interval: 2500
        onTriggered: {
            notification.state = "hidden"
        }
    }
    
    // Functions
    function show(msg, icn) {
        message = msg || "Coming Soon"
        icon = icn || "✨"
        state = "visible"
        hideTimer.restart()
    }
    
    function hide() {
        state = "hidden"
        hideTimer.stop()
    }
    
    // Initialize as hidden
    Component.onCompleted: {
        state = "hidden"
    }
}