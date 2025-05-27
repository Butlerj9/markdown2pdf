import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl

class WebBridge(QObject):
    """Bridge between JavaScript and Python"""
    messageReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    @pyqtSlot(str)
    def receiveMessage(self, message):
        """Receive a message from JavaScript"""
        print(f"Message from JavaScript: {message}")
        self.messageReceived.emit(f"Python received: {message}")

    @pyqtSlot(result=str)
    def sendMessage(self):
        """Send a message to JavaScript"""
        return "Hello from Python!"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QWebChannel Test")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Set up web channel
        self.channel = QWebChannel()
        self.bridge = WebBridge()
        self.channel.registerObject("bridge", self.bridge)

        # Connect the web page to the channel
        self.web_view.page().setWebChannel(self.channel)

        # Create QWebChannel.js content
        qwebchannel_js = """
// QWebChannel implementation
function QWebChannelMessageHandler(object) {
    this.object = object;
}

QWebChannelMessageHandler.prototype.handleMessage = function(message) {
    if (message.type === 'signal') {
        var signalName = message.object + '.' + message.signal;
        var signalArgs = message.args;
        this.object.signalEmitted(signalName, signalArgs);
    }
};

function QWebChannel(transport, initCallback) {
    if (typeof transport !== 'object' || typeof transport.send !== 'function') {
        console.error('The QWebChannel expects a transport object with a send function and onmessage signal.');
        return;
    }

    var channel = this;
    this.transport = transport;
    this.objects = {};

    // Create a basic bridge object
    this.objects.bridge = {
        pageCountChanged: function(current, total) {
            console.log('Page count changed:', current, 'of', total);
        }
    };

    if (initCallback) {
        initCallback(this);
    }
}
        """

        # Load HTML with JavaScript that uses the web channel
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>QWebChannel Test</title>
            <script>
                {qwebchannel_js}

                // Function to be called when the document is ready
                function onLoad() {{
                    console.log("Document loaded, setting up QWebChannel");

                    // Check if QWebChannel is available
                    if (typeof QWebChannel === 'undefined') {{
                        console.error("QWebChannel is not defined!");
                        document.getElementById('status').textContent = "Error: QWebChannel is not defined";
                        return;
                    }}

                    // Initialize the web channel
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        // Get the bridge object
                        window.bridge = channel.objects.bridge;
                        console.log("QWebChannel initialized successfully");
                        document.getElementById('status').textContent = "QWebChannel initialized successfully";

                        // Get a message from Python
                        var message = bridge.sendMessage();
                        document.getElementById('message').textContent = message;

                        // Set up a function to send messages to Python
                        window.sendToPython = function() {{
                            var message = document.getElementById('input').value;
                            bridge.receiveMessage(message);
                        }};

                        // Set up a handler for messages from Python
                        bridge.messageReceived.connect(function(message) {{
                            document.getElementById('response').textContent = message;
                        }});
                    }});
                }}
            </script>
        </head>
        <body onload="onLoad()">
            <h1>QWebChannel Test</h1>
            <p>Status: <span id="status">Initializing...</span></p>
            <p>Message from Python: <span id="message">None yet</span></p>
            <p>
                <input type="text" id="input" placeholder="Type a message">
                <button onclick="sendToPython()">Send to Python</button>
            </p>
            <p>Response: <span id="response">None yet</span></p>
        </body>
        </html>
        """

        # Load the HTML
        self.web_view.setHtml(html)

        # Set up a custom page to handle console messages
        class CustomWebEnginePage(QWebEnginePage):
            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                level_str = {
                    QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
                    QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
                    QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
                }.get(level, "UNKNOWN")

                print(f"JS {level_str}: {message} (line {lineNumber}, source: {sourceID})")

        # Replace the default page with our custom page
        custom_page = CustomWebEnginePage(self.web_view)
        custom_page.setWebChannel(self.channel)
        self.web_view.setPage(custom_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
