#!/usr/bin/env python3
"""
Zoom Utilities
-------------
Clean, standalone zoom utilities for the page preview component.
File: src/zoom_utils.py
"""

import logging
from PyQt6.QtCore import QTimer

# Get logger
logger = logging.getLogger(__name__)

class ZoomManager:
    """
    Manages zoom functionality for page preview

    This class provides clean, standalone zoom functions without dependencies
    on other utilities or helper scripts.
    """

    def __init__(self, web_page, default_zoom=100):
        """
        Initialize the zoom manager

        Args:
            web_page: The QWebEnginePage to apply zoom to
            default_zoom: Default zoom percentage (100 = 100%)
        """
        self.web_page = web_page
        self.zoom_factor = default_zoom / 100.0
        self.current_zoom = default_zoom

        # Flag to track if zoom is being updated to prevent recursion
        self._updating_zoom = False

        # Flag to track if the page is ready for zoom operations
        self._page_ready = False

        # Initialize zoom variables
        self._initialize_zoom_variables()

    def _initialize_zoom_variables(self):
        """Initialize zoom variables in the web page"""
        # First set the CSS variable
        css_script = f"""
        (function() {{
            var result = false;
            // Set zoom factor as a CSS variable for consistent reference
            if (document && document.documentElement && document.documentElement.style) {{
                document.documentElement.style.setProperty('--zoom-factor', '{self.zoom_factor}');
                result = true;
            }}
            return result;
        }})();
        """

        # Then check if the page is ready for zoom operations
        ready_script = """
        (function() {
            var result = false;
            try {
                // Check if document is ready
                if (!document || !document.body) {
                    console.log('Document not ready for zoom operations');
                    result = false;
                }
                else {
                    // Check if pages exist
                    var pages = document.querySelectorAll('.page');
                    if (!pages || pages.length === 0) {
                        console.log('No pages found for zoom operations');
                        result = false;
                    }
                    else {
                        console.log('Document ready for zoom operations, found ' + pages.length + ' pages');
                        result = true;
                    }
                }
            } catch (e) {
                console.error('Error checking document readiness:', e);
                result = false;
            }
            return result;
        })();
        """

        # First set the CSS variable
        try:
            self.web_page.runJavaScript(css_script, lambda result:
                self._handle_initialization_result(result))

            # Then check if the page is ready for zoom operations
            self.web_page.runJavaScript(ready_script, lambda result:
                self._handle_page_ready_check(result))
        except Exception as e:
            logger.error(f"Error initializing zoom variables: {str(e)}")
            self._page_ready = False

    def _handle_initialization_result(self, result):
        """Handle the result of initialization"""
        logger.debug(f"Zoom variables initialized: {result}")
        # Don't set page_ready here, wait for the page ready check

    def _handle_page_ready_check(self, result):
        """Handle the result of page ready check"""
        logger.debug(f"Page ready check result: {result}")
        self._page_ready = bool(result)

    def update_zoom(self, zoom_value):
        """
        Update the zoom level

        Args:
            zoom_value: Zoom percentage (100 = 100%)
        """
        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug(f"Zoom operation already in progress, skipping update_zoom({zoom_value})")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Store the zoom value for later application
            self.current_zoom = zoom_value
            # Schedule a delayed zoom application
            QTimer.singleShot(300, lambda: self._delayed_zoom_update(zoom_value))
            return

        try:
            self._updating_zoom = True

            # Calculate the zoom factor (percentage to decimal)
            self.zoom_factor = zoom_value / 100.0
            self.current_zoom = zoom_value
            logger.debug(f"Setting zoom factor to {self.zoom_factor}")

            # Apply zoom to the page using JavaScript
            script = f"""
            (function() {{
                try {{
                    // Set zoom factor as a CSS variable for consistent reference
                    if (document && document.documentElement && document.documentElement.style) {{
                        document.documentElement.style.setProperty('--zoom-factor', '{self.zoom_factor}');
                        console.log('Set zoom factor CSS variable to {self.zoom_factor}');
                    }}

                    // Apply zoom to pages
                    var pages = document.querySelectorAll('.page');
                    if (pages && pages.length > 0) {{
                        for (var i = 0; i < pages.length; i++) {{
                            if (pages[i] && pages[i].style) {{
                                pages[i].style.transform = 'scale({self.zoom_factor})';
                                pages[i].style.transformOrigin = 'center center';  // Changed from 'top center' to properly center
                                pages[i].style.margin = '20px auto 40px auto';
                            }}
                        }}
                        console.log('Applied zoom to ' + pages.length + ' pages');

                        // Calculate scroll position to center the current page
                        var currentPage = document.querySelector('.page.current-page') || pages[0];
                        if (currentPage) {{
                            var rect = currentPage.getBoundingClientRect();
                            var viewportHeight = window.innerHeight;
                            var scrollNeeded = rect.top + (rect.height - viewportHeight) / 2;

                            // Only scroll if we need to
                            if (scrollNeeded > 0) {{
                                window.scrollTo({{
                                    top: window.scrollY + scrollNeeded,
                                    behavior: 'smooth'
                                }});
                            }}
                        }}

                        return 'Zoom applied to pages';
                    }}

                    // Fallback: Apply to body
                    if (document && document.body && document.body.style) {{
                        document.body.style.transform = 'scale({self.zoom_factor})';
                        document.body.style.transformOrigin = 'center center';  // Changed from 'top center'
                        console.log('Applied zoom to body');
                        return 'Zoom applied to body';
                    }}

                    return 'No elements found to apply zoom';
                }} catch (e) {{
                    console.error('Error applying zoom:', e);
                    return 'Error: ' + e.message;
                }}
            }})();
            """

            self.web_page.runJavaScript(script, lambda result:
                logger.debug(f"Zoom update result: {result}"))
        finally:
            # Clear the updating flag with a delay to prevent immediate re-entry
            QTimer.singleShot(500, lambda: setattr(self, '_updating_zoom', False))

    def _delayed_zoom_update(self, zoom_value):
        """Apply zoom after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed zoom update: {zoom_value}%")
            self.update_zoom(zoom_value)
        else:
            logger.debug(f"Page still not ready for zoom, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_zoom_update(zoom_value))

    def fit_to_page(self, view_width, view_height):
        """
        Fit the page to the view (both width and height)

        Args:
            view_width: Width of the view in pixels
            view_height: Height of the view in pixels
        """
        logger.debug(f"Fitting page to view: {view_width}x{view_height}")

        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug("Zoom operation already in progress, skipping fit_to_page")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Schedule a delayed fit_to_page operation
            QTimer.singleShot(300, lambda: self._delayed_fit_to_page(view_width, view_height))
            return

        self._updating_zoom = True

        try:
            if view_width <= 0 or view_height <= 0:
                logger.warning(f"Invalid view dimensions: {view_width}x{view_height}, using defaults")
                view_width = 800
                view_height = 600

            # Calculate the zoom factor to fit the page
            script = f"""
            (function() {{
                try {{
                    // Find the first page
                    var page = document.querySelector('.page');
                    if (!page) {{
                        console.log('No page element found for fit_to_page');
                        return 0.9; // Default zoom
                    }}

                    // Get page dimensions
                    var pageWidth = page.offsetWidth;
                    var pageHeight = page.offsetHeight;

                    // If dimensions are invalid, use defaults
                    if (!pageWidth || pageWidth <= 0) {{
                        console.warn('Invalid page width, using default: 210mm');
                        pageWidth = 793; // Approximate pixel equivalent of 210mm
                    }}

                    if (!pageHeight || pageHeight <= 0) {{
                        console.warn('Invalid page height, using default: 297mm');
                        pageHeight = 1122; // Approximate pixel equivalent of 297mm
                    }}

                    // Calculate zoom factors for width and height
                    var widthZoom = ({view_width} * 0.9) / pageWidth;
                    var heightZoom = ({view_height} * 0.9) / pageHeight;

                    // Use the smaller zoom factor to ensure the entire page fits
                    var zoomFactor = Math.min(widthZoom, heightZoom);

                    // Limit zoom factor to reasonable range (25% to 150%)
                    zoomFactor = Math.max(0.25, Math.min(1.5, zoomFactor));

                    console.log('Calculated zoom factor for fit to page:', zoomFactor,
                                'View dimensions:', {view_width}, 'x', {view_height},
                                'Page dimensions:', pageWidth, 'x', pageHeight);

                    // Center the page vertically
                    setTimeout(function() {{
                        try {{
                            var page = document.querySelector('.page');
                            if (page) {{
                                var rect = page.getBoundingClientRect();
                                var viewportHeight = window.innerHeight;

                                // Center in viewport
                                if (rect.height < viewportHeight) {{
                                    // If page is smaller than viewport, center it
                                    var topSpace = (viewportHeight - rect.height) / 2;
                                    window.scrollTo(0, Math.max(0, rect.top + window.scrollY - topSpace));
                                }} else {{
                                    // If page is larger, ensure it's positioned at the top
                                    window.scrollTo(0, 0);
                                }}
                            }}
                        }} catch (e) {{
                            console.error('Error centering page:', e);
                        }}
                    }}, 100); // Small delay to allow for DOM updates

                    return zoomFactor;
                }} catch (e) {{
                    console.error('Error in fit_to_page:', e);
                    return 0.9; // Default zoom on error
                }}
            }})();
            """

            # Execute the script and update the zoom
            self.web_page.runJavaScript(script, lambda zoom_factor:
                self.update_zoom(int((zoom_factor or 0.9) * 100)))
        finally:
            # Clear the updating flag with a delay to prevent immediate re-entry
            QTimer.singleShot(500, lambda: setattr(self, '_updating_zoom', False))

    def _delayed_fit_to_page(self, view_width, view_height):
        """Apply fit_to_page after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed fit_to_page: {view_width}x{view_height}")
            self.fit_to_page(view_width, view_height)
        else:
            logger.debug(f"Page still not ready for fit_to_page, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_fit_to_page(view_width, view_height))

    def fit_to_width(self, view_width):
        """
        Fit the page width to the view

        Args:
            view_width: Width of the view in pixels
        """
        logger.debug(f"Fitting page width to view: {view_width}")

        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug("Zoom operation already in progress, skipping fit_to_width")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Schedule a delayed fit_to_width operation
            QTimer.singleShot(300, lambda: self._delayed_fit_to_width(view_width))
            return

        self._updating_zoom = True

        try:
            if view_width <= 0:
                logger.warning(f"Invalid view width: {view_width}, using default")
                view_width = 800

            # Calculate the zoom factor to fit the page width
            script = f"""
            (function() {{
                try {{
                    // Find the first page
                    var page = document.querySelector('.page');
                    if (!page) {{
                        console.log('No page element found for fit_to_width');
                        return 0.9; // Default zoom
                    }}

                    // Get page width
                    var pageWidth = page.offsetWidth;

                    // If width is invalid, use default
                    if (!pageWidth || pageWidth <= 0) {{
                        console.warn('Invalid page width, using default: 210mm');
                        pageWidth = 793; // Approximate pixel equivalent of 210mm
                    }}

                    // Calculate zoom factor (with some margin for scrollbar)
                    var zoomFactor = ({view_width} * 0.95) / pageWidth;

                    // Limit zoom factor to reasonable range (25% to 150%)
                    zoomFactor = Math.max(0.25, Math.min(1.5, zoomFactor));

                    console.log('Calculated zoom factor for fit to width:', zoomFactor,
                                'View width:', {view_width},
                                'Page width:', pageWidth);

                    // Center the page horizontally and scroll to top
                    setTimeout(function() {{
                        try {{
                            // For horizontal centering, CSS should handle it with margin: auto
                            // Just scroll to top for the most predictable experience
                            window.scrollTo(0, 0);
                        }} catch (e) {{
                            console.error('Error scrolling to top:', e);
                        }}
                    }}, 100); // Small delay to allow for DOM updates

                    return zoomFactor;
                }} catch (e) {{
                    console.error('Error in fit_to_width:', e);
                    return 0.9; // Default zoom on error
                }}
            }})();
            """

            # Execute the script and update the zoom
            self.web_page.runJavaScript(script, lambda zoom_factor:
                self.update_zoom(int((zoom_factor or 0.9) * 100)))
        finally:
            # Clear the updating flag with a delay to prevent immediate re-entry
            QTimer.singleShot(500, lambda: setattr(self, '_updating_zoom', False))

    def _delayed_fit_to_width(self, view_width):
        """Apply fit_to_width after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed fit_to_width: {view_width}")
            self.fit_to_width(view_width)
        else:
            logger.debug(f"Page still not ready for fit_to_width, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_fit_to_width(view_width))

    def reset_zoom(self):
        """Reset zoom to 100%"""
        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug("Zoom operation already in progress, skipping reset_zoom")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Schedule a delayed reset_zoom operation
            QTimer.singleShot(300, lambda: self._delayed_reset_zoom())
            return

        self.update_zoom(100)

    def _delayed_reset_zoom(self):
        """Apply reset_zoom after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed reset_zoom")
            self.reset_zoom()
        else:
            logger.debug(f"Page still not ready for reset_zoom, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_reset_zoom())

    def zoom_in(self, step=10):
        """
        Zoom in by the specified step

        Args:
            step: Zoom step percentage (default: 10%)
        """
        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug("Zoom operation already in progress, skipping zoom_in")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Schedule a delayed zoom_in operation
            QTimer.singleShot(300, lambda: self._delayed_zoom_in(step))
            return

        new_zoom = min(self.current_zoom + step, 200)
        self.update_zoom(new_zoom)

    def _delayed_zoom_in(self, step=10):
        """Apply zoom_in after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed zoom_in: {step}%")
            self.zoom_in(step)
        else:
            logger.debug(f"Page still not ready for zoom_in, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_zoom_in(step))

    def zoom_out(self, step=10):
        """
        Zoom out by the specified step

        Args:
            step: Zoom step percentage (default: 10%)
        """
        # Prevent recursive calls
        if self._updating_zoom:
            logger.debug("Zoom operation already in progress, skipping zoom_out")
            return

        # Check if the page is ready for zoom operations
        if not self._page_ready:
            logger.debug(f"Page not ready for zoom operations, initializing first")
            self._initialize_zoom_variables()
            # Schedule a delayed zoom_out operation
            QTimer.singleShot(300, lambda: self._delayed_zoom_out(step))
            return

        new_zoom = max(self.current_zoom - step, 25)
        self.update_zoom(new_zoom)

    def _delayed_zoom_out(self, step=10):
        """Apply zoom_out after a delay to ensure page is ready"""
        if self._page_ready and not self._updating_zoom:
            logger.debug(f"Applying delayed zoom_out: {step}%")
            self.zoom_out(step)
        else:
            logger.debug(f"Page still not ready for zoom_out, scheduling another attempt")
            QTimer.singleShot(300, lambda: self._delayed_zoom_out(step))

    def __del__(self):
        """Destructor to clean up resources"""
        try:
            pass  # No special cleanup needed for this class
        except Exception as e:
            # Suppress errors during cleanup in destructor
            pass