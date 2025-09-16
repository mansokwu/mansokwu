import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

RowLayout {
    id: pathRow
    property string label: ""
    property alias field: textField
    property alias text: textField.text
    property string placeholder: ""
    
    signal browse()
    
    Layout.fillWidth: true
    
    Text {
        text: pathRow.label
        color: "#8b949e"
        font.pixelSize: 12
        Layout.preferredWidth: 130
    }
    
    CustomTextField {
        id: textField
        placeholderText: pathRow.placeholder
        Layout.fillWidth: true
        Layout.preferredHeight: 40
        fieldColor: "#121722"
        borderColor: "#30363d"
        textColor: "#f0f6fc"
        fieldRadius: 10
    }
    
    CustomButton {
        text: "Browse…"
        Layout.preferredHeight: 40
        Layout.preferredWidth: 80
        buttonColor: "#0a0a0a"
        hoverColor: "#1a1a1a"
        pressedColor: "#2a2a2a"
        textColor: "#f0f6fc"
        buttonRadius: 10
        onClicked: pathRow.browse()
    }
}
