import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    
    property bool running: false
    property string text: "Load data from Steam..."
    property color primaryColor: "#2196F3"
    property color secondaryColor: "#E3F2FD"
    
    visible: running
    enabled: running
    opacity: running ? 1 : 0
    z: running ? 1000 : -1
    
    // Smooth fade in/out animation
    Behavior on opacity {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }
    
    // Background overlay
    Rectangle {
        anchors.fill: parent
        color: mainWindow.darkBg
        opacity: running ? 0.9 : 0
        
        Behavior on opacity {
            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
        }
        
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            enabled: running
            onClicked: {} // Prevent clicks from passing through
            onWheel: {} // Prevent wheel events from passing through
        }
    }
    
    // Loading container
    Rectangle {
        id: loadingContainer
        width: 280
        height: 160
        anchors.centerIn: parent
        radius: 12
        color: mainWindow.cardBg
        border.color: mainWindow.border
        border.width: 1
        visible: running
        
        // Modern shadow
        Rectangle {
            anchors.fill: parent
            anchors.margins: -4
            radius: parent.radius + 4
            color: "transparent"
            border.color: "#10000000"
            border.width: 1
            z: -1
        }
        
        // Content
        Column {
            anchors.centerIn: parent
            spacing: 16
            width: parent.width - 32
            
            // Modern spinner
            Item {
                width: 48
                height: 48
                anchors.horizontalCenter: parent.horizontalCenter
                
                // Outer ring
                Rectangle {
                    id: outerRing
                    width: 48
                    height: 48
                    anchors.centerIn: parent
                    radius: 24
                    color: "transparent"
                    border.color: primaryColor
                    border.width: 3
                    opacity: 0.2
                }
                
                // Spinning ring
                Rectangle {
                    id: spinnerRing
                    width: 48
                    height: 48
                    anchors.centerIn: parent
                    radius: 24
                    color: "transparent"
                    border.color: primaryColor
                    border.width: 3
                    
                    // Create arc effect
                    Canvas {
                        anchors.fill: parent
                        anchors.margins: 3
                        
                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            
                            ctx.strokeStyle = primaryColor
                            ctx.lineWidth = 3
                            ctx.lineCap = "round"
                            
                            var centerX = width / 2
                            var centerY = height / 2
                            var radius = Math.min(width, height) / 2 - 3
                            
                            ctx.beginPath()
                            ctx.arc(centerX, centerY, radius, 0, Math.PI * 1.5)
                            ctx.stroke()
                        }
                        
                        RotationAnimation on rotation {
                            running: root.running
                            loops: Animation.Infinite
                            duration: 1200
                            from: 0
                            to: 360
                        }
                    }
                }
            }
            
            // Loading text
            Text {
                text: root.text
                color: mainWindow.textPrimary
                font.pixelSize: 14
                font.weight: 500
                horizontalAlignment: Text.AlignHCenter
                anchors.horizontalCenter: parent.horizontalCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            // Progress indicator
            Rectangle {
                width: parent.width
                height: 2
                radius: 1
                color: mainWindow.border
                anchors.horizontalCenter: parent.horizontalCenter
                
                Rectangle {
                    width: parent.width * 0.3
                    height: parent.height
                    radius: parent.radius
                    color: primaryColor
                    
                    SequentialAnimation on x {
                        running: root.running
                        loops: Animation.Infinite
                        NumberAnimation {
                            from: 0
                            to: parent.width - width
                            duration: 1000
                            easing.type: Easing.InOutQuad
                        }
                        NumberAnimation {
                            from: parent.width - width
                            to: 0
                            duration: 1000
                            easing.type: Easing.InOutQuad
                        }
                    }
                }
            }
        }
    }
}