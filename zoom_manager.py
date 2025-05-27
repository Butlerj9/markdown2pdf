"""
Zoom Manager for the Page Preview component.
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

class ZoomManager:
    """Manages zoom functionality for the page preview component."""
    
    def __init__(self):
        """Initialize the zoom manager."""
        self.zoom_factor = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.default_zoom = 1.0
        self.web_view = None
        
    def set_web_view(self, web_view):
        """Set the web view to manage."""
        self.web_view = web_view
        
    def update_zoom(self, value):
        """Update the zoom level based on a percentage value."""
        logger.debug(f"Updating zoom to {value}%")
        
        if not self.web_view:
            logger.warning("No web view set for zoom manager")
            return
            
        try:
            # Convert percentage to factor (100% = 1.0)
            zoom_factor = value / 100.0
            
            # Clamp to min/max values
            zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom_factor))
            
            # Update the zoom factor
            self.zoom_factor = zoom_factor
            
            # Apply to web view
            self.web_view.setZoomFactor(zoom_factor)
            
            # Execute JavaScript to update zoom
            script = f"""
            (function() {{
                try {{
                    document.body.style.zoom = {zoom_factor};
                    return true;
                }} catch (e) {{
                    console.error('Error setting zoom: ' + e.message);
                    return false;
                }}
            }})();
            """
            
            self.web_view.page().runJavaScript(script)
            
            logger.debug(f"Zoom updated to {zoom_factor}")
        except Exception as e:
            logger.error(f"Error updating zoom: {str(e)}")
            
    def reset_zoom(self):
        """Reset zoom to 100%."""
        logger.debug("Resetting zoom to 100%")
        self.update_zoom(100)
        
    def fit_to_page(self):
        """Fit the entire page in the view."""
        logger.debug("Fitting page to view")
        
        if not self.web_view:
            logger.warning("No web view set for zoom manager")
            return
            
        try:
            # Execute JavaScript to calculate the appropriate zoom level
            script = """
            (function() {
                try {
                    // Get the page element
                    var page = document.querySelector('.page');
                    if (!page) {
                        console.error('No page element found');
                        return { success: false, error: 'No page element found' };
                    }
                    
                    // Get the viewport dimensions
                    var viewportWidth = window.innerWidth;
                    var viewportHeight = window.innerHeight;
                    
                    // Get the page dimensions
                    var pageWidth = page.offsetWidth;
                    var pageHeight = page.offsetHeight;
                    
                    // Calculate the zoom factor to fit the page
                    var widthRatio = (viewportWidth - 40) / pageWidth;
                    var heightRatio = (viewportHeight - 40) / pageHeight;
                    var zoomFactor = Math.min(widthRatio, heightRatio);
                    
                    // Apply the zoom
                    document.body.style.zoom = zoomFactor;
                    
                    // Center the page
                    page.scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});
                    
                    return { 
                        success: true, 
                        zoomFactor: zoomFactor,
                        zoomPercent: Math.round(zoomFactor * 100)
                    };
                } catch (e) {
                    console.error('Error fitting page to view: ' + e.message);
                    return { success: false, error: e.message };
                }
            })();
            """
            
            self.web_view.page().runJavaScript(script, self._handle_fit_to_page_result)
        except Exception as e:
            logger.error(f"Error fitting page to view: {str(e)}")
            
    def _handle_fit_to_page_result(self, result):
        """Handle the result of the fit to page JavaScript execution."""
        logger.debug(f"Fit to page result: {result}")
        
        if isinstance(result, dict) and result.get('success', False):
            zoom_percent = result.get('zoomPercent', 100)
            
            # Update the zoom factor
            self.zoom_factor = zoom_percent / 100.0
            
            # Update the UI if needed
            if hasattr(self, 'update_zoom_ui'):
                self.update_zoom_ui(zoom_percent)
                
            logger.debug(f"Fit to page successful, zoom set to {zoom_percent}%")
        else:
            error = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
            logger.warning(f"Fit to page failed: {error}")
            
    def fit_to_width(self):
        """Fit the page width to the view."""
        logger.debug("Fitting page width to view")
        
        if not self.web_view:
            logger.warning("No web view set for zoom manager")
            return
            
        try:
            # Execute JavaScript to calculate the appropriate zoom level
            script = """
            (function() {
                try {
                    // Get the page element
                    var page = document.querySelector('.page');
                    if (!page) {
                        console.error('No page element found');
                        return { success: false, error: 'No page element found' };
                    }
                    
                    // Get the viewport width
                    var viewportWidth = window.innerWidth;
                    
                    // Get the page width
                    var pageWidth = page.offsetWidth;
                    
                    // Calculate the zoom factor to fit the width
                    var zoomFactor = (viewportWidth - 40) / pageWidth;
                    
                    // Apply the zoom
                    document.body.style.zoom = zoomFactor;
                    
                    // Center the page horizontally
                    page.scrollIntoView({behavior: 'auto', block: 'start', inline: 'center'});
                    
                    return { 
                        success: true, 
                        zoomFactor: zoomFactor,
                        zoomPercent: Math.round(zoomFactor * 100)
                    };
                } catch (e) {
                    console.error('Error fitting page width to view: ' + e.message);
                    return { success: false, error: e.message };
                }
            })();
            """
            
            self.web_view.page().runJavaScript(script, self._handle_fit_to_width_result)
        except Exception as e:
            logger.error(f"Error fitting page width to view: {str(e)}")
            
    def _handle_fit_to_width_result(self, result):
        """Handle the result of the fit to width JavaScript execution."""
        logger.debug(f"Fit to width result: {result}")
        
        if isinstance(result, dict) and result.get('success', False):
            zoom_percent = result.get('zoomPercent', 100)
            
            # Update the zoom factor
            self.zoom_factor = zoom_percent / 100.0
            
            # Update the UI if needed
            if hasattr(self, 'update_zoom_ui'):
                self.update_zoom_ui(zoom_percent)
                
            logger.debug(f"Fit to width successful, zoom set to {zoom_percent}%")
        else:
            error = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
            logger.warning(f"Fit to width failed: {error}")
            
    def center_page(self):
        """Center the page in the view."""
        logger.debug("Centering page in view")
        
        if not self.web_view:
            logger.warning("No web view set for zoom manager")
            return
            
        try:
            # Execute JavaScript to center the page
            script = """
            (function() {
                try {
                    // Get the page element
                    var page = document.querySelector('.page');
                    if (!page) {
                        console.error('No page element found');
                        return { success: false, error: 'No page element found' };
                    }
                    
                    // Center the page
                    page.scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});
                    
                    return { success: true };
                } catch (e) {
                    console.error('Error centering page: ' + e.message);
                    return { success: false, error: e.message };
                }
            })();
            """
            
            self.web_view.page().runJavaScript(script)
        except Exception as e:
            logger.error(f"Error centering page: {str(e)}")
            
    def apply_document_settings(self, settings):
        """Apply document settings to the preview."""
        logger.debug("Applying document settings")
        
        if not self.web_view:
            logger.warning("No web view set for zoom manager")
            return
            
        try:
            # Extract relevant settings
            font_family = settings.get('fonts', {}).get('body', {}).get('family', 'Arial')
            font_size = settings.get('fonts', {}).get('body', {}).get('size', 11)
            text_color = settings.get('colors', {}).get('text', '#000000')
            bg_color = settings.get('colors', {}).get('background', '#FFFFFF')
            
            # Create CSS for the document
            css = f"""
            body {{
                font-family: '{font_family}', sans-serif;
                font-size: {font_size}pt;
                color: {text_color};
                background-color: {bg_color};
            }}
            """
            
            # Apply the CSS
            script = f"""
            (function() {{
                try {{
                    // Create or update the style element
                    var style = document.getElementById('document-settings-style');
                    if (!style) {{
                        style = document.createElement('style');
                        style.id = 'document-settings-style';
                        document.head.appendChild(style);
                    }}
                    
                    // Set the CSS
                    style.textContent = `{css}`;
                    
                    return true;
                }} catch (e) {{
                    console.error('Error applying document settings: ' + e.message);
                    return false;
                }}
            }})();
            """
            
            self.web_view.page().runJavaScript(script)
        except Exception as e:
            logger.error(f"Error applying document settings: {str(e)}")
