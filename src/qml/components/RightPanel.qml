import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: rightPanel
    color: "#0e1117"
    border.color: "#30363d"
    border.width: 1
    radius: 16
    
    function setRequirements(minimum, recommended) {
        requirementsTabs.setRequirements(minimum, recommended)
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16
        
        // Requirements Section
        Rectangle {
            id: reqSection
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: "#30363d"
            border.width: 1
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12
                
                // Requirements Section Header
                Text {
                    text: "System Requirements"
                    color: "#f0f6fc"
                    font.weight: Font.Bold
                    font.pixelSize: 14
                    Layout.fillWidth: true
                }
                
                RequirementsTabs {
                    id: requirementsTabs
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
            }
        }
    }
}