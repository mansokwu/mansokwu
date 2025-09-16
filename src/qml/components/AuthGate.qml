import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: authGate
    anchors.fill: parent
    color: "transparent"
    visible: true
    z: 1000
    
    // Properties
    property bool isAuthenticated: false
    property bool isLoading: false
    property string statusMessage: ""
    property string statusType: "info" // info, success, error
    
    // Signals
    signal loginRequested(string token)
    signal loginSuccess()
    signal loginFailed(string message)
    
    // Dark background
    Rectangle {
        anchors.fill: parent
        color: mainWindow.darkBg
    }
    
    // Main content container
    Rectangle {
        id: mainContainer
        width: Math.min(400, parent.width * 0.9)
        height: Math.min(500, parent.height * 0.8)
        anchors.centerIn: parent
        color: "transparent"
        
        Column {
            anchors.centerIn: parent
            spacing: 32
            width: parent.width
            
            // Logo section
            Rectangle {
                width: 180
                height: 180
                anchors.horizontalCenter: parent.horizontalCenter
                color: "transparent"
                
                Image {
                    id: logoImage
                    width: 160
                    height: 160
                    anchors.centerIn: parent
                    source: "file:///E:/MantaTools/src/assets/icons/logo.png"
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    
                    // Fallback text if image fails to load
                    Text {
                        anchors.centerIn: parent
                        text: "🎮"
                        font.pixelSize: 70
                        color: mainWindow.accent
                        visible: logoImage.status !== Image.Ready
                    }
                }
            }
            
            // Welcome text
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Welcome to Manta Games"
                color: "#ffffff"
                font.pixelSize: 24
                font.weight: Font.Bold
                font.family: "Segoe UI, Arial, sans-serif"
            }
            
            // Instruction text
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Enter your Token below to login"
                color: "#b0b0b0"
                font.pixelSize: 14
                font.family: "Segoe UI, Arial, sans-serif"
            }
            
            // Input field
            Rectangle {
                width: parent.width
                height: 48
                anchors.horizontalCenter: parent.horizontalCenter
                color: "#0d1117"
                border.color: tokenInput.activeFocus ? mainWindow.accent : mainWindow.border
                border.width: 1
                radius: 8
                
                TextInput {
                    id: tokenInput
                    anchors.fill: parent
                    anchors.margins: 16
                    verticalAlignment: TextInput.AlignVCenter
                    color: "#f0f6fc"
                    font.pixelSize: 14
                    font.family: "Segoe UI, Arial, sans-serif"
                    selectByMouse: true
                    selectionColor: mainWindow.accent
                    
                    property string placeholderText: "Enter your token..."
                    
                    Text {
                        anchors.fill: parent
                        text: tokenInput.placeholderText
                        color: "#7d8590"
                        font: tokenInput.font
                        verticalAlignment: Text.AlignVCenter
                        visible: tokenInput.text.length === 0 && !tokenInput.activeFocus
                    }
                    
                    onAccepted: {
                        if (text.trim().length > 0) {
                            authGate.loginRequested(text.trim())
                        }
                    }
                }
            }
            
            // Login button
            Rectangle {
                width: parent.width
                height: 48
                anchors.horizontalCenter: parent.horizontalCenter
                color: loginButton.enabled ? 
                       (loginButton.pressed ? mainWindow.buttonSuccessPressed : 
                        loginButton.hovered ? mainWindow.buttonSuccessHover : mainWindow.buttonSuccess) : 
                       mainWindow.buttonPrimary
                radius: 8
                
                MouseArea {
                    id: loginButton
                    anchors.fill: parent
                    enabled: !authGate.isLoading && tokenInput.text.trim().length > 0
                    hoverEnabled: true
                    
                    property bool hovered: false
                    
                    onEntered: hovered = true
                    onExited: hovered = false
                    onClicked: {
                        if (tokenInput.text.trim().length > 0) {
                            authGate.loginRequested(tokenInput.text.trim())
                        }
                    }
                    
                    Text {
                        anchors.centerIn: parent
                        text: authGate.isLoading ? "Authenticating..." : "Login"
                        color: loginButton.enabled ? mainWindow.buttonText : mainWindow.buttonTextSecondary
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        font.family: "Segoe UI, Arial, sans-serif"
                    }
                }
            }
            
            // Loading text
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Authenticating..."
                color: "#8b949e"
                font.pixelSize: 12
                font.family: "Segoe UI, Arial, sans-serif"
                visible: authGate.isLoading
                
                // Animated dots
                property int dotCount: 0
                
                Timer {
                    interval: 500
                    running: authGate.isLoading
                    repeat: true
                    onTriggered: {
                        loadingText.dotCount = (loadingText.dotCount + 1) % 4
                        loadingText.text = "Authenticating" + ".".repeat(loadingText.dotCount)
                    }
                }
            }
            
            // Status message
            Rectangle {
                width: parent.width
                height: 36
                anchors.horizontalCenter: parent.horizontalCenter
                color: authGate.statusType === "success" ? "#0d4429" : 
                       authGate.statusType === "error" ? "#490202" : 
                       "#0c2d6b"
                border.color: authGate.statusType === "success" ? "#238636" : 
                              authGate.statusType === "error" ? "#da3633" : 
                              mainWindow.accent
                border.width: 1
                radius: 6
                visible: authGate.statusMessage.length > 0
                
                Text {
                    anchors.centerIn: parent
                    text: authGate.statusMessage
                    color: authGate.statusType === "success" ? "#3fb950" : 
                           authGate.statusType === "error" ? "#f85149" : 
                           mainWindow.accent
                    font.pixelSize: 12
                    font.weight: Font.Medium
                    font.family: "Segoe UI, Arial, sans-serif"
                }
            }
            
            // Register text
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Don't have an account ? Register on"
                color: "#b0b0b0"
                font.pixelSize: 12
                font.family: "Segoe UI, Arial, sans-serif"
            }
            
            // Discord link
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Discord"
                color: "#0078d4"
                font.pixelSize: 12
                font.family: "Segoe UI, Arial, sans-serif"
                
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    
                    onEntered: parent.opacity = 1.0
                    onExited: parent.opacity = 0.8
                    onClicked: {
                        Qt.openUrlExternally("https://discord.com/invite/yBYsHXtZrR")
                    }
                }
            }
        }
    }
    
    // Animation for show/hide
    Behavior on opacity {
        NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
    }
    
    // Functions
    function show() {
        visible = true
        opacity = 1.0
    }
    
    function hide() {
        opacity = 0.0
        visible = false
    }
    
    function setLoading(loading) {
        isLoading = loading
    }
    
    function setStatus(message, type) {
        statusMessage = message
        statusType = type
    }
    
    function clearStatus() {
        statusMessage = ""
        statusType = "info"
    }
    
    function clearInput() {
        tokenInput.text = ""
    }
    
    // Initialize
    Component.onCompleted: {
        show()
    }
}
