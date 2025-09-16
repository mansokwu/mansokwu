import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import MantaTools 1.0
import "../components"

Item {
    id: libraryPage
    z: 0
    
    // Loading spinner - overlay di atas ScrollView
    LoadingSpinner {
        id: loadingSpinner
        anchors.fill: parent
        running: false
        text: "Sync data from Steam..."
        z: 1000
    }
    
    ScrollView {
        id: scrollView
        anchors.fill: parent
        z: 0
        
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
        
        Rectangle {
            width: scrollView.width
            color: "transparent"
            // Ensure ScrollView gets a proper implicit content height with extra space for pagination
            implicitHeight: layoutRoot.implicitHeight + 20
            
            Column {
                id: layoutRoot
                anchors.fill: parent
                anchors.margins: 24
                anchors.bottomMargin: 20  // Extra space untuk pagination
                spacing: 8
                
                // Library content
                Column {
                    width: parent.width
                    spacing: 12
                    
                    // Results count
                    Text {
                        text: allItems.length > 0 ? allItems.length + " games found" : ""
                        color: mainWindow.textMuted
                        font.pixelSize: 13
                        font.weight: 500
                    }
                    
                    // Library items list
                    Column {
                        width: parent.width
                        spacing: 16
                        visible: currentPageItems.length > 0
                        
                        property real cardWidth: width
                        
                        Repeater {
                            model: currentPageItems
                            delegate: gameCardComponent
                        }
                    }
                    
                    // Empty state (only show when no games)
                    Rectangle {
                        width: parent.width
                        height: 200
                        color: mainWindow.darkBg
                        radius: 12
                        visible: allItems.length === 0 && !isSyncing
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 16
                            
                            Text {
                                text: "📚"
                                color: mainWindow.textMuted
                                font.pixelSize: 48
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            
                            Text {
                                text: "Your library is empty.\nClick 'Sync My Library' to load your Steam games."
                                color: mainWindow.textMuted
                                font.pixelSize: 14
                                font.weight: 400
                                horizontalAlignment: Text.AlignHCenter
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                    
                    // Pagination - sama seperti GameListPage
                    Item {
                        width: parent.width
                        height: 35
                        visible: allItems.length > 0
                        
                        RowLayout {
                            anchors.fill: parent
                            spacing: 12
                            
                            Text {
                                id: pageLabel
                                text: "Page 1 / 1  |  0 results"
                                color: mainWindow.textMuted
                                font.pixelSize: 13
                                font.weight: 500
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            CustomButton {
                                id: prevButton
                                text: "Previous"
                                enabled: currentPage > 1
                                height: 36
                                width: 90
                                buttonColor: enabled ? mainWindow.buttonSecondary : mainWindow.buttonPrimary
                                hoverColor: enabled ? mainWindow.buttonSecondaryHover : mainWindow.buttonPrimaryHover
                                pressedColor: enabled ? mainWindow.buttonSecondaryPressed : mainWindow.buttonPrimaryPressed
                                textColor: enabled ? mainWindow.buttonText : mainWindow.buttonTextSecondary
                                
                                onClicked: {
                                    if (enabled) prevPage()
                                }
                            }
                            
                            CustomButton {
                                id: nextButton
                                text: "Next"
                                enabled: currentPage < totalPages
                                height: 36
                                width: 90
                                buttonColor: enabled ? mainWindow.buttonSecondary : mainWindow.buttonPrimary
                                hoverColor: enabled ? mainWindow.buttonSecondaryHover : mainWindow.buttonPrimaryHover
                                pressedColor: enabled ? mainWindow.buttonSecondaryPressed : mainWindow.buttonPrimaryPressed
                                textColor: enabled ? mainWindow.buttonText : mainWindow.buttonTextSecondary
                                
                                onClicked: {
                                    if (enabled) nextPage()
                                }
                            }
                        }
                    }
                    
                    // Extra spacer untuk memastikan pagination tidak terpotong
                    Item {
                        width: parent.width
                        height: 10
                        visible: allItems.length > 0
                    }
                }
            }
        }
    }
    
    signal openGame(string title, int appid)
    signal syncStateChanged(bool hasBeenSynced)
    signal refreshPatchStatus(int appid)
    
    property var qmlBridge: null
    property var header: null
    
    onQmlBridgeChanged: {
        if (qmlBridge) {
            qmlBridge.librarySyncStarted.connect(onLibrarySyncStarted)
            qmlBridge.librarySyncProgress.connect(onLibrarySyncProgress)
            qmlBridge.librarySyncGameProgress.connect(onLibrarySyncGameProgress)
            qmlBridge.librarySyncFinished.connect(onLibrarySyncFinished)
        }
    }
    
    // Connect to Steam API signals for metadata updates
    Connections {
        target: qmlBridge && qmlBridge.steamApi ? qmlBridge.steamApi : null
        function onMetaCacheUpdated() {
            // Trigger bindings to re-evaluate genre text
            libraryPage.metaTick = (libraryPage.metaTick + 1) % 1000000
        }
    }
    
    // Listen for refresh patch status requests
    onRefreshPatchStatus: function(appid) {
        refreshPatchStatusForGame(appid)
    }
    property string searchText: ""
    property var filteredItems: []
    property bool isSyncing: false
    property bool isSearching: false
    property int syncProgress: 0
    property int syncTotal: 0
    property int syncGameProgress: 0
    property int syncGameTotal: 0
    property string currentGameName: ""
    // Tick to refresh bindings when metadata cache updates
    property int metaTick: 0
    // Track if library has been synced at least once
    property bool hasBeenSynced: false
    
    // Library data from Steam
    property var allItems: []
    
    // Pagination properties
    property int currentPage: 1
    property int pageSize: 25
    property int totalPages: 1
    property var currentPageItems: []
    
    function filterItems(text) {
        isSearching = true
        searchText = text || ""
        currentPage = 1
        loadCurrentPage()
    }
    
    function loadCurrentPage() {
        console.log("Loading current page:", currentPage, "searchText:", searchText)
        
        if (searchText.length === 0) {
            currentPageItems = allItems
        } else {
            var filtered = []
            for (var i = 0; i < allItems.length; i++) {
                if (allItems[i].title.toLowerCase().indexOf(searchText.toLowerCase()) !== -1) {
                    filtered.push(allItems[i])
                }
            }
            currentPageItems = filtered
        }
        
        // Calculate pagination
        totalPages = Math.max(1, Math.ceil(currentPageItems.length / pageSize))
        currentPage = Math.min(Math.max(1, currentPage), totalPages)
        
        // Get items for current page
        var startIndex = (currentPage - 1) * pageSize
        var endIndex = Math.min(startIndex + pageSize, currentPageItems.length)
        currentPageItems = currentPageItems.slice(startIndex, endIndex)
        
        console.log("totalItems:", currentPageItems.length, "totalPages:", totalPages, "currentPage:", currentPage)
        renderPage()
    }
    
    function renderPage() {
        console.log("Rendering page with", currentPageItems.length, "items")
        pageLabel.text = `Page ${currentPage} / ${totalPages}  |  ${currentPageItems.length} results`
        prevButton.enabled = currentPage > 1
        nextButton.enabled = currentPage < totalPages
    }
    
    function prevPage() {
        if (currentPage > 1) {
            currentPage--
            loadCurrentPage()
        }
    }
    
    function nextPage() {
        if (currentPage < totalPages) {
            currentPage++
            loadCurrentPage()
        }
    }
    
    function clearSearch() {
        searchText = ""
        currentPage = 1
        loadCurrentPage()
    }
    
    function syncSteamLibrary() {
        if (qmlBridge && qmlBridge.steamApi) {
            console.log("Starting Steam library sync...")
            isSyncing = true
            syncProgress = 0
            syncTotal = 0
            
            // Use async sync function
            qmlBridge.steamApi.syncUserLibrary()
        } else {
            console.log("QML Bridge or Steam API not available")
            isSyncing = false
        }
    }
    
    function onLibrarySyncStarted() {
        console.log("Library sync started")
        isSyncing = true
        syncProgress = 0
        syncTotal = 0
        loadingSpinner.running = true
        if (header) {
            header.setLibrarySyncing(true)
        }
    }
    
    function onLibrarySyncProgress(current, total) {
        console.log("Library sync progress:", current, "/", total)
        syncProgress = current
        syncTotal = total
    }
    
    function onLibrarySyncGameProgress(current, total, gameName) {
        console.log("Library sync game progress:", current, "/", total, "-", gameName)
        syncGameProgress = current
        syncGameTotal = total
        currentGameName = gameName
    }
    
    function onLibrarySyncFinished(userLibrary) {
        console.log("Library sync finished")
        isSyncing = false
        syncProgress = 0
        syncTotal = 0
        loadingSpinner.running = false
        
        // Mark as synced
        hasBeenSynced = true
        syncStateChanged(hasBeenSynced)
        
        if (header) {
            header.setLibrarySyncing(false)
        }
        
        if (userLibrary && userLibrary.length > 0) {
            allItems = userLibrary
            loadCurrentPage()
            console.log("Steam library synced:", allItems.length, "games found")
        } else {
            console.log("No games found in your Steam library")
            allItems = []
            currentPageItems = []
        }
    }
    
    function loadSteamLibrary() {
        if (qmlBridge && qmlBridge.steamApi) {
            console.log("Loading Steam library...")
            isSyncing = true
            
            // Get user's Steam library (games added via MantaTools)
            var userLibrary = qmlBridge.steamApi.getUserLibrary()
            if (userLibrary && userLibrary.length > 0) {
                allItems = userLibrary
                loadCurrentPage()
                console.log("Library loaded:", allItems.length, "games found")
            } else {
                allItems = []
                currentPageItems = []
                console.log("Library loaded (empty)")
            }
            
            isSyncing = false
        }
    }
    
    function refreshLibrary() {
        if (hasBeenSynced) {
            console.log("Refreshing library and scanning patches...")
            
            // Set refreshing state
            if (header) {
                header.setRefreshing(true)
            }
            
            // Reset scan states for all game cards
            metaTick = (metaTick + 1) % 1000000
            // Reload current page
            loadCurrentPage()
            // Trigger patch scan for all visible games
            triggerPatchScanForVisibleGames()
            
            // Reset refreshing state after a delay
            refreshTimer.start()
        } else {
            // If never synced, do full sync
            syncSteamLibrary()
        }
    }
    
    function triggerPatchScanForVisibleGames() {
        // Scan patches for all games on current page with staggered timing
        var gamesToScan = []
        for (var i = 0; i < currentPageItems.length; i++) {
            var game = currentPageItems[i]
            if (game && game.appid > 0) {
                gamesToScan.push(game.appid)
            }
        }
        
        // Start staggered scanning
        if (gamesToScan.length > 0) {
            scanIndex = 0
            scanGamesList = gamesToScan
            scanTimer.start()
        }
    }
    
    function refreshPatchStatusForGame(appid) {
        // Refresh patch status for a specific game
        if (appid > 0 && qmlBridge && qmlBridge.steamApi) {
            console.log("Refreshing patch status for AppID:", appid)
            qmlBridge.steamApi.startPatchScan(appid)
        }
    }
    
    // Properties for staggered scanning
    property int scanIndex: 0
    property var scanGamesList: []
    
    // Timer for staggered patch scanning
    Timer {
        id: scanTimer
        interval: 200  // 200ms delay between each scan
        repeat: true
        onTriggered: {
            if (scanIndex < scanGamesList.length) {
                var appid = scanGamesList[scanIndex]
                if (qmlBridge && qmlBridge.steamApi) {
                    console.log("Triggering patch scan for AppID:", appid, "index:", scanIndex)
                    qmlBridge.steamApi.startPatchScan(appid)
                }
                scanIndex++
            } else {
                // All games scanned, stop timer
                scanTimer.stop()
                scanIndex = 0
                scanGamesList = []
            }
        }
    }
    
    // Timer to reset refreshing state
    Timer {
        id: refreshTimer
        interval: 3000  // 3 seconds delay to allow patch scans to complete
        onTriggered: {
            if (header) {
                header.setRefreshing(false)
            }
        }
    }
    
    
    Component.onCompleted: {
        loadSteamLibrary()
    }
    
    // Game card component (same as GameListPage)
    Component {
        id: gameCardComponent
        
        Rectangle {
            id: gameCard
            // Bind to data from Repeater model
            property string title: (typeof modelData !== 'undefined' && modelData && modelData.title) ? modelData.title : ""
            property int appid: (typeof modelData !== 'undefined' && modelData && modelData.appid) ? modelData.appid : 0
            property bool installed: (typeof modelData !== 'undefined' && modelData && modelData.installed) ? modelData.installed : false
            property bool hovered: false
            property bool pressed: false
            // Patch status properties
            property string patchStatus: ""
            property string patchStatusVariant: "ok"  // "ok", "warn", "error"
            property bool isScanning: false
            property bool hasScanned: false
            
            signal clicked(string title, int appid)
            
            // Functions
            function scanPatch() {
                if (appid && qmlBridge && qmlBridge.steamApi && !isScanning) {
                    // Set scanning state
                    isScanning = true
                    hasScanned = true
                    
                    // Reset patch status
                    patchStatus = ""
                    patchStatusVariant = "ok"
                    
                    // Start timeout timer
                    scanTimeoutTimer.start()
                    
                    // Start scan
                    qmlBridge.steamApi.startPatchScan(appid)
                }
            }
            
            // Debounced scan function
            function debouncedScan() {
                if (scanTimer.running) {
                    scanTimer.restart()
                } else {
                    scanTimer.start()
                }
            }
            
            // Adaptive width based on container
            width: (parent && parent.cardWidth) ? parent.cardWidth : (parent ? parent.width : libraryPage.width)
            height: 100
            color: hovered ? mainWindow.hoverCard : mainWindow.cardBg
            border.color: hovered ? mainWindow.hoverBorder : mainWindow.border
            border.width: 1
            radius: 8
            
            // Enhanced responsive animations
            scale: hovered ? 1.01 : 1.0
            z: hovered ? 10 : 1
            
            // Responsive behaviors
            Behavior on scale { 
                NumberAnimation { 
                    duration: 80
                    easing.type: Easing.OutQuad 
                } 
            }
            Behavior on color { 
                ColorAnimation { 
                    duration: 100
                    easing.type: Easing.OutQuad
                } 
            }
            Behavior on z { 
                NumberAnimation { 
                    duration: 80
                    easing.type: Easing.OutQuad
                } 
            }
            
            visible: true
            
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    gameCard.clicked(gameCard.title, gameCard.appid)
                    // Bubble to page-level signal so main.qml can open detail
                    libraryPage.openGame(gameCard.title, gameCard.appid)
                }
                cursorShape: Qt.PointingHandCursor
                onEntered: { gameCard.hovered = true }
                onExited: { gameCard.hovered = false }
                onPressed: { gameCard.pressed = true }
                onReleased: { gameCard.pressed = false }
            }
            
            // Debounce timer for scanning
            Timer {
                id: scanTimer
                interval: 500  // 500ms debounce
                onTriggered: scanPatch()
            }
            
            // Timeout timer for scanning (prevent infinite scanning)
            Timer {
                id: scanTimeoutTimer
                interval: 10000  // 10 seconds timeout
                onTriggered: {
                    if (isScanning) {
                        isScanning = false
                        patchStatus = "Timeout"
                        patchStatusVariant = "error"
                    }
                }
            }
            
            // Listen for patch status updates
            Connections {
                target: qmlBridge ? qmlBridge : null
                function onPatchStatusUpdated(status, variant) {
                    // Note: This signal doesn't include appid, so we need to check if this is for current game
                    // For now, we'll update all game cards when any patch status is received
                    // This is a limitation since the signal doesn't include appid
                    if (isScanning) {
                        isScanning = false
                        scanTimeoutTimer.stop()  // Stop timeout timer
                        patchStatus = status
                        patchStatusVariant = variant
                    }
                }
            }
            
            // Auto-scan patch status when game card is created
            Component.onCompleted: {
                if (appid > 0 && !hasScanned) {
                    debouncedScan()
                }
            }
            
            // Re-scan when appid changes (e.g., when switching pages)
            onAppidChanged: {
                if (appid > 0 && hasScanned) {
                    hasScanned = false
                    debouncedScan()
                }
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 20
                
                // Game image
                Rectangle {
                    // Steam header aspect ratio ~ 460x215
                    property real headerAspect: 460/215
                    // Jaga agar gambar selalu muat dalam kartu: tinggi dibatasi
                    property real headerHeight: Math.min(70, Math.max(50, gameCard.height - 30))
                    height: headerHeight
                    width: Math.round(headerHeight * headerAspect)
                    color: "transparent"
                    radius: 8
                    clip: true
                    
                    Image {
                        id: gameImage
                        anchors.fill: parent
                        // Keep binding to appid and toggle between primary/alt host
                        property bool useAltSource: false
                        source: useAltSource
                            ? `https://steamcdn-a.akamaihd.net/steam/apps/${gameCard.appid}/header.jpg`
                            : `https://cdn.akamai.steamstatic.com/steam/apps/${gameCard.appid}/header.jpg`
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        asynchronous: true
                        cache: true
                        
                        // Reset fallback when appid changes (keeps source in sync)
                        Connections {
                            target: gameCard
                            function onAppidChanged() {
                                gameImage.useAltSource = false
                            }
                        }
                        
                        onStatusChanged: {
                            if (status === Image.Error && !useAltSource) {
                                useAltSource = true
                            }
                        }
                    }
                }
                
                // Game info
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 8
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        
                        Text {
                            text: gameCard.title
                            color: mainWindow.textPrimary
                            font.weight: 700
                            font.pixelSize: 14
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                            maximumLineCount: 2
                            elide: Text.ElideRight
                        }
                        
                        // Clean patch status badge
                        Rectangle {
                            id: patchStatusBadge
                            Layout.preferredWidth: Math.max(100, patchStatusText.implicitWidth + 24)
                            Layout.preferredHeight: 28
                            
                            // Button-like styling
                            color: mainWindow.darkBg
                            border.color: mainWindow.buttonBorder
                            border.width: 1
                            radius: 8
                            visible: patchStatus !== "" || isScanning
                            
                            // Modern shadow effect like buttons
                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: -1
                                color: "transparent"
                                border.color: mainWindow.buttonBorder
                                border.width: 1
                                radius: 9
                                opacity: 0.15
                                z: -1
                            }
                            
                            // Button-like hover effect
                            property bool hovered: false
                            
                            // Smooth color transition
                            Behavior on color {
                                ColorAnimation { duration: 100; easing.type: Easing.OutQuad }
                            }
                            Behavior on scale {
                                NumberAnimation { duration: 80; easing.type: Easing.OutQuad }
                            }
                            
                            // Scale effect on hover
                            scale: hovered ? 1.01 : 1.0
                            
                            // Text shadow like buttons
                            Text {
                                anchors.centerIn: parent
                                anchors.horizontalCenterOffset: 1
                                anchors.verticalCenterOffset: 1
                                text: patchStatusText.text
                                color: "#000000"
                                opacity: 0.3
                                font.pixelSize: 12
                                font.weight: Font.Demi
                                z: -1
                            }
                            
                            Text {
                                id: patchStatusText
                                anchors.centerIn: parent
                                text: {
                                    if (isScanning) return "⏳ Scanning..."
                                    if (patchStatusVariant === "warn") {
                                        // Replace "Unpatched" with "Update Available"
                                        var statusText = patchStatus
                                        if (statusText.indexOf("Unpatched") !== -1) {
                                            statusText = statusText.replace("Unpatched", "Update Available")
                                        }
                                        return "⚠️ " + statusText
                                    }
                                    if (patchStatusVariant === "error") return "❌ " + patchStatus
                                    return "✅ " + patchStatus
                                }
                                color: mainWindow.buttonText
                                font.pixelSize: 12
                                font.weight: Font.Demi
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            // MouseArea for hover effect
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                
                                onEntered: patchStatusBadge.hovered = true
                                onExited: patchStatusBadge.hovered = false
                            }
                            
                            // Simple scale animation for scanning state
                            SequentialAnimation on scale {
                                running: isScanning
                                loops: Animation.Infinite
                                NumberAnimation { to: 1.02; duration: 800; easing.type: Easing.InOutQuad }
                                NumberAnimation { to: 1.0; duration: 800; easing.type: Easing.InOutQuad }
                            }
                        }
                    }
                    
                    // Installation status line
                    Text {
                        text: gameCard.installed ? "Installed" : "Not Installed"
                        color: gameCard.installed ? mainWindow.success : mainWindow.error
                        font.pixelSize: 11
                        font.weight: 500
                        Layout.fillWidth: true
                    }
                    
                    RowLayout {
                        spacing: 8
                        Text {
                            text: `AppID: ${gameCard.appid}`
                            color: mainWindow.textTertiary
                            font.pixelSize: 11
                            font.weight: 500
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
}