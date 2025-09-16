import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: requirementsTabs
    color: "transparent"
    
    property string minimumReq: "No data available"
    property string recommendedReq: "No data available"
    
    function setRequirements(minimum, recommended) {
        minimumReq = minimum || "No data available"
        recommendedReq = recommended || "No data available"
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 12
        
        // Tab buttons dengan background
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            color: "#0a0e1a"
            radius: 8
            border.color: "#2a2f36"
            border.width: 1
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 4
                spacing: 4
                
                CustomTabButton {
                    id: minimumTab
                    text: "Minimum"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    checked: true
                    
                    onClicked: {
                        minimumTab.checked = true
                        recommendedTab.checked = false
                    }
                }
                
                CustomTabButton {
                    id: recommendedTab
                    text: "Recommended"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    checked: false
                    
                    onClicked: {
                        minimumTab.checked = false
                        recommendedTab.checked = true
                    }
                }
            }
        }
        
        // Requirements content tanpa background/shapes
        ScrollView {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            
            // Tampilkan scrollbar modern saat diperlukan
            ScrollBar.horizontal.policy: ScrollBar.AsNeeded
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            
            // Styling modern untuk scrollbar
            ScrollBar.vertical {
                id: verticalScrollBar
                width: 6
                active: true
                policy: ScrollBar.AsNeeded
                anchors.right: parent.right
                anchors.rightMargin: 0
                
                background: Rectangle {
                    color: "#0a0e1a"
                    radius: 3
                }
                
                contentItem: Rectangle {
                    color: verticalScrollBar.pressed ? mainWindow.accent : (verticalScrollBar.hovered ? mainWindow.hoverSecondary : mainWindow.border)
                    radius: 3
                    
                    Behavior on color {
                        ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
                    }
                }
            }
            
            ScrollBar.horizontal {
                id: horizontalScrollBar
                height: 6
                active: true
                policy: ScrollBar.AsNeeded
                
                background: Rectangle {
                    color: "#0a0e1a"
                    radius: 3
                }
                
                contentItem: Rectangle {
                    color: horizontalScrollBar.pressed ? mainWindow.accent : (horizontalScrollBar.hovered ? mainWindow.hoverSecondary : mainWindow.border)
                    radius: 3
                    
                    Behavior on color {
                        ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
                    }
                }
            }
            
            Text {
                id: contentText
                width: parent.width
                text: "<div style='color:#8b949e; font-size:12px; line-height:1.6em; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;'>" +
                      (minimumTab.checked ? requirementsTabs.minimumReq : requirementsTabs.recommendedReq) +
                      "</div>"
                textFormat: Text.RichText
                wrapMode: Text.WordWrap
            }
        }
    }
}