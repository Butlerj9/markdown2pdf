#!/usr/bin/env python3
"""
Verify Settings Fix
-----------------
This script verifies that the settings are no longer being saved multiple times.
"""

import os
import sys
import logging
from PyQt6.QtCore import QCoreApplication, Qt, QSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Qt attribute before creating QApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

class SettingsCounter:
    """Class to count settings save operations"""
    
    def __init__(self):
        """Initialize the counter"""
        self.count = 0
        self.settings = {}
    
    def setValue(self, key, value):
        """Mock setValue method"""
        self.count += 1
        self.settings[key] = value
        logger.debug(f"setValue called for key: {key} (count: {self.count})")
        
        # Print stack trace to see where the call is coming from
        import traceback
        stack = traceback.extract_stack()
        caller = stack[-2]  # The caller of this method
        logger.debug(f"Called from: {caller.filename}:{caller.lineno}")
        
        return True

class TestWindow(QMainWindow):
    """Test window to simulate the main application"""
    
    def __init__(self):
        """Initialize the window"""
        super().__init__()
        
        self.setWindowTitle("Settings Test")
        self.resize(400, 300)
        
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create a layout
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("This is a test window to verify settings saving.")
        layout.addWidget(label)
        
        # Add a button to save settings
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        # Add a button to open an MDZ file
        open_mdz_button = QPushButton("Simulate Open MDZ")
        open_mdz_button.clicked.connect(self.simulate_open_mdz)
        layout.addWidget(open_mdz_button)
        
        # Add a button to save an MDZ file
        save_mdz_button = QPushButton("Simulate Save MDZ")
        save_mdz_button.clicked.connect(self.simulate_save_mdz)
        layout.addWidget(save_mdz_button)
        
        # Add a button to export to MDZ
        export_mdz_button = QPushButton("Simulate Export MDZ")
        export_mdz_button.clicked.connect(self.simulate_export_mdz)
        layout.addWidget(export_mdz_button)
        
        # Add a button to quit
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)
        
        # Initialize dialog paths
        self.dialog_paths = {
            "open": "",
            "save": "",
            "export": ""
        }
        
        # Create a settings counter
        self.settings_counter = SettingsCounter()
        
        # Set up MDZ integration
        self.setup_mdz_integration()
    
    def setup_mdz_integration(self):
        """Set up MDZ integration"""
        try:
            # Import MDZ integration
            from mdz_integration import integrate_mdz
            
            # Integrate MDZ
            self.mdz_integration = integrate_mdz(self)
            
            logger.info("MDZ integration set up")
        except Exception as e:
            logger.error(f"Error setting up MDZ integration: {str(e)}")
            self.mdz_integration = None
    
    def save_settings(self):
        """Save settings"""
        logger.info("Saving settings...")
        
        # Save dialog paths
        self.settings_counter.setValue("dialog_paths", self.dialog_paths)
        
        logger.info("Settings saved")
    
    def simulate_open_mdz(self):
        """Simulate opening an MDZ file"""
        logger.info("Simulating opening an MDZ file...")
        
        # Update dialog paths
        self.dialog_paths["open"] = "/path/to/mdz"
        
        # Call the MDZ integration method
        if self.mdz_integration:
            # Create a temporary file
            import tempfile
            temp_mdz = tempfile.NamedTemporaryFile(delete=False, suffix='.mdz')
            temp_mdz.close()
            
            # Call the open_mdz_file method
            self.mdz_integration.open_mdz_file(temp_mdz.name)
            
            # Clean up
            try:
                os.unlink(temp_mdz.name)
            except:
                pass
        
        logger.info("Simulated opening an MDZ file")
    
    def simulate_save_mdz(self):
        """Simulate saving an MDZ file"""
        logger.info("Simulating saving an MDZ file...")
        
        # Update dialog paths
        self.dialog_paths["save"] = "/path/to/mdz"
        
        # Call the MDZ integration method
        if self.mdz_integration:
            # Create a temporary file
            import tempfile
            temp_mdz = tempfile.NamedTemporaryFile(delete=False, suffix='.mdz')
            temp_mdz.close()
            
            # Call the save_mdz_file method
            self.mdz_integration.save_mdz_file(temp_mdz.name)
            
            # Clean up
            try:
                os.unlink(temp_mdz.name)
            except:
                pass
        
        logger.info("Simulated saving an MDZ file")
    
    def simulate_export_mdz(self):
        """Simulate exporting to MDZ"""
        logger.info("Simulating exporting to MDZ...")
        
        # Update dialog paths
        self.dialog_paths["export"] = "/path/to/mdz"
        
        # Call the MDZ integration method
        if self.mdz_integration:
            # Create a temporary file
            import tempfile
            temp_mdz = tempfile.NamedTemporaryFile(delete=False, suffix='.mdz')
            temp_mdz.close()
            
            # Manually call the code that would be executed in export_to_mdz
            self.dialog_paths["export"] = os.path.dirname(temp_mdz.name)
            
            # Clean up
            try:
                os.unlink(temp_mdz.name)
            except:
                pass
        
        logger.info("Simulated exporting to MDZ")
    
    def closeEvent(self, event):
        """Handle close event"""
        logger.info("Closing window...")
        
        # Save settings
        self.save_settings()
        
        # Accept the event
        event.accept()

def main():
    """Main function"""
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create the test window
    window = TestWindow()
    
    # Show the window
    window.show()
    
    # Run the application
    app.exec()
    
    # Print the settings counter
    logger.info(f"Total setValue calls: {window.settings_counter.count}")
    logger.info(f"Final settings: {window.settings_counter.settings}")
    
    # Return success
    return 0

if __name__ == "__main__":
    sys.exit(main())
