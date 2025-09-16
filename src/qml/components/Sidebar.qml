import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: sidebar
    color: mainWindow.darkBg
    border.color: mainWindow.border
    border.width: 1
    radius: 16
    
    // Subtle shadow effect
    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        color: "transparent"
        border.color: "#000000"
        border.width: 1
        radius: 17
        opacity: 0.1
        z: -1
    }
    
    signal navChanged(string name)
    signal showComingSoon(string message, string icon)
    
    property bool gamesSelected: true
    property bool settingsSelected: false
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 0
        
        // STEAM UNLOCKER section
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 24
            spacing: 12
            
            Text {
                text: "STEAM UNLOCKER"
                color: mainWindow.textMuted
                font.weight: Font.DemiBold
                font.pixelSize: 11
                font.letterSpacing: 1.5
                Layout.topMargin: 0
                Layout.bottomMargin: 8
            }
            
            Rectangle {
                height: 1
                Layout.fillWidth: true
                color: mainWindow.divider
                opacity: 0.3
                radius: 0.5
            }
            
            // Navigation buttons with improved spacing
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Layout.topMargin: 12
                
                NavButton {
                    text: "Games"
                    icon: "file:///E:/MantaTools/src/assets/icons/games.svg"
                    selected: sidebar.gamesSelected
                    onClicked: {
                        sidebar.gamesSelected = true
                        sidebar.settingsSelected = false
                        navChanged("games")
                    }
                }
                
                NavButton {
                    text: "Library"
                    icon: "file:///E:/MantaTools/src/assets/icons/library.svg"
                    selected: sidebar.settingsSelected
                    onClicked: {
                        sidebar.gamesSelected = false
                        sidebar.settingsSelected = true
                        navChanged("settings")
                    }
                }
            }
        }
        
        // MEMBERSHIP section
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 32
            spacing: 12
            
            Text {
                text: "MEMBERSHIP"
                color: mainWindow.textMuted
                font.weight: Font.DemiBold
                font.pixelSize: 11
                font.letterSpacing: 1.5
                Layout.topMargin: 0
                Layout.bottomMargin: 8
            }
            
            Rectangle {
                height: 1
                Layout.fillWidth: true
                color: mainWindow.divider
                opacity: 0.3
                radius: 0.5
            }
            
            // Membership buttons
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Layout.topMargin: 12
                
                NavButton {
                    text: "Denuvo Activation"
                    icon: "file:///E:/MantaTools/src/assets/icons/denuvo_activation.svg"
                    comingSoon: true
                    onClicked: {
                        sidebar.showComingSoon("Denuvo Activation", "🛡️")
                    }
                }
                
                NavButton {
                    text: "3rd-Party Bypass"
                    icon: "file:///E:/MantaTools/src/assets/icons/3rd_party_bypass.svg"
                    comingSoon: true
                    onClicked: {
                        sidebar.showComingSoon("3rd-Party Bypass", "🔑")
                    }
                }
                
                NavButton {
                    text: "Subscribe"
                    icon: "file:///E:/MantaTools/src/assets/icons/subscribe.svg"
                    comingSoon: true
                    onClicked: {
                        sidebar.showComingSoon("Subscribe", "👑")
                    }
                }
            }
        }
        
        // Spacer
        Item {
            Layout.fillHeight: true
        }
        
        // Discord CTA with enhanced design
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 52
            Layout.topMargin: 20
            Layout.bottomMargin: 20
            color: "#5865F2"
            radius: 12
            
            // Hover effect
            Rectangle {
                anchors.fill: parent
                color: "#7289DA"
                radius: 12
                opacity: discordButton.hovered ? 1.0 : 0.0
                
                Behavior on opacity {
                    NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                }
            }
            
            // Pressed effect
            Rectangle {
                anchors.fill: parent
                color: "#4752C4"
                radius: 12
                opacity: discordButton.pressed ? 1.0 : 0.0
                
                Behavior on opacity {
                    NumberAnimation { duration: 100; easing.type: Easing.OutCubic }
                }
            }
            
            // Subtle shadow
            Rectangle {
                anchors.fill: parent
                anchors.margins: 2
                color: "#000000"
                opacity: 0.1
                radius: 12
                z: -1
            }
            
            MouseArea {
                id: discordButton
                anchors.fill: parent
                hoverEnabled: true
                
                property bool hovered: false
                property bool pressed: false
                
                onEntered: hovered = true
                onExited: hovered = false
                onPressed: pressed = true
                onReleased: pressed = false
                onClicked: {
                    Qt.openUrlExternally("https://discord.com/invite/yBYsHXtZrR")
                }
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 10
                    
                    Image {
                        source: "file:///E:/MantaTools/src/assets/icons/discord.svg"
                        width: 20
                        height: 20
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        sourceSize.width: 20
                        sourceSize.height: 20
                    }
                    
                    Text {
                        text: "Join Discord"
                        color: "white"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        font.family: "Segoe UI, Arial, sans-serif"
                    }
                }
            }
        }
    }
}