#!/usr/bin/env python3
"""
Content Processor Registry
-------------------------
Registry for all content processors in the Markdown to PDF converter.
"""

from typing import Dict, List, Type, Optional, Any
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class ProcessorRegistry:
    """Registry for all content processors"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ProcessorRegistry, cls).__new__(cls)
            cls._instance._processors = {}
            cls._instance._processor_instances = {}
        return cls._instance
    
    def register_processor(self, processor_class: Type[ContentProcessor], priority: int = 100):
        """
        Register a content processor
        
        Args:
            processor_class: The processor class to register
            priority: Priority of the processor (lower values = higher priority)
        """
        processor_name = processor_class.__name__
        logger.debug(f"Registering processor: {processor_name} with priority {priority}")
        self._processors[processor_name] = {
            'class': processor_class,
            'priority': priority
        }
    
    def get_processor(self, processor_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[ContentProcessor]:
        """
        Get a processor instance by name
        
        Args:
            processor_name: Name of the processor
            config: Optional configuration for the processor
            
        Returns:
            Processor instance or None if not found
        """
        if processor_name not in self._processors:
            logger.warning(f"Processor not found: {processor_name}")
            return None
        
        # Create a new instance if it doesn't exist or if config is provided
        if processor_name not in self._processor_instances or config is not None:
            processor_class = self._processors[processor_name]['class']
            self._processor_instances[processor_name] = processor_class(config)
        
        return self._processor_instances[processor_name]
    
    def get_all_processors(self, config: Optional[Dict[str, Any]] = None) -> List[ContentProcessor]:
        """
        Get all registered processors, sorted by priority
        
        Args:
            config: Optional configuration for the processors
            
        Returns:
            List of processor instances
        """
        # Sort processors by priority
        sorted_processors = sorted(
            self._processors.items(),
            key=lambda x: x[1]['priority']
        )
        
        # Create instances
        processor_instances = []
        for processor_name, processor_info in sorted_processors:
            processor_class = processor_info['class']
            processor_instances.append(processor_class(config))
        
        return processor_instances
    
    def process_content(self, content: str, format_type: str = 'preview') -> str:
        """
        Process content using all registered processors
        
        Args:
            content: The content to process
            format_type: 'preview' or export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content
        """
        processors = self.get_all_processors()
        processed_content = content
        
        # First, detect all content blocks
        content_blocks = []
        for processor in processors:
            detected_blocks = processor.detect(processed_content)
            for start, end, metadata in detected_blocks:
                content_blocks.append({
                    'start': start,
                    'end': end,
                    'processor': processor,
                    'metadata': metadata
                })
        
        # Sort blocks by start position (in reverse order to avoid index changes)
        content_blocks.sort(key=lambda x: x['start'], reverse=True)
        
        # Process each block
        for block in content_blocks:
            processor = block['processor']
            start = block['start']
            end = block['end']
            metadata = block['metadata']
            
            # Extract the block content
            block_content = processed_content[start:end]
            
            # Process the block
            if format_type == 'preview':
                processed_block = processor.process_for_preview(block_content, metadata)
            else:
                processed_block = processor.process_for_export(block_content, metadata, format_type)
            
            # Replace the block in the content
            processed_content = processed_content[:start] + processed_block + processed_content[end:]
        
        return processed_content
    
    def get_required_scripts(self) -> List[str]:
        """
        Get all required JavaScript scripts
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        scripts = []
        for processor in self.get_all_processors():
            scripts.extend(processor.get_required_scripts())
        return scripts
    
    def get_required_styles(self) -> List[str]:
        """
        Get all required CSS styles
        
        Returns:
            List of CSS style URLs or inline styles
        """
        styles = []
        for processor in self.get_all_processors():
            styles.extend(processor.get_required_styles())
        return styles
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if all required dependencies are available
        
        Returns:
            Dictionary mapping processor names to dependency status
        """
        dependency_status = {}
        for processor_name, processor_info in self._processors.items():
            processor = self.get_processor(processor_name)
            dependency_status[processor_name] = processor.check_dependencies()
        return dependency_status
