import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: settingsCard
    property string title: ""
    property string hint: ""
    
    Layout.fillWidth: true
    color: mainWindow.cardBg
    border.color: mainWindow.border
    border.width: 1
    radius: 14
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: settingsCard.title
                color: mainWindow.textPrimary
                font.weight: Font.Black
                font.pixelSize: 15
                font.letterSpacing: 0.2
            }
            
            Item { Layout.fillWidth: true }
        }
        
        // Hint
        Text {
            text: settingsCard.hint
            color: mainWindow.textMuted
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Content
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
