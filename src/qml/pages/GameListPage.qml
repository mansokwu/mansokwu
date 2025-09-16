import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import MantaTools 1.0
import "../components"

Item {
    id: gameListPage
    z: 0
    
    // Loading spinner - overlay di atas ScrollView
    LoadingSpinner {
        id: loadingSpinner
        anchors.fill: parent
        running: false
        text: "load data from Steam..."
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
            clip: true
            implicitHeight: layoutRoot.implicitHeight + 20
            
            Column {
            id: layoutRoot
            anchors.fill: parent
            anchors.margins: 24
            anchors.bottomMargin: 20  // Extra space untuk pagination
            spacing: 8

            // Spacer di bawah header agar ada jarak kecil saat di posisi paling atas
            Item { width: parent.width; height: 1 }
            
            // Page content (header & search handled by global Header)
            
            // Loading indicator
            Rectangle {
                width: parent.width
                height: 50
                color: "transparent"
                visible: isLoading
                
                Row {
                    anchors.centerIn: parent
                    spacing: 12
                    
                    BusyIndicator {
                        running: isLoading
                        width: 24
                        height: 24
                    }
                    
                    Text {
                        text: "Loading games from Steam API..."
                        color: "#b0b0b0"
                        font.pixelSize: 14
                        font.weight: 500
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
            
            // Empty state
            
            // Cards container (vertical-only list)
            Column {
                id: cardsContainer
                width: parent.width
                spacing: 16
                visible: !isLoading
                
                property real cardWidth: width
                
                Repeater {
                    id: gamesRepeater
                    // Enforce 25 items per page even if backend returns more
                    model: currentPageGames.slice(0, pageSize)
                    delegate: gameCardComponent
                    
                }
            }
            
            // Pagination - kembali ke dalam Column dengan spacing yang cukup
            Item {
                width: parent.width
                height: 35
                visible: !isLoading && currentPageGames.length > 0
                
                RowLayout {
                    anchors.fill: parent
                    spacing: 12
                    
                    Component.onCompleted: {
                        console.log("Pagination Component.onCompleted - visible:", visible)
                    }
                    
                    Text {
                        id: pageLabel
                        text: "Page 1 / 1  |  0 results"
                        color: "#8b949e"
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
                        
                        onEnabledChanged: {
                            console.log("prevButton enabled changed to:", enabled)
                        }
                        
                        onClicked: {
                            console.log("prevButton clicked, enabled:", enabled)
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
                        
                        onEnabledChanged: {
                            console.log("nextButton enabled changed to:", enabled)
                        }
                        
                        onClicked: {
                            console.log("nextButton clicked, enabled:", enabled)
                            if (enabled) nextPage()
                        }
                    }
                }
            }
            
            // Extra spacer untuk memastikan pagination tidak terpotong
            Item {
                width: parent.width
                height: 10
                visible: !isLoading && currentPageGames.length > 0
            }
            }
        }
    }
    
    signal openGame(string title, int appid)
    
    property var qmlBridge: null
    
    // Game list properties
    property string searchText: ""
    property int currentPage: 1
    property int pageSize: 25
    property int totalPages: 1
    property int totalGames: 0
    property var currentPageGames: []
    
    property bool isLoading: false
    
    // Always show only games whose header image is available
    property bool withImageOnly: true
    // Debounce timer (unused for now to avoid reloading model and resetting image loads)
    property var refreshTimer: Timer { interval: 300; repeat: false; onTriggered: {/* no-op */} }
    // Tick to refresh bindings when metadata cache updates
    property int metaTick: 0
    
    function filter(text) {
        searchText = (text || "").trim()
        currentPage = 1
        loadCurrentPage()
    }
    
    function loadCurrentPage() {
        console.log("Loading current page:", currentPage, "searchText:", searchText)
        if (qmlBridge && qmlBridge.steamApi) {
            var useImageOnly = withImageOnly && !!(searchText && searchText.length > 0)
            console.log("useImageOnly:", useImageOnly)
            
            // Always use the same API call for consistency
            totalGames = qmlBridge.steamApi.getTotalGamesCount(searchText, useImageOnly)
            totalPages = Math.max(1, Math.ceil(totalGames / pageSize))
            currentPage = Math.min(Math.max(1, currentPage), totalPages)
            currentPageGames = qmlBridge.steamApi.searchGames(searchText, currentPage, pageSize, useImageOnly)
            
            console.log("totalGames:", totalGames, "totalPages:", totalPages, "currentPage:", currentPage)
            console.log("currentPageGames.length:", currentPageGames.length)
        }
        renderPage()
    }
    
    function renderPage() {
        console.log("Rendering page with", currentPageGames.length, "games")
        console.log("prevButton.enabled:", currentPage > 1, "nextButton.enabled:", currentPage < totalPages)
        console.log("isLoading:", isLoading, "currentPageGames.length:", currentPageGames.length)
        
        // Repeater will render items automatically from currentPageGames
        pageLabel.text = `Page ${currentPage} / ${totalPages}  |  ${totalGames} results`
        prevButton.enabled = currentPage > 1
        nextButton.enabled = currentPage < totalPages
        
        console.log("After renderPage - prevButton.enabled:", prevButton.enabled, "nextButton.enabled:", nextButton.enabled)
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
    
    function loadGames() {
        console.log("Loading games...")
        if (qmlBridge && qmlBridge.steamApi) {
            console.log("Loading games from Steam API...")
            isLoading = true
            // reset view while waiting
            currentPage = 1
            totalGames = 0
            totalPages = 1
            currentPageGames = []
            renderPage()
            qmlBridge.steamApi.loadGames()
        }
    }

    // Public refresh without reloading data from API
    function refreshView() {
        if (!isLoading) {
            loadCurrentPage()
        }
    }
    
    // Connect to Steam API signals (only listen to steamApi to avoid duplicate loading)
    Connections {
        target: qmlBridge && qmlBridge.steamApi ? qmlBridge.steamApi : null
        function onGamesLoaded(games) {
            console.log("Steam games loaded (steamApi)")
            isLoading = false
            loadCurrentPage()
        }
        function onErrorOccurred(message) {
            console.log("Steam API error (steamApi):", message)
            isLoading = false
            loadCurrentPage()
        }
        // Avoid reloading model on every cache update, let images finish loading
        function onImageCacheUpdated() {
            // no-op; cards will become visible when each Image becomes Ready
        }
        function onMetaCacheUpdated() {
            // Trigger bindings to re-evaluate genre text
            gameListPage.metaTick = (gameListPage.metaTick + 1) % 1000000
        }
        function onLoadingStarted() {
            console.log("Loading started from GitHub")
            loadingSpinner.running = true
        }
        function onLoadingFinished() {
            console.log("Loading finished from GitHub")
            loadingSpinner.running = false
        }
    }
    
    Component.onCompleted: {
        console.log("GameListPage initialized")
        if (qmlBridge && qmlBridge.steamApi) {
            loadGames()
        }
    }
    
    // Game card component
    Component {
        id: gameCardComponent
        
        Rectangle {
            id: gameCard
            // Bind to data from Repeater model
            property string title: (typeof modelData !== 'undefined' && modelData && modelData.title) ? modelData.title : ""
            property int appid: (typeof modelData !== 'undefined' && modelData && modelData.appid) ? modelData.appid : 0
            property bool hovered: false
            property bool pressed: false
            
            signal clicked(string title, int appid)
            
            // Adaptive width based on container
            width: (cardsContainer && cardsContainer.cardWidth) ? cardsContainer.cardWidth : (parent ? parent.width : gameListPage.width)
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
            // Backend already filters only-with-image; keep UI visible regardless of Image status
            visible: true
            
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    gameCard.clicked(gameCard.title, gameCard.appid)
                    // Bubble to page-level signal so main.qml can open detail
                    gameListPage.openGame(gameCard.title, gameCard.appid)
                }
                cursorShape: Qt.PointingHandCursor
                onEntered: { gameCard.hovered = true }
                onExited: { gameCard.hovered = false }
                onPressed: { gameCard.pressed = true }
                onReleased: { gameCard.pressed = false }
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
                    
                    Text {
                        text: gameCard.title
                        color: "#ffffff"
                        font.weight: 700
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                    
                    // Genres line (fetched lazily via Steam store API)
                    Text {
                        text: qmlBridge && qmlBridge.steamApi ? (gameListPage.metaTick, qmlBridge.steamApi.getGenres(gameCard.appid)) : ""
                        color: "#b0b0b0"
                        font.pixelSize: 11
                        font.weight: 500
                        elide: Text.ElideRight
                        maximumLineCount: 1
                        Layout.fillWidth: true
                        visible: text.length > 0
                    }
                    
                    RowLayout {
                        spacing: 8
                        Text {
                            text: `AppID: ${gameCard.appid}`
                            color: "#b0b0b0"
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