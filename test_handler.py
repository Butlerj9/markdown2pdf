"""
Test script for the _create_recent_file_handler method
"""

def create_handler(file_path):
    """Create a method to handle opening a specific recent file"""
    # Create a copy of the file path to avoid reference issues
    path_copy = str(file_path)
    
    def handler(checked=False):
        print(f"Opening file: {path_copy}")
    
    return handler

# Create a list of file paths
file_paths = [
    "C:/path/to/file1.md",
    "C:/path/to/file2.md",
    "C:/path/to/file3.md"
]

# Create handlers for each file path
handlers = []
for file_path in file_paths:
    handlers.append(create_handler(file_path))

# Call each handler
for i, handler in enumerate(handlers):
    print(f"Calling handler {i+1}:")
    handler()
