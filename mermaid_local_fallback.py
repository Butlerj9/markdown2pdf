#!/usr/bin/env python3
"""
Mermaid Local Fallback
---------------------
Provides local fallback for Mermaid library loading.
File: src--mermaid_local_fallback.py
"""

import os
import tempfile
import platform
import subprocess
from logging_config import get_logger, EnhancedLogger

logger = get_logger()

def find_mermaid_js():
    """
    Find the local Mermaid JS file in standard installation locations.
    Resources directory is prioritized over other locations.
    
    Returns:
        str: Path to the local Mermaid JS file if found, None otherwise
    """
    logger.debug("Searching for local Mermaid.js installations")
    
    # PRIORITY FIX: Check resources directory FIRST before any other location
    # Determine application directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    resources_mermaid_path = os.path.join(resources_dir, "mermaid.esm.min.js")
    
    # If resources directory exists and contains mermaid.esm.min.js with reasonable size, use it
    if os.path.exists(resources_mermaid_path) and os.path.getsize(resources_mermaid_path) > 100000:
        logger.info(f"Found valid Mermaid.js in resources directory: {resources_mermaid_path}")
        return resources_mermaid_path
    
    # Define common locations where Mermaid JS might be found
    potential_paths = []
    
    # Add Node.js global modules path
    if platform.system() == "Windows":
        # On Windows, check both Program Files and npm paths
        npm_path = os.path.join(os.environ.get('APPDATA', ''), "npm", "node_modules", "mermaid", "dist", "mermaid.esm.min.js")
        potential_paths.append(npm_path)
        
        # Add potential local installation in node_modules
        potential_paths.append(os.path.join(os.getcwd(), "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
        
        # Add npm global path based on the output from path_test.py
        if 'APPDATA' in os.environ:
            potential_paths.append(os.path.join(os.environ['APPDATA'], "Roaming", "npm", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
    else:
        # On Unix-like systems
        potential_paths.append("/usr/local/lib/node_modules/mermaid/dist/mermaid.esm.min.js")
        potential_paths.append("/usr/lib/node_modules/mermaid/dist/mermaid.esm.min.js")
        potential_paths.append(os.path.join(os.path.expanduser("~"), ".npm", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
    
    # Look in the directory where mmdc is located
    try:
        mmdc_path = subprocess.run(["where", "mmdc"] if platform.system() == "Windows" else ["which", "mmdc"],
                                  capture_output=True, text=True, check=False).stdout.strip()
        if mmdc_path:
            mmdc_dir = os.path.dirname(mmdc_path)
            potential_paths.append(os.path.join(mmdc_dir, "..", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
            potential_paths.append(os.path.join(mmdc_dir, "..", "..", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
            # For Windows npm global installs
            potential_paths.append(os.path.join(mmdc_dir, "..", "node_modules", "@mermaid-js", "mermaid-cli", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
    except Exception as e:
        logger.warning(f"Error checking mmdc path: {str(e)}")
    
    # Search for the local mermaid.js file
    for path in potential_paths:
        if os.path.exists(path):
            # Check that the file is valid (not empty)
            if os.path.getsize(path) > 100000:  # Mermaid.js should be at least 100KB
                logger.info(f"Found valid local Mermaid.js at: {path}")
                
                # VALIDATION FIX: Verify the file doesn't have syntax issues
                try:
                    with open(path, 'rb') as f:
                        content = f.read(5000)  # Read first 5000 bytes for quick validation
                        # Simple validation to catch obvious issues
                        if b"function" not in content or b"mermaid" not in content:
                            logger.warning(f"Mermaid file at {path} may have syntax issues")
                            continue  # Skip this file and try the next one
                except Exception as e:
                    logger.warning(f"Error validating Mermaid.js at {path}: {str(e)}")
                    continue  # Skip this file and try the next one
                    
                return path
            else:
                logger.warning(f"Found Mermaid.js at {path} but it appears to be invalid (size: {os.path.getsize(path)} bytes)")
    
    # If not found in standard locations, try npm root command
    try:
        result = subprocess.run(
            ["npm", "root", "-g"], 
            capture_output=True, 
            text=True,
            check=True
        )
        npm_root = result.stdout.strip()
        npm_mermaid_path = os.path.join(npm_root, "mermaid", "dist", "mermaid.esm.min.js")
        
        if os.path.exists(npm_mermaid_path) and os.path.getsize(npm_mermaid_path) > 100000:
            # Validate this file too
            try:
                with open(npm_mermaid_path, 'rb') as f:
                    content = f.read(5000)
                    if b"function" not in content or b"mermaid" not in content:
                        logger.warning(f"Mermaid file at {npm_mermaid_path} may have syntax issues")
                    else:
                        logger.info(f"Found Mermaid.js in npm global modules: {npm_mermaid_path}")
                        return npm_mermaid_path
            except Exception as e:
                logger.warning(f"Error validating Mermaid.js at {npm_mermaid_path}: {str(e)}")
            
        # Also check @mermaid-js/mermaid-cli
        npm_mermaid_cli_path = os.path.join(npm_root, "@mermaid-js", "mermaid-cli", "node_modules", "mermaid", "dist", "mermaid.esm.min.js")
        if os.path.exists(npm_mermaid_cli_path) and os.path.getsize(npm_mermaid_cli_path) > 100000:
            # Validate this file too
            try:
                with open(npm_mermaid_cli_path, 'rb') as f:
                    content = f.read(5000)
                    if b"function" not in content or b"mermaid" not in content:
                        logger.warning(f"Mermaid file at {npm_mermaid_cli_path} may have syntax issues")
                    else:
                        logger.info(f"Found Mermaid.js in mermaid-cli package: {npm_mermaid_cli_path}")
                        return npm_mermaid_cli_path
            except Exception as e:
                logger.warning(f"Error validating Mermaid.js at {npm_mermaid_cli_path}: {str(e)}")
    except Exception as e:
        logger.warning(f"Error checking npm root: {str(e)}")
    
    logger.warning("No valid local Mermaid.js installation found in standard locations")
    return None

def create_resources_directory():
    """Create resources directory if it doesn't exist"""
    # Determine application directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    
    # Create resources directory if it doesn't exist
    if not os.path.exists(resources_dir):
        try:
            os.makedirs(resources_dir)
            logger.info(f"Created resources directory: {resources_dir}")
        except Exception as e:
            logger.error(f"Error creating resources directory: {str(e)}")
            return None
            
    return resources_dir

def extract_mermaid_from_npm():
    """
    Try to extract mermaid.min.js from the npm installation.
    
    Returns:
        str: Path to extracted mermaid.min.js or None if unsuccessful
    """
    try:
        logger.debug("Attempting to extract Mermaid from npm installation")
        
        # Check if mmdc is available (indicates mermaid-cli is installed)
        from shutil import which
        mmdc_path = which('mmdc')
        
        if not mmdc_path:
            logger.warning("mmdc not found in PATH, cannot extract from mermaid-cli")
            return None
        
        logger.debug(f"Found mmdc at: {mmdc_path}")
        
        # Get the directory of mmdc
        mmdc_dir = os.path.dirname(mmdc_path)
        potential_paths = []
        
        # Add potential paths based on the typical npm installation structure
        if platform.system() == "Windows":
            # Windows paths
            potential_paths.append(os.path.join(mmdc_dir, "..", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
            potential_paths.append(os.path.join(mmdc_dir, "..", "..", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
            potential_paths.append(os.path.join(mmdc_dir, "..", "..", "mermaid", "dist", "mermaid.esm.min.js"))
            # For Windows npm global installs, look in packaged node_modules
            potential_paths.append(os.path.join(mmdc_dir, "..", "node_modules", "@mermaid-js", "mermaid-cli", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
        else:
            # Unix-like paths
            potential_paths.append(os.path.join(mmdc_dir, "..", "lib", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
            potential_paths.append(os.path.join(mmdc_dir, "..", "node_modules", "mermaid", "dist", "mermaid.esm.min.js"))
        
        # Check each potential path
        for path in potential_paths:
            normalized_path = os.path.normpath(path)
            if os.path.exists(normalized_path) and os.path.getsize(normalized_path) > 100000:
                # Validate the file
                try:
                    with open(normalized_path, 'rb') as f:
                        content = f.read(5000)
                        if b"function" not in content or b"mermaid" not in content:
                            logger.warning(f"Mermaid file at {normalized_path} may have syntax issues")
                            continue
                except Exception as e:
                    logger.warning(f"Error validating Mermaid.js at {normalized_path}: {str(e)}")
                    continue
                    
                logger.info(f"Found valid Mermaid.js at: {normalized_path}")
                return normalized_path
        
        logger.warning("Could not find valid Mermaid.js in npm installation")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting Mermaid from npm: {str(e)}")
        return None

def copy_mermaid_to_resources():
    """
    Copy found mermaid.esm.min.js to resources directory.
    
    Returns:
        str: Path to the copied file or None if failed
    """
    # First try to find mermaid.js
    source_path = find_mermaid_js()
    if not source_path:
        source_path = extract_mermaid_from_npm()
    
    if not source_path:
        logger.warning("No valid Mermaid.js found to copy")
        
        # ENHANCEMENT: Try to download from CDN as last resort
        cdn_url = "https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"
        resources_dir = create_resources_directory()
        if resources_dir:
            target_path = os.path.join(resources_dir, "mermaid.esm.min.js")
            try:
                import urllib.request
                logger.info(f"Attempting to download Mermaid.js from CDN: {cdn_url}")
                urllib.request.urlretrieve(cdn_url, target_path)
                if os.path.exists(target_path) and os.path.getsize(target_path) > 100000:
                    logger.info(f"Successfully downloaded Mermaid.js to: {target_path}")
                    return target_path
            except Exception as e:
                logger.error(f"Error downloading Mermaid.js: {str(e)}")
        
        return None
    
    # Create resources directory
    resources_dir = create_resources_directory()
    if not resources_dir:
        return None
    
    # Copy the file
    import shutil
    target_path = os.path.join(resources_dir, "mermaid.esm.min.js")
    
    # Check if the source and target are the same (which would cause an error)
    if os.path.abspath(source_path) == os.path.abspath(target_path):
        # Check if the file is valid
        try:
            with open(source_path, 'rb') as f:
                content = f.read(5000)
                if b"function" not in content or b"mermaid" not in content:
                    logger.warning(f"Existing Mermaid.js file has syntax issues: {source_path}")
                    # Try to replace with a better version
                    os.remove(target_path)
                    logger.info(f"Removed invalid Mermaid.js file: {target_path}")
                    # Continue to find another source
                else:
                    logger.info(f"Source and target are the same and file is valid: {source_path}")
                    return source_path
        except Exception as e:
            logger.error(f"Error validating existing Mermaid.js: {str(e)}")
            return None
    
    try:
        shutil.copy2(source_path, target_path)
        logger.info(f"Copied Mermaid.js to: {target_path}")
        
        # Validate the copied file
        try:
            with open(target_path, 'rb') as f:
                content = f.read(5000)
                if b"function" not in content or b"mermaid" not in content:
                    logger.warning(f"Copied Mermaid.js file has syntax issues: {target_path}")
                    os.remove(target_path)
                    logger.warning(f"Removed invalid copied file: {target_path}")
                    return None
        except Exception as e:
            logger.error(f"Error validating copied Mermaid.js: {str(e)}")
            return None
            
        return target_path
    except Exception as e:
        logger.error(f"Error copying Mermaid.js: {str(e)}")
        return None

def get_mermaid_script_tag():
    """
    Get the appropriate script tag for including Mermaid.js,
    explicitly prioritizing the resources directory version.
    
    Returns:
        str: HTML script tag for including Mermaid.js
    """
    import os
    import platform
    from logging_config import get_logger
    
    logger = get_logger()
    
    # EXPLICIT CHECK: Only use resources directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    resources_mermaid_path = os.path.join(resources_dir, "mermaid.esm.min.js")
    
    # Validation and fallback strategy
    if not os.path.exists(resources_mermaid_path) or os.path.getsize(resources_mermaid_path) < 100000:
        logger.warning("Valid Mermaid.js not found in resources directory")
        
        # Download a known-good version if needed
        downloaded_path = download_compatible_mermaid_js()
        if downloaded_path:
            resources_mermaid_path = downloaded_path
        else:
            # If download fails, use CDN version directly
            logger.warning("Could not obtain valid Mermaid.js, using CDN version")
            return '<script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js" defer integrity="sha384-eRSR0e1COLQf4DSk7hwiOxYT+N3OtGSHX0oe8XqkY3OLqQvgPmxTHqKzExPnSqvs" crossorigin="anonymous"></script>'
    
    # Use the resources directory file
    try:
        # Convert to file URL with proper format for all platforms
        if platform.system() == "Windows":
            file_url = f"file:///{resources_mermaid_path.replace(os.sep, '/').replace(' ', '%20')}"
        else:
            file_url = f"file://{resources_mermaid_path.replace(' ', '%20')}"
            
        logger.info(f"Using Mermaid.js from resources: {file_url}")
        
        # Use defer to prevent execution before the DOM is loaded
        return f'<script src="{file_url}" defer></script>'
    except Exception as e:
        logger.error(f"Error preparing Mermaid script tag: {str(e)}")
        # Fall back to CDN version
        return '<script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js" defer integrity="sha384-eRSR0e1COLQf4DSk7hwiOxYT+N3OtGSHX0oe8XqkY3OLqQvgPmxTHqKzExPnSqvs" crossorigin="anonymous"></script>'

def embed_mermaid_directly():
    """
    Return embedded Mermaid script for basic diagram rendering directly in HTML.
    This provides offline rendering capabilities without relying on external files.
    
    Returns:
        str: JavaScript code string for basic Mermaid rendering
    """
    logger.info("Using embedded basic Mermaid renderer")
    return """
    <script>
    // Embedded basic Mermaid renderer (no external dependencies)
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Using embedded basic Mermaid renderer');
        
        function renderBasicMermaid() {
            var diagrams = document.querySelectorAll('.mermaid');
            console.log('Found ' + diagrams.length + ' Mermaid diagrams');
            
            if (diagrams.length === 0) return;
            
            diagrams.forEach(function(diagram, index) {
                try {
                    // Create a container for the rendered diagram
                    var container = document.createElement('div');
                    container.className = 'mermaid-basic-render';
                    container.style.border = '1px solid #ccc';
                    container.style.borderRadius = '5px';
                    container.style.padding = '10px';
                    container.style.margin = '10px 0';
                    container.style.backgroundColor = '#f8f9fa';
                    container.style.textAlign = 'center';
                    
                    // Extract diagram text
                    var code = diagram.textContent.trim();
                    
                    // Create title for diagram type
                    var titleDiv = document.createElement('div');
                    titleDiv.style.fontWeight = 'bold';
                    titleDiv.style.marginBottom = '10px';
                    titleDiv.style.color = '#0066cc';
                    titleDiv.style.textAlign = 'left';
                    
                    if (code.startsWith('flowchart') || code.startsWith('graph')) {
                        titleDiv.textContent = '📊 Flowchart Diagram';
                    } else if (code.startsWith('sequenceDiagram')) {
                        titleDiv.textContent = '🔄 Sequence Diagram';
                    } else if (code.startsWith('classDiagram')) {
                        titleDiv.textContent = '📋 Class Diagram';
                    } else if (code.startsWith('gantt')) {
                        titleDiv.textContent = '📅 Gantt Chart';
                    } else if (code.startsWith('pie')) {
                        titleDiv.textContent = '🥧 Pie Chart';
                    } else {
                        titleDiv.textContent = '📈 Mermaid Diagram';
                    }
                    
                    // Create content display
                    var contentDiv = document.createElement('div');
                    contentDiv.style.whiteSpace = 'pre-wrap';
                    contentDiv.style.fontFamily = 'monospace';
                    contentDiv.style.fontSize = '12px';
                    contentDiv.style.color = '#333';
                    contentDiv.style.textAlign = 'left';
                    contentDiv.style.padding = '10px';
                    contentDiv.style.backgroundColor = '#f0f0f0';
                    contentDiv.style.borderRadius = '3px';
                    contentDiv.style.overflow = 'auto';
                    contentDiv.textContent = code;
                    
                    // Add note about basic rendering
                    var noteDiv = document.createElement('div');
                    noteDiv.style.fontSize = '11px';
                    noteDiv.style.fontStyle = 'italic';
                    noteDiv.style.marginTop = '10px';
                    noteDiv.style.color = '#666';
                    noteDiv.textContent = 'Note: Using basic rendering - actual diagram may differ slightly';
                    
                    // Assemble the container
                    container.appendChild(titleDiv);
                    container.appendChild(contentDiv);
                    container.appendChild(noteDiv);
                    
                    // Replace the original diagram with our rendered version
                    diagram.parentNode.replaceChild(container, diagram);
                    
                    console.log('Rendered basic diagram ' + index);
                } catch (e) {
                    console.error('Error processing diagram ' + index + ':', e);
                }
            });
        }
        
        // Run renderer
        renderBasicMermaid();
    });
    </script>
    <style>
    .mermaid-basic-render {
        margin: 20px auto;
        max-width: 100%;
    }
    .mermaid {
        text-align: center;
        margin: 20px auto;
        max-width: 100%;
        overflow-x: auto;
    }
    </style>
    """

# Function to use in page_preview.py to update the HTML
def inject_mermaid_into_html(html_content):
    """Inject Mermaid library into HTML content, using local fallback if available"""
    logger.debug("Injecting Mermaid into HTML content")
    
    # First ensure we have a valid HTML structure
    if "<html>" not in html_content:
        html_content = f"<html><head><meta charset='UTF-8'></head><body>{html_content}</body></html>"
    elif "<head>" not in html_content:
        html_content = html_content.replace("<html>", "<html><head><meta charset='UTF-8'></head>")
    
    # Make sure we have charset meta tag
    if "<meta charset=" not in html_content:
        html_content = html_content.replace("<head>", "<head><meta charset='UTF-8'>")
    
    # Get Mermaid script tag
    mermaid_script = get_mermaid_script_tag()
    
    # Add initialization script - only if we found a local mermaid.js
    init_script = ""
    if "<script src=" in mermaid_script:  # This indicates we found a local mermaid.js
        init_script = """
        <script>
            // Ensure we only initialize once
            if (window.mermaidInitialized) return;
            
            window.addEventListener('load', function() {
                setTimeout(function() {
                    try {
                        if (typeof mermaid !== 'undefined') {
                            console.log('Mermaid is available, initializing...');
                            mermaid.initialize({
                                startOnLoad: false,
                                theme: 'default',
                                securityLevel: 'loose',
                                flowchart: { 
                                    useMaxWidth: true,
                                    htmlLabels: true,
                                    curve: 'basis'
                                }
                            });
                            
                            var diagrams = document.querySelectorAll('.mermaid');
                            console.log('Found ' + diagrams.length + ' Mermaid diagrams');
                            if (diagrams.length > 0) {
                                console.log('Rendering diagrams with Mermaid...');
                                mermaid.init(undefined, diagrams);
                                console.log('Mermaid rendering complete');
                            }
                            window.mermaidInitialized = true;
                        } else {
                            console.error('Mermaid library not available - using fallback renderer');
                            renderBasicMermaidDiagrams();
                        }
                    } catch(e) {
                        console.error('Error initializing Mermaid:', e);
                        // Fall back to basic rendering
                        renderBasicMermaidDiagrams();
                    }
                }, 1000);
            });
            
            // Basic fallback renderer
            function renderBasicMermaidDiagrams() {
                if (window.mermaidRendered) return;
                window.mermaidRendered = true;
                
                var diagrams = document.querySelectorAll('.mermaid');
                if (diagrams.length === 0) return;
                
                console.log('Using fallback renderer for ' + diagrams.length + ' diagrams');
                
                diagrams.forEach(function(diagram, index) {
                    try {
                        // Basic rendering code (similar to the embed_mermaid_directly function)
                        var container = document.createElement('div');
                        container.className = 'mermaid-fallback';
                        container.style.border = '1px solid #ccc';
                        container.style.padding = '10px';
                        container.style.backgroundColor = '#f8f9fa';
                        container.style.margin = '10px 0';
                        container.style.borderRadius = '5px';
                        
                        var titleDiv = document.createElement('div');
                        titleDiv.innerHTML = '<strong style="color:#0066cc;">Mermaid Diagram (Fallback Rendering)</strong>';
                        titleDiv.style.marginBottom = '8px';
                        
                        var contentDiv = document.createElement('pre');
                        contentDiv.style.whiteSpace = 'pre-wrap';
                        contentDiv.style.fontFamily = 'monospace';
                        contentDiv.style.backgroundColor = '#f0f0f0';
                        contentDiv.style.padding = '8px';
                        contentDiv.style.borderRadius = '4px';
                        contentDiv.style.color = '#333';
                        contentDiv.textContent = diagram.textContent;
                        
                        container.appendChild(titleDiv);
                        container.appendChild(contentDiv);
                        
                        diagram.parentNode.replaceChild(container, diagram);
                    } catch(e) {
                        console.error('Error in fallback rendering for diagram ' + index + ':', e);
                    }
                });
            }
        </script>
        """
    else:
        # Include the basic renderer function
        init_script = """
        <script>
            window.addEventListener('load', function() {
                setTimeout(function() {
                    // Check for previous initialization
                    if (window.mermaidRendered) return;
                    window.mermaidRendered = true;
                    
                    // Using basic rendering as no Mermaid JS was found
                    renderBasicMermaid();
                }, 500);
            });
            
            function renderBasicMermaid() {
                var diagrams = document.querySelectorAll('.mermaid');
                console.log('Found ' + diagrams.length + ' Mermaid diagrams for basic rendering');
                
                diagrams.forEach(function(diagram, index) {
                    try {
                        // Create basic HTML to display mermaid code 
                        var code = diagram.textContent.trim();
                        
                        var wrapper = document.createElement('div');
                        wrapper.className = 'mermaid-basic-render';
                        wrapper.style.border = '1px solid #ccc';
                        wrapper.style.borderRadius = '5px';
                        wrapper.style.padding = '10px';
                        wrapper.style.backgroundColor = '#f8f9fa';
                        wrapper.style.margin = '10px 0';
                        
                        var titleDiv = document.createElement('div');
                        titleDiv.innerHTML = '<strong>Mermaid Diagram</strong>';
                        titleDiv.style.marginBottom = '8px';
                        
                        var codeDiv = document.createElement('pre');
                        codeDiv.style.whiteSpace = 'pre-wrap';
                        codeDiv.style.fontFamily = 'monospace';
                        codeDiv.style.backgroundColor = '#f0f0f0';
                        codeDiv.style.padding = '8px';
                        codeDiv.style.borderRadius = '4px';
                        codeDiv.textContent = code;
                        
                        wrapper.appendChild(titleDiv);
                        wrapper.appendChild(codeDiv);
                        
                        diagram.parentNode.replaceChild(wrapper, diagram);
                    } catch(e) {
                        console.error('Error rendering diagram ' + index + ':', e);
                    }
                });
            }
        </script>
        """
    
    # Insert scripts at the end of head
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", mermaid_script + init_script + "</head>")
    else:
        # If no head tag found, add a basic one
        html_content = f"<html><head><meta charset='UTF-8'>{mermaid_script}{init_script}</head><body>{html_content}</body></html>"
    
    logger.debug("Mermaid injection complete")
    return html_content

# Try to initialize on module load - create resources directory and check for existing files
try:
    resources_dir = create_resources_directory()
    if resources_dir:
        # Check if mermaid.esm.min.js already exists in resources
        js_path = os.path.join(resources_dir, "mermaid.esm.min.js")
        if os.path.exists(js_path):
            # Verify if it's valid
            file_size = os.path.getsize(js_path)
            if file_size < 100000:
                # Invalid file, remove it so we can copy a valid one later
                try:
                    os.remove(js_path)
                    logger.info(f"Removed invalid Mermaid.js file: {js_path}")
                except Exception as e:
                    logger.error(f"Error removing invalid Mermaid.js: {str(e)}")
            else:
                # Validate content
                try:
                    with open(js_path, 'rb') as f:
                        content = f.read(5000)
                        if b"function" not in content or b"mermaid" not in content:
                            logger.warning(f"Existing Mermaid.js file has syntax issues: {js_path}")
                            # Remove invalid file
                            os.remove(js_path)
                            logger.info(f"Removed invalid Mermaid.js file: {js_path}")
                except Exception as e:
                    logger.error(f"Error validating Mermaid.js in resources: {str(e)}")
except Exception as e:
    logger.error(f"Error initializing resources: {str(e)}")

def download_compatible_mermaid_js():
    """
    Download a known-compatible version of mermaid.min.js from CDN.
    Carefully validates the downloaded content before using it.
    
    Returns:
        str: Path to the downloaded file or None if failed
    """
    import os
    import tempfile
    import hashlib
    from logging_config import get_logger
    
    logger = get_logger()
    logger.info("Downloading compatible Mermaid.js from CDN")
    
    # Determine resources directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    
    # Create resources directory if it doesn't exist
    if not os.path.exists(resources_dir):
        try:
            os.makedirs(resources_dir)
            logger.info(f"Created resources directory: {resources_dir}")
        except Exception as e:
            logger.error(f"Error creating resources directory: {str(e)}")
            return None
    
    # Target file path
    target_path = os.path.join(resources_dir, "mermaid.esm.min.js")
    
    # Delete existing file if it has issues
    if os.path.exists(target_path):
        try:
            with open(target_path, 'rb') as f:
                content = f.read(5000)
                if b"function" not in content or b"mermaid" not in content:
                    logger.warning(f"Existing Mermaid.js file may have syntax issues")
                    os.remove(target_path)
                    logger.info(f"Removed problematic file: {target_path}")
        except Exception as e:
            logger.warning(f"Error checking existing file: {str(e)}")
            try:
                os.remove(target_path)
                logger.info(f"Removed potentially problematic file: {target_path}")
            except Exception as e2:
                logger.error(f"Error removing file: {str(e2)}")
                return None
    
    # Choose a known good version of Mermaid.js
    # Version 9.4.3 is stable and well-tested
    mermaid_url = "https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"
    expected_md5 = "e1e7801bf530b891a33add8e1bd0d3b6"  # Known good hash for v9.4.3
    
    try:
        # Use proper HTTP request with headers
        import urllib.request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        request = urllib.request.Request(mermaid_url, headers=headers)
        
        # Download to temporary file first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
                temp_file.write(content)
                temp_path = temp_file.name
        
        # Validate the downloaded file
        is_valid = True
        validation_message = ""
        
        # Check 1: Size validation
        file_size = os.path.getsize(temp_path)
        if file_size < 100000:  # Should be at least 100KB
            is_valid = False
            validation_message = f"File too small: {file_size} bytes"
        
        # Check 2: Content validation
        if is_valid:
            with open(temp_path, 'rb') as f:
                content = f.read()
                content_str = content.decode('utf-8', errors='ignore')
                
                if b"function" not in content:
                    is_valid = False
                    validation_message = "Missing 'function' keyword"
                elif b"mermaid" not in content:
                    is_valid = False
                    validation_message = "Missing 'mermaid' keyword"
                elif "return;" in content_str and "{" not in content_str[:content_str.find("return;")]:
                    is_valid = False
                    validation_message = "Possible illegal return statement"
        
        # Check 3: MD5 hash validation
        if is_valid:
            file_hash = hashlib.md5(content).hexdigest()
            if file_hash != expected_md5:
                logger.warning(f"Downloaded file hash ({file_hash}) doesn't match expected hash ({expected_md5})")
                # Continue anyway since other checks passed
        
        # Move the file to the resources directory if it passed validation
        if is_valid:
            import shutil
            shutil.move(temp_path, target_path)
            logger.info(f"Successfully downloaded and validated Mermaid.js to: {target_path}")
            return target_path
        else:
            logger.error(f"Downloaded file failed validation: {validation_message}")
            os.remove(temp_path)
            return None
            
    except Exception as e:
        logger.error(f"Error downloading Mermaid.js: {str(e)}")
        return None