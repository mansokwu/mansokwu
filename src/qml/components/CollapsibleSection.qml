import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: collapsibleSection
    property string title: ""
    property bool collapsed: false
    
    color: "transparent"
    Layout.fillWidth: true
    Layout.fillHeight: true
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Header
        CustomButton {
            id: headerButton
            Layout.fillWidth: true
            height: 40
            text: (collapsed ? "▸ " : "▾ ") + title
            buttonColor: "transparent"
            hoverColor: mainWindow.hoverBg
            pressedColor: mainWindow.darkBg
            textColor: mainWindow.textPrimary
            buttonRadius: 8
            
            onClicked: {
                collapsed = !collapsed
            }
        }
        
        // Content
        Rectangle {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: mainWindow.cardBg
            border.color: mainWindow.border
            border.width: 1
            radius: 8
            visible: !collapsed
            
            // Default content area - will be filled by parent
            default property alias content: contentArea.data
            
            Behavior on height {
                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
            }
        }
    }
}
