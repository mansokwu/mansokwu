import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import MantaTools 1.0
import "../components"

ScrollView {
    id: gameDetailPage
    z: 0
    
    // OptionMenuItem component - Like Photo Design
    Component {
        id: optionMenuItemComponent
        
        Rectangle {
            id: optionItem
            property string icon: ""
            property string text: ""
            property bool isDangerous: false
            property bool showSeparator: true
            
            signal clicked()
            
            width: parent.width
            height: 40
            color: mouseArea.containsMouse ? mainWindow.hoverPrimary : "transparent"
            
            Behavior on color {
                ColorAnimation { duration: 100; easing.type: Easing.OutCubic }
            }
            
            Row {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                anchors.topMargin: 8
                anchors.bottomMargin: 8
                spacing: 12
                
                Image {
                    source: optionItem.icon
                    width: 16
                    height: 16
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    sourceSize.width: 16
                    sourceSize.height: 16
                }
                
                Text {
                    text: optionItem.text
                    color: isDangerous ? "#f85149" : "#f0f6fc"
                    font.pixelSize: 14
                    font.weight: 400
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                }
            }
            
            // Separator line
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 1
                color: "#2a2f36"
                visible: optionItem.showSeparator
            }
            
            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: optionItem.clicked()
            }
        }
    }
    
    // Tampilkan scrollbar modern saat diperlukan
    ScrollBar.horizontal.policy: ScrollBar.AsNeeded
    ScrollBar.vertical.policy: ScrollBar.AsNeeded
    
    // Styling modern untuk scrollbar
    ScrollBar.vertical {
        id: verticalScrollBar
        width: 8
        active: true
        policy: ScrollBar.AsNeeded
        
        background: Rectangle {
            color: mainWindow.darkBg
            radius: 4
        }
        
        contentItem: Rectangle {
            color: verticalScrollBar.pressed ? mainWindow.accent : (verticalScrollBar.hovered ? mainWindow.hoverSecondary : mainWindow.border)
            radius: 4
            
            Behavior on color {
                ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
            }
        }
    }
    
    ScrollBar.horizontal {
        id: horizontalScrollBar
        height: 8
        active: true
        policy: ScrollBar.AsNeeded
        
        background: Rectangle {
            color: mainWindow.darkBg
            radius: 4
        }
        
        contentItem: Rectangle {
            color: horizontalScrollBar.pressed ? mainWindow.accent : (horizontalScrollBar.hovered ? mainWindow.hoverSecondary : mainWindow.border)
            radius: 4
            
            Behavior on color {
                ColorAnimation { duration: 150; easing.type: Easing.OutCubic }
            }
        }
    }
    
    // Properties
    property string currentTitle: ""
    property int currentAppid: 0
    property bool isLoading: false
    property var qmlBridge: null
    // Add-to-Steam progress state
    property bool isAdding: false
    property int addToSteamProgress: -1    // -1: hidden, 0..100: progress
    property string addToSteamStatus: ""
    // Track if game has been added to Steam
    property bool gameAddedToSteam: false
    
    // Signals
    signal openGame(string title, int appid)
    signal backRequested()
    
    // Functions
    function showGame(title, appid) {
        currentTitle = title
        currentAppid = appid
        gameInfoLabel.text = `${appid} | ${title}`
        // Reset add-to-steam state when switching games
        isAdding = false
        addToSteamProgress = -1
        addToSteamStatus = ""
        gameAddedToSteam = false
        
        // Load banner image
        loadBannerImage(appid)
        
        // Load game details
        loadGameDetails(appid)
        
    }
    
    function loadBannerImage(appid) {
        if (appid > 0) {
            bannerImage.source = `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/library_hero.jpg`
        } else {
            bannerImage.source = ""
        }
    }
    
    function loadGameDetails(appid) {
        if (qmlBridge && qmlBridge.steamApi) {
            console.log("qml: requesting game details for", appid)
            qmlBridge.steamApi.loadGameDetails(appid)
        }
    }
    
    function addToSteam() {
        if (currentAppid && qmlBridge && qmlBridge.steamApi) {
            isAdding = true
            addToSteamProgress = 0
            addToSteamStatus = "Starting…"
            qmlBridge.steamApi.addGameToSteam(currentAppid)
            // Show toast notification
            if (mainWindow && mainWindow.showSnack) {
                mainWindow.showSnack("Menambahkan game ke Steam...", "info", 2000)
            }
        }
    }
    
    function restartSteam() {
        if (qmlBridge && qmlBridge.steamApi) {
            qmlBridge.steamApi.restartSteam()
            // Show toast notification
            if (mainWindow && mainWindow.showSnack) {
                mainWindow.showSnack("Steam sedang direstart...", "info", 2000)
            }
        }
    }
    
    function openGameFolder() {
        if (currentAppid && qmlBridge && qmlBridge.steamApi) {
            qmlBridge.steamApi.openGameFolder(currentAppid)
        }
    }
    
    function removeGame() {
        if (currentAppid && qmlBridge && qmlBridge.steamApi) {
            // Show loading notification
            if (mainWindow && mainWindow.showSnack) {
                mainWindow.showSnack("Menghapus file game...", "info", 2000)
            }
            qmlBridge.steamApi.removeGame(currentAppid)
        }
    }
    
    function updateGame() {
        if (currentAppid && qmlBridge && qmlBridge.steamApi) {
            qmlBridge.steamApi.updateGame(currentAppid)
            // Show toast notification
            if (mainWindow && mainWindow.showSnack) {
                mainWindow.showSnack("Game sedang diupdate...", "info", 2000)
            }
        }
    }
    
    
    
    // Main content
    Rectangle {
        width: gameDetailPage.width
        color: "transparent"
        clip: true
        implicitHeight: layoutRoot.implicitHeight

        ColumnLayout {
            id: layoutRoot
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 0
        
        // Header with back button and game info (above banner)
        Rectangle {
            id: headerContainer
            height: 52
            Layout.fillWidth: true
            color: "transparent"
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 0
                anchors.topMargin: 0
                anchors.bottomMargin: 0
                spacing: 16
                
                // Back button
                CustomButton {
                    id: backBtn
                    text: "←"
                    Layout.preferredWidth: 40
                    Layout.preferredHeight: 40
                    buttonColor: mainWindow.buttonSecondary
                    hoverColor: mainWindow.buttonSecondaryHover
                    pressedColor: mainWindow.buttonSecondaryPressed
                    textColor: mainWindow.buttonText
                    buttonRadius: 8
                    font.pixelSize: 18
                    font.weight: 700
                    onClicked: gameDetailPage.backRequested()
                }
                
                // Game title and AppID
                Text {
                    id: gameInfoLabel
                    text: "AppID | Game Title"
                    color: "#f0f6fc"
                    font.weight: 600
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                
            }
        }
        
        
        // Hero banner
        Rectangle {
            id: bannerContainer
            height: 380
            Layout.fillWidth: true
            color: mainWindow.darkBg
            radius: 12
            border.color: mainWindow.border
            border.width: 1
            
            Image {
                id: bannerImage
                anchors.fill: parent
                source: ""
                fillMode: Image.PreserveAspectCrop
                smooth: true
                
                onStatusChanged: {
                    if (status === Image.Error) {
                        source = ""
                    }
                }
            }
            
            Text {
                anchors.centerIn: parent
                text: "Loading..."
                color: "#8b949e"
                font.pixelSize: 13
                font.weight: 600
                visible: bannerImage.status === Image.Loading
            }
            
            
            
            // Subtle top gradient for readability (no external effects)
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 80
                radius: bannerContainer.radius
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#80000000" }
                    GradientStop { position: 1.0; color: "#00000000" }
                }
            }
            
            // (DLC panel moved below buttons)
        }
        
        // Action buttons below banner (not overlay)
        RowLayout {
            id: actionsRow
            Layout.fillWidth: true
            Layout.leftMargin: 0
            Layout.rightMargin: 16
            Layout.topMargin: 16
            spacing: 10

            // Filler di kiri agar tombol terdorong ke kanan
            Item { Layout.fillWidth: true }
            
            CustomButton {
                id: addToSteamBtn
                Layout.preferredWidth: 160
                Layout.preferredHeight: 40
                buttonColor: gameAddedToSteam ? mainWindow.buttonSuccess : mainWindow.buttonAccent
                hoverColor: gameAddedToSteam ? mainWindow.buttonSuccessHover : mainWindow.buttonAccentHover
                pressedColor: gameAddedToSteam ? mainWindow.buttonSuccessPressed : mainWindow.buttonAccentPressed
                textColor: mainWindow.buttonText
                buttonRadius: 8
                progress: isAdding ? addToSteamProgress : -1
                progressColor: mainWindow.buttonSuccess
                enabled: !isAdding
                onClicked: {
                    if (gameAddedToSteam) {
                        console.log("qml: Restart Steam clicked for", currentAppid)
                        restartSteam()
                    } else {
                        console.log("qml: Add to Steam clicked for", currentAppid)
                        addToSteam()
                    }
                }
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 8
                    
                    Image {
                        source: gameAddedToSteam ? "file:///E:/MantaTools/src/assets/icons/restart_steam.svg" : "file:///E:/MantaTools/src/assets/icons/add_to_steam.svg"
                        width: 16
                        height: 16
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        sourceSize.width: 16
                        sourceSize.height: 16
                    }
                    
                    Text {
                        text: isAdding ? ("Downloading " + Math.max(0, Math.min(100, addToSteamProgress)) + "%") : 
                              (gameAddedToSteam ? "Restart Steam" : "Add to Steam")
                        color: addToSteamBtn.textColor
                        font.pixelSize: 14
                        font.weight: 500
                    }
                }
            }
            
            
            CustomButton {
                id: optionsBtn
                Layout.preferredWidth: 110
                Layout.preferredHeight: 40
                buttonColor: mainWindow.buttonSecondary
                hoverColor: mainWindow.buttonSecondaryHover
                pressedColor: mainWindow.buttonSecondaryPressed
                textColor: mainWindow.buttonText
                buttonRadius: 8
                onClicked: optionsMenu.open()
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 8
                    
                    Image {
                        source: "file:///E:/MantaTools/src/assets/icons/options.svg"
                        width: 16
                        height: 16
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        sourceSize.width: 16
                        sourceSize.height: 16
                    }
                    
                    Text {
                        text: "Options"
                        color: optionsBtn.textColor
                        font.pixelSize: 14
                        font.weight: 500
                    }
                }
            }
        }




        
        
        
        // Content area
        Rectangle {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 24
                
                // Spacer
                Item { Layout.fillHeight: true }
            }
        }
        
    }
    
    }
    
    // Listen backend signals
    Connections {
        target: qmlBridge ? qmlBridge : null
        function onStatusUpdated(message) {
            console.log("qml: status:", message)
            addToSteamStatus = message
            
            // Handle remove game status updates
            if (message.includes("Berhasil hapus") || message.includes("file untuk AppID")) {
                if (mainWindow && mainWindow.showSnack) {
                    mainWindow.showSnack("Game berhasil dihapus dari Steam!", "success", 3000)
                }
            } else if (message.includes("Ditemukan") && message.includes("file untuk dihapus")) {
                if (mainWindow && mainWindow.showSnack) {
                    mainWindow.showSnack("File ditemukan, sedang menghapus...", "info", 2000)
                }
            } else if (message.includes("Tidak ada file") || message.includes("Error:")) {
                if (mainWindow && mainWindow.showSnack) {
                    mainWindow.showSnack(message, "warning", 3000)
                }
            }
        }
        function onProgressUpdated(p) {
            addToSteamProgress = Math.max(0, Math.min(100, p))
        }
        function onAddToSteamFinished(ok, message) {
            console.log("qml: addToSteam finished:", ok, message)
            addToSteamStatus = message
            addToSteamProgress = 100
            isAdding = false
            gameAddedToSteam = !!ok
            
            // Show toast notification based on result
            if (mainWindow && mainWindow.showSnack) {
                if (ok) {
                    mainWindow.showSnack("Game berhasil ditambahkan ke Steam!", "success", 3000)
                } else {
                    mainWindow.showSnack("Gagal menambahkan game ke Steam", "error", 3000)
                }
            }
        }
    }
    
    // Options menu - Like Photo Design
    Popup {
        id: optionsMenu
        x: 0
        y: 0
        width: 180
        height: optionsColumn.implicitHeight + 20
        modal: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        
        onAboutToShow: {
            var buttonRect = optionsBtn.mapToItem(gameDetailPage, 0, 0, optionsBtn.width, optionsBtn.height)
            var buttonCenterX = buttonRect.x + (optionsBtn.width / 2)
            var targetX = buttonCenterX - (optionsMenu.width / 2)
            var finalX = Math.max(16, Math.min(targetX, gameDetailPage.width - optionsMenu.width - 16))
            
            optionsMenu.x = finalX
            optionsMenu.y = buttonRect.y + buttonRect.height + 6
        }
        
        background: Rectangle {
            color: mainWindow.darkBg
            border.color: mainWindow.border
            border.width: 1
            radius: 8
        }
        
        Column {
            id: optionsColumn
            anchors.fill: parent
            spacing: 0
            
            // Restart Steam option
            Loader {
                width: parent.width
                sourceComponent: optionMenuItemComponent
                onLoaded: {
                    item.icon = "file:///E:/MantaTools/src/assets/icons/restart_steam.svg"
                    item.text = "Restart Steam"
                    item.showSeparator = true
                    item.clicked.connect(function() {
                        restartSteam()
                        optionsMenu.close()
                    })
                }
            }
            
            // Open game folder option
            Loader {
                width: parent.width
                sourceComponent: optionMenuItemComponent
                onLoaded: {
                    item.icon = "file:///E:/MantaTools/src/assets/icons/open_game_folder.svg"
                    item.text = "Open Game Folder"
                    item.showSeparator = true
                    item.clicked.connect(function() {
                        openGameFolder()
                        optionsMenu.close()
                    })
                }
            }
            
            // Update Game option
            Loader {
                width: parent.width
                sourceComponent: optionMenuItemComponent
                onLoaded: {
                    item.icon = "file:///E:/MantaTools/src/assets/icons/update_game.svg"
                    item.text = "Update Game"
                    item.showSeparator = true
                    item.clicked.connect(function() {
                        updateGame()
                        optionsMenu.close()
                    })
                }
            }
            
            
            // Remove Game option (dangerous action)
            Loader {
                width: parent.width
                sourceComponent: optionMenuItemComponent
                onLoaded: {
                    item.icon = "file:///E:/MantaTools/src/assets/icons/remove_game.svg"
                    item.text = "Remove Game"
                    item.isDangerous = true
                    item.showSeparator = false
                    item.clicked.connect(function() {
                        removeGame()
                        optionsMenu.close()
                    })
                }
            }
        }
    }
}
