#!/usr/bin/env python3
"""
Content Processors Package
------------------------
Package for content processors in the Markdown to PDF converter.
"""

from content_processors.processor_registry import ProcessorRegistry
from content_processors.base_processor import ContentProcessor
from content_processors.mermaid_processor import MermaidContentProcessor
from content_processors.math_processor import MathContentProcessor
from content_processors.image_processor import ImageContentProcessor
from content_processors.code_processor import CodeBlockProcessor
from content_processors.media_processor import MediaContentProcessor
from content_processors.visualization_processor import VisualizationProcessor
from content_processors.enhanced_element_processor import EnhancedElementProcessor

# Register all processors
registry = ProcessorRegistry()
registry.register_processor(EnhancedElementProcessor, priority=5)  # Highest priority for enhanced elements
registry.register_processor(MermaidContentProcessor, priority=10)
registry.register_processor(MathContentProcessor, priority=20)
registry.register_processor(ImageContentProcessor, priority=30)
registry.register_processor(CodeBlockProcessor, priority=40)
registry.register_processor(MediaContentProcessor, priority=50)
registry.register_processor(VisualizationProcessor, priority=60)

# Export the registry
__all__ = ['registry', 'ContentProcessor', 'ProcessorRegistry']
