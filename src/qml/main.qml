import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import MantaTools 1.0
import "components"
import "pages"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 800
    minimumWidth: 1200
    minimumHeight: 700
    title: "MantaTools v1.0.0"
    
    // Minimalist Dark Theme - Clean & Modern
    // Primary Backgrounds
    readonly property color darkBg: "#0d1117"                    // GitHub dark main
    readonly property color darkBgSecondary: "#161b22"          // GitHub secondary
    readonly property color darkBgTertiary: "#21262d"           // GitHub tertiary
    readonly property color panelBg: "#0d1117"                  // Panel background
    readonly property color cardBg: "#161b22"                   // Card background
    readonly property color hoverBg: "#21262d"                  // Hover background
    
    // Text Colors
    readonly property color textPrimary: "#f0f6fc"              // Primary text
    readonly property color textSecondary: "#e6edf3"            // Secondary text
    readonly property color textTertiary: "#8b949e"             // Tertiary text
    readonly property color textMuted: "#6e7681"                // Muted text
    
    // Border & Divider Colors
    readonly property color border: "#30363d"                   // Default border
    readonly property color borderLight: "#484f58"              // Light border
    readonly property color borderHover: "#484f58"              // Hover border
    readonly property color divider: "#30363d"                  // Divider lines
    
    // Accent Colors
    readonly property color accent: "#484f58"                   // Gray accent
    readonly property color accentHover: "#6e7681"              // Gray hover
    readonly property color accentLight: "#8b949e"              // Light gray
    
    // Status Colors
    readonly property color success: "#3fb950"                  // GitHub success green
    readonly property color warning: "#d29922"                  // GitHub warning amber
    readonly property color error: "#f85149"                    // GitHub error red
    readonly property color info: "#484f58"                     // Gray info
    
    // Overlay Colors
    readonly property color overlay01: "#0d1117"                // Overlay 1
    readonly property color overlay02: "#161b22"                // Overlay 2
    readonly property color overlay03: "#21262d"                // Overlay 3
    readonly property color glassBg: "#0dffffff"                // Glass background
    readonly property color glassBorder: "#1affffff"            // Glass border
    
    // Shadow Colors
    readonly property color shadowLight: "#15000000"            // Light shadow
    readonly property color shadowMedium: "#20000000"           // Medium shadow
    readonly property color shadowDark: "#40000000"             // Dark shadow
    
    // Button Colors - Harmonious & Serasi
    readonly property color buttonPrimary: "#21262d"            // Primary button background
    readonly property color buttonPrimaryHover: "#30363d"       // Primary button hover
    readonly property color buttonPrimaryPressed: "#0d1117"     // Primary button pressed
    readonly property color buttonSecondary: "#161b22"          // Secondary button background
    readonly property color buttonSecondaryHover: "#21262d"     // Secondary button hover
    readonly property color buttonSecondaryPressed: "#0d1117"   // Secondary button pressed
    readonly property color buttonAccent: "#484f58"             // Accent button background
    readonly property color buttonAccentHover: "#6e7681"        // Accent button hover
    readonly property color buttonAccentPressed: "#30363d"      // Accent button pressed
    readonly property color buttonSuccess: "#238636"            // Success button background
    readonly property color buttonSuccessHover: "#2ea043"       // Success button hover
    readonly property color buttonSuccessPressed: "#1a7f37"     // Success button pressed
    readonly property color buttonDanger: "#da3633"             // Danger button background
    readonly property color buttonDangerHover: "#f85149"        // Danger button hover
    readonly property color buttonDangerPressed: "#b91c1c"      // Danger button pressed
    readonly property color buttonText: "#f0f6fc"               // Button text color
    readonly property color buttonTextSecondary: "#8b949e"      // Secondary button text
    readonly property color buttonBorder: "#30363d"             // Button border
    readonly property color buttonBorderHover: "#484f58"        // Button border hover
    
    // Hover Colors - Harmonious & Serasi
    readonly property color hoverPrimary: "#21262d"             // Primary hover background
    readonly property color hoverSecondary: "#30363d"           // Secondary hover background
    readonly property color hoverAccent: "#484f58"              // Accent hover background
    readonly property color hoverSuccess: "#238636"             // Success hover background
    readonly property color hoverDanger: "#da3633"              // Danger hover background
    readonly property color hoverCard: "#21262d"                // Card hover background
    readonly property color hoverBorder: "#484f58"              // Hover border color
    readonly property color hoverText: "#f0f6fc"                // Hover text color
    readonly property color hoverShadow: "#20000000"            // Hover shadow
    readonly property color hoverGlow: "#1a484f58"              // Hover glow effect
    
    // Modern spacing scale - Clean and consistent
    readonly property int spacingXs: 6
    readonly property int spacingSm: 12
    readonly property int spacingMd: 20
    readonly property int spacingLg: 12
    readonly property int spacingXl: 12
    readonly property int spacing2xl: 48
    readonly property int spacing3xl: 64
    
    // Modern font sizes
    readonly property int fontXs: 11
    readonly property int fontSm: 13
    readonly property int fontMd: 15
    readonly property int fontLg: 17
    readonly property int fontXl: 19
    readonly property int font2xl: 22
    readonly property int font3xl: 26
    readonly property int font4xl: 32
    
    // Font weights
    readonly property int weightNormal: 400
    readonly property int weightMedium: 500
    readonly property int weightSemiBold: 600
    readonly property int weightBold: 700
    readonly property int weightExtraBold: 800
    
    // Modern border radius
    readonly property int radiusSm: 8
    readonly property int radiusMd: 12
    readonly property int radiusLg: 16
    readonly property int radiusXl: 20
    readonly property int radius2xl: 24
    readonly property int radius3xl: 32
    
    // Responsive sidebar width
    readonly property int sidebarMinWidth: 240
    readonly property int sidebarMaxWidth: 450
    readonly property real sidebarWidthRatio: 0.22
    readonly property int computedSidebarWidth: Math.round(Math.max(sidebarMinWidth, Math.min(sidebarMaxWidth, width * sidebarWidthRatio)))
    
    // Navigation state
    property int currentPage: 0  // 0: Games, 1: Game Detail, 2: Settings
    property int previousPage: 0  // Store previous page before opening detail
    property string currentGameTitle: ""
    property int currentGameAppid: 0
    
    // QML Bridge property
    property var qmlBridge: null
    
    // Authentication state
    property bool isAuthenticated: false
    property bool showAuthGate: true
    
    // Functions from QWidget MainWindow
    function openGameDetail(title, appid) {
        // Store previous page before opening detail
        previousPage = currentPage
        
        currentGameTitle = title
        currentGameAppid = appid
        gameDetailPage.showGame(title, appid)
        currentPage = 1
        stackView.push(gameDetailPage)
        header.setMode("detail", title)
    }
    
    function backToGameList() {
        // Get current game info before popping
        var currentAppid = gameDetailPage.currentAppid
        
        // Simply pop the stack
        stackView.pop()
        
        // Restore the previous page state
        if (previousPage === 0) {
            // Was on game list page
            currentPage = 0
            header.setMode("list", "Games")
        } else if (previousPage === 2) {
            // Was on library page
            currentPage = 2
            header.setMode("library", "Library")
            // Scan patch for the game when going back to library page
            if (libraryPage && currentAppid > 0) {
                console.log("Back to library, scanning patch for AppID:", currentAppid)
                Qt.callLater(function() {
                    libraryPage.refreshPatchStatus(currentAppid)
                })
            }
        }
    }
    
    function onNavChanged(name) {
        if (name === "games") {
            currentPage = 0
            header.setMode("list", "Games")
            header.showSearchBar(true)
            // Clear stack dan push Games page
            stackView.clear()
            stackView.push(gameListPage)
        } else if (name === "settings") {
            currentPage = 2
            header.setMode("library", "Library")
            header.showSearchBar(true)
            // Clear stack dan push Library page
            stackView.clear()
            stackView.push(libraryPage)
        } else {
            // Fallback: preserve current header mode
            if (currentPage === 0) {
                header.setMode("list")
            } else {
                header.setMode("detail", currentGameTitle || "Game Detail")
            }
        }
    }
    
    function showSnack(message, type, duration) {
        console.log("MainWindow: showSnack called with:", message, type, duration)
        snackManager.showSnack(message, type, duration)
    }
    
    function showSnackAnchor(anchor, message, type, duration, side) {
        console.log("MainWindow: showSnackAnchor called with:", message, type, duration)
        snackManager.showSnackAnchor(anchor, message, type, duration, side)
    }
    
    // Test function for toast notifications
    function testToast() {
        console.log("MainWindow: Testing toast notification")
        showSnack("Test notification", "success", 3000)
    }
    
    // Authentication functions
    function onLoginRequested(token) {
        console.log("Login requested with token:", token)
        
        // Try to get qmlBridge from context property using different methods
        var bridge = null
        
        // Method 1: Direct access
        try {
            bridge = qmlBridge
            console.log("Method 1 - Direct qmlBridge access:", bridge)
        } catch (e) {
            console.log("Method 1 - Error accessing qmlBridge directly:", e)
        }
        
        // Method 2: Try to access from parent
        if (!bridge) {
            try {
                bridge = mainWindow.parent ? mainWindow.parent.qmlBridge : null
                console.log("Method 2 - Parent qmlBridge access:", bridge)
            } catch (e) {
                console.log("Method 2 - Error accessing parent qmlBridge:", e)
            }
        }
        
        // Method 3: Try to access from application
        if (!bridge) {
            try {
                bridge = Qt.application ? Qt.application.qmlBridge : null
                console.log("Method 3 - Application qmlBridge access:", bridge)
            } catch (e) {
                console.log("Method 3 - Error accessing application qmlBridge:", e)
            }
        }
        
        // Method 4: Try to access from root context
        if (!bridge) {
            try {
                bridge = Qt.application ? Qt.application.arguments : null
                console.log("Method 4 - Application arguments:", bridge)
                // Try to get from root context
                var rootObjects = Qt.application ? Qt.application.rootObjects : null
                console.log("Method 4 - Root objects:", rootObjects)
            } catch (e) {
                console.log("Method 4 - Error accessing root context:", e)
            }
        }
        
        console.log("Final bridge available:", typeof bridge !== 'undefined' && bridge)
        console.log("Final bridge.authenticateUser available:", bridge && typeof bridge.authenticateUser === 'function')
        
        if (bridge && bridge.authenticateUser) {
            console.log("Calling bridge.authenticateUser...")
            // Show loading state
            authGateComponent.setLoading(true)
            authGateComponent.clearStatus()
            
            // Call Python authentication (asynchronous)
            bridge.authenticateUser(token)
        } else {
            console.log("bridge or authenticateUser not available!")
        }
    }
    
    function onLoginSuccess() {
        console.log("Login successful!")
        isAuthenticated = true
        showAuthGate = false
        authGateComponent.hide()
        
        // Load games after successful authentication
        if (qmlBridge && qmlBridge.loadGames) {
            console.log("Loading games after successful authentication...")
            qmlBridge.loadGames()
        }
    }
    
    function onLoginFailed(message) {
        console.log("Login failed:", message)
        authGateComponent.setStatus(message, "error")
    }
    
    
    function startAuthentication() {
        showAuthGate = true
        isAuthenticated = false
        authGateComponent.show()
    }
    
    // Initialize QML Bridge
    Component.onCompleted: {
        console.log("Main window initialized")
        
        // Try to get qmlBridge from context property
        try {
            var contextBridge = Qt.application.arguments.length > 0 ? 
                mainWindow.parent ? mainWindow.parent.qmlBridge : null : null
            console.log("Context bridge:", contextBridge)
        } catch (e) {
            console.log("Error getting context bridge:", e)
        }
        
        // Set qmlBridge property from context
        qmlBridge = typeof qmlBridge !== 'undefined' ? qmlBridge : null
        console.log("qmlBridge available:", typeof qmlBridge !== 'undefined' && qmlBridge)
        console.log("qmlBridge type:", typeof qmlBridge)
        console.log("qmlBridge value:", qmlBridge)
        
        // Set initial page
        stackView.push(gameListPage)
        
        // Provide qmlBridge to pages
        if (typeof qmlBridge !== 'undefined' && qmlBridge) {
            console.log("Setting qmlBridge to gameListPage")
            gameListPage.qmlBridge = qmlBridge
            if (gameDetailPage) {
                console.log("Setting qmlBridge to gameDetailPage")
                gameDetailPage.qmlBridge = qmlBridge
            }
            if (libraryPage) {
                console.log("Setting qmlBridge to libraryPage")
                libraryPage.qmlBridge = qmlBridge
            }
            // Don't auto-load games - wait for authentication
            console.log("Waiting for user authentication before loading games...")
        } else {
            console.log("QML Bridge not available yet, will be set later")
        }
    }
    
    // Watch for qmlBridge property changes
    onQmlBridgeChanged: {
        console.log("qmlBridge property changed")
        if (qmlBridge) {
            console.log("QML Bridge available, setting to all pages...")
            if (gameListPage) {
                console.log("Setting qmlBridge to gameListPage from property change")
                gameListPage.qmlBridge = qmlBridge
                // Don't auto-load games - wait for authentication
                console.log("QML Bridge set, waiting for authentication...")
            }
            if (gameDetailPage) {
                console.log("Setting qmlBridge to gameDetailPage from property change")
                gameDetailPage.qmlBridge = qmlBridge
            }
            if (libraryPage) {
                console.log("Setting qmlBridge to libraryPage from property change")
                libraryPage.qmlBridge = qmlBridge
            }
        } else {
            console.log("QML Bridge not available yet, will be set later")
        }
    }
    
    // Connect to authentication signals
    Connections {
        target: qmlBridge
        function onAuthenticationSuccess() {
            console.log("Authentication success signal received")
            onLoginSuccess()
            authGateComponent.setLoading(false)
        }
        function onAuthenticationFailed(message) {
            console.log("Authentication failed signal received:", message)
            onLoginFailed(message)
            authGateComponent.setLoading(false)
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: darkBg
        
        // Main content - only visible when authenticated
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: spacingLg
            anchors.topMargin: spacingLg
            anchors.bottomMargin: spacingLg
            anchors.rightMargin: mainWindow.currentPage === 1 ? 0 : spacingLg
            spacing: mainWindow.currentPage === 1 ? 0 : spacingXl
            visible: mainWindow.isAuthenticated
            
            // Sidebar
            Sidebar {
                id: sidebar
                Layout.preferredWidth: mainWindow.computedSidebarWidth
                Layout.fillHeight: true
                onNavChanged: function(name) {
                    mainWindow.onNavChanged(name)
                }
                onShowComingSoon: function(message, icon) {
                    comingSoonNotification.show(message, icon)
                }
            }
            
            // Content area
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0
                
                // Header
                Header {
                    id: header
                    Layout.fillWidth: true
                    Layout.preferredHeight: header.implicitHeight
                    
                    onSearchChanged: function(text) {
                        if (stackView.currentItem && stackView.currentItem.filter) {
                            // Saat melakukan pencarian, tampilkan hasil relevan tanpa membatasi hanya yang punya header image
                            if ('withImageOnly' in stackView.currentItem) {
                                stackView.currentItem.withImageOnly = false
                            }
                            stackView.currentItem.filter(text)
                        }
                    }
                    
                    onBackClicked: {
                        mainWindow.backToGameList()
                    }

                    onRefreshRequested: {
                        if (stackView.currentItem && stackView.currentItem.refreshView) {
                            stackView.currentItem.refreshView()
                        }
                    }
                    
                    onLibrarySearchChanged: function(text) {
                        if (stackView.currentItem && stackView.currentItem.filterItems) {
                            stackView.currentItem.filterItems(text)
                        }
                    }
                    
                    onLibraryRefreshRequested: {
                        if (stackView.currentItem) {
                            if (stackView.currentItem.refreshLibrary) {
                                stackView.currentItem.refreshLibrary()
                            } else if (stackView.currentItem.syncSteamLibrary) {
                                stackView.currentItem.syncSteamLibrary()
                            }
                        }
                    }

                    
                    // Toggle Header search from navigation - delegated to Header component
                }
                
                // Stack view for pages with dark gray styling
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: darkBg
                    clip: true
                    z: 0
                    
                    StackView {
                        id: stackView
                        anchors.fill: parent
                        
                        // Game list page
                        GameListPage {
                            id: gameListPage
                            objectName: "gameListPage"
                            onOpenGame: function(title, appid) {
                                mainWindow.openGameDetail(title, appid)
                            }
                        }
                        
                        // Game detail page
                        GameDetailPage {
                            id: gameDetailPage
                            onBackRequested: mainWindow.backToGameList()
                        }
                        
                        // Library page
                        LibraryPage {
                            id: libraryPage
                            objectName: "libraryPage"
                            qmlBridge: mainWindow.qmlBridge
                            header: header
                            onOpenGame: function(title, appid) {
                                mainWindow.openGameDetail(title, appid)
                            }
                            onSyncStateChanged: function(hasBeenSynced) {
                                header.setLibrarySynced(hasBeenSynced)
                            }
                        }
                        
                        // Initial item will be set by navigation
                    }
                }
            }
        }
    }
    
    // Toast Manager
    ToastManager {
        id: toastManager
    }
    
    // Snack manager - simplified to avoid infinite loop
    Rectangle {
        id: snackManager
        anchors.fill: parent
        color: "transparent"
        visible: false
        z: 1000
        
        function showSnack(message, type, duration) {
            console.log("SnackManager: showSnack called with:", message, type, duration)
            if (toastManager) {
                console.log("SnackManager: Calling toastManager.showToast")
                toastManager.showToast(message, type, duration)
            } else {
                console.log("SnackManager: toastManager is null!")
            }
        }
        
        function showSnackAnchor(anchor, message, type, duration, side) {
            console.log("SnackManager: showSnackAnchor called with:", message, type, duration)
            if (toastManager) {
                console.log("SnackManager: Calling toastManager.showToast")
                toastManager.showToast(message, type, duration)
            } else {
                console.log("SnackManager: toastManager is null!")
            }
        }
    }
    
    // Coming Soon Notification
    ComingSoonNotification {
        id: comingSoonNotification
        anchors.right: parent.right
        anchors.top: parent.top
        z: 1001
    }
    
    // AuthGate Component
    AuthGate {
        id: authGateComponent
        visible: !mainWindow.isAuthenticated
        isAuthenticated: mainWindow.isAuthenticated
        
        onLoginRequested: function(token) {
            mainWindow.onLoginRequested(token)
        }
        
        onLoginSuccess: {
            mainWindow.onLoginSuccess()
        }
        
        onLoginFailed: function(message) {
            mainWindow.onLoginFailed(message)
        }
    }
    
    // Set modern Material style
    Material.theme: Material.Dark
    Material.accent: Material.Blue
    Material.primary: Material.BlueGrey
}