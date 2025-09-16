import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: header
    color: mainWindow.darkBg
    radius: 12
    // Collapse entirely in detail mode to avoid extra top spacing
    implicitHeight: (currentMode === "list" || currentMode === "library") ? rootCol.implicitHeight + 32 : 0
    visible: (currentMode === "list" || currentMode === "library")
    
    property string currentMode: "list"
    property string currentTitle: "Games"
    property string searchText: ""
    property var qmlBridge: null
    property bool isLibrarySyncing: false
    property bool libraryHasBeenSynced: false
    property bool isRefreshing: false
    
    signal searchChanged(string text)
    signal librarySearchChanged(string text)
    signal refreshRequested()
    signal libraryRefreshRequested()
    signal backClicked()
    
    function setLibrarySyncing(syncing) {
        isLibrarySyncing = syncing
    }
    
    function setLibrarySynced(synced) {
        libraryHasBeenSynced = synced
    }
    
    function setRefreshing(refreshing) {
        isRefreshing = refreshing
    }
    
    function setMode(mode, title) {
        currentMode = mode
        currentTitle = title || "Games"
    }
    
    // Function to show/hide search bar (from QWidget MainWindow)
    function showSearchBar(visible) {
        searchBar.visible = visible
        btnSearch.visible = visible
        instructionLabel.visible = visible
    }
    
    ColumnLayout {
        id: rootCol
        anchors.fill: parent
        anchors.margins: 24
        spacing: 6
        
        // Title and subtitle
        RowLayout {
            Layout.fillWidth: true
            
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                Text {
                    text: header.currentTitle
                    color: "#ffffff"
                    font.weight: 700
                    font.pixelSize: 24
                    visible: (currentMode === "list" || currentMode === "library")
                }
                
                
                // Instruction text for search
                Text {
                    id: instructionLabel
                    text: currentMode === "library" ? 
                          "Search through your Steam library games." : 
                          "If the game you're searching for doesn't appear, try using the AppID or entering a more specific keyword."
                    color: "#b0b0b0"
                    font.pixelSize: 12
                    font.weight: 400
                    visible: (currentMode === "list" || currentMode === "library")
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
            
        }
        
        // Search bar (only visible in list and library mode)
        RowLayout {
            id: searchBar
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            visible: (currentMode === "list" || currentMode === "library")
            spacing: 12
            
            CustomTextField {
                id: searchField
                placeholderText: currentMode === "library" ? "Search library..." : "Search games..."
                Layout.fillWidth: true
                Layout.preferredWidth: 400
                height: 44
                text: header.searchText
                
                onTextChanged: {
                    header.searchText = text
                }

                Keys.onReturnPressed: {
                    if (currentMode === "library") {
                        header.librarySearchChanged(searchField.text)
                    } else {
                        header.searchChanged(searchField.text)
                    }
                }
                Keys.onEnterPressed: {
                    if (currentMode === "library") {
                        header.librarySearchChanged(searchField.text)
                    } else {
                        header.searchChanged(searchField.text)
                    }
                }
            }
            
            // Removed checkbox; image-only filtering is now automatic

            
            CustomButton {
                id: btnSearch
                text: "Search"
                height: 44
                width: 100
                buttonColor: mainWindow.buttonSecondary
                hoverColor: mainWindow.buttonSecondaryHover
                pressedColor: mainWindow.buttonSecondaryPressed
                textColor: mainWindow.buttonText
                onClicked: {
                    if (currentMode === "library") {
                        librarySearchChanged(searchField.text)
                    } else {
                        searchChanged(searchField.text)
                    }
                }
            }

            // Update button
            CustomButton {
                id: btnUpdate
                text: "Check Update"
                height: 44
                width: 120
                buttonColor: mainWindow.buttonSecondary
                hoverColor: mainWindow.buttonSecondaryHover
                pressedColor: mainWindow.buttonSecondaryPressed
                textColor: mainWindow.buttonText
                onClicked: {
                    if (updateManager) {
                        updateManager.check_for_updates(true)
                    }
                }
            }

            // Refresh button
            CustomButton {
                id: btnRefresh
                text: {
                    if (currentMode === "library") {
                        if (isLibrarySyncing) return "Syncing..."
                        if (isRefreshing) return "Scanning..."
                        return libraryHasBeenSynced ? "Refresh" : "Sync Library"
                    }
                    return "Refresh"
                }
                height: 44
                width: currentMode === "library" ? 130 : 100
                buttonColor: currentMode === "library" && (isLibrarySyncing || isRefreshing) ? mainWindow.buttonPrimary : mainWindow.buttonAccent
                hoverColor: currentMode === "library" && (isLibrarySyncing || isRefreshing) ? mainWindow.buttonPrimaryHover : mainWindow.buttonAccentHover
                pressedColor: currentMode === "library" && (isLibrarySyncing || isRefreshing) ? mainWindow.buttonPrimaryPressed : mainWindow.buttonAccentPressed
                textColor: currentMode === "library" && (isLibrarySyncing || isRefreshing) ? mainWindow.buttonText : mainWindow.buttonText
                enabled: !(currentMode === "library" && (isLibrarySyncing || isRefreshing))
                onClicked: {
                    if (currentMode === "library") {
                        libraryRefreshRequested()
                    } else {
                        refreshRequested()
                    }
                }
            }
        }
    }
}