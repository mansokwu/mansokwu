import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: customTextField
    
    property alias text: textInput.text
    property alias placeholderText: placeholder.text
    property color fieldColor: mainWindow.cardBg
    property color borderColor: mainWindow.border
    property color textColor: mainWindow.textPrimary
    property int fieldRadius: 8
    
    color: fieldColor
    border.color: borderColor
    border.width: 1
    radius: fieldRadius
    
    // Ensure border is not clipped
    clip: false
    
    TextInput {
        id: textInput
        anchors.fill: parent
        anchors.margins: 10
        color: textColor
        font.pixelSize: 14
        font.weight: 400
        selectByMouse: true
        verticalAlignment: TextInput.AlignVCenter
        
        onTextChanged: {
            if (customTextField.textChangedSignal) {
                customTextField.textChangedSignal()
            }
        }
    }
    
    Text {
        id: placeholder
        anchors.fill: textInput
        anchors.margins: 10
        color: mainWindow.textTertiary
        font.pixelSize: 14
        font.weight: 400
        verticalAlignment: Text.AlignVCenter
        visible: textInput.text.length === 0
    }
    
    signal textChangedSignal()
}
