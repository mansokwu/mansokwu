import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: toastManager
    anchors.fill: parent
    z: 2000
    
    // Properties
    property int maxToasts: 4
    property int toastSpacing: 8
    property int toastDuration: 2500
    
    // Toast list
    property var toastList: []
    
    // Functions
    function showToast(message, type, duration) {
        console.log("ToastManager: Creating toast with message:", message)
        
        var toastComponent = Qt.createComponent("ToastNotification.qml")
        if (toastComponent.status === Component.Ready) {
            var toast = toastComponent.createObject(toastManager)
            if (toast) {
                // Position toast at top-right
                var targetX = toastManager.width - toast.width - 16 // 16px margin from right
                var targetY = calculateToastY()
                
                // Set position
                toast.x = targetX
                toast.y = targetY
                
                // Configure toast
                toast.show(message, type, duration || toastDuration)
                
                // Add to list
                toastList.push(toast)
                
                // Remove from list when hidden
                toast.isVisibleChanged.connect(function() {
                    if (!toast.isVisible) {
                        removeToast(toast)
                    }
                })
                
                // Limit number of toasts
                if (toastList.length > maxToasts) {
                    var oldestToast = toastList.shift()
                    if (oldestToast) {
                        oldestToast.hide()
                    }
                }
                
                // Reposition all toasts
                repositionToasts()
                
                console.log("ToastManager: Toast created successfully at", targetX, targetY)
            } else {
                console.log("ToastManager: Failed to create toast object")
            }
        } else {
            console.log("ToastManager: Failed to create toast component:", toastComponent.errorString())
        }
    }
    
    function calculateToastY() {
        var y = 16 // Top margin
        for (var i = 0; i < toastList.length; i++) {
            if (toastList[i] && toastList[i].isVisible) {
                y += toastList[i].height + toastSpacing
            }
        }
        return y
    }
    
    function repositionToasts() {
        var y = 16 // Top margin
        for (var i = 0; i < toastList.length; i++) {
            if (toastList[i] && toastList[i].isVisible) {
                // Position at top-right
                toastList[i].x = toastManager.width - toastList[i].width - 16 // 16px margin from right
                toastList[i].y = y
                y += toastList[i].height + toastSpacing
            }
        }
    }
    
    function removeToast(toast) {
        var index = toastList.indexOf(toast)
        if (index !== -1) {
            toastList.splice(index, 1)
            toast.destroy()
            repositionToasts()
        }
    }
    
    function clearAll() {
        for (var i = 0; i < toastList.length; i++) {
            if (toastList[i]) {
                toastList[i].hide()
            }
        }
        toastList = []
    }
}