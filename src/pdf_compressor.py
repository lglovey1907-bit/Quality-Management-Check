"""
PDF Compression Utility
Automatically compresses PDFs to reduce file size for upload
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import PyPDF2
from io import BytesIO
from PIL import Image
import tempfile


class PDFCompressor:
    """
    Compresses PDF files to reduce size while maintaining readability
    """
    
    def __init__(self, target_size_mb: float = 20.0):
        """
        Initialize PDF compressor
        
        Args:
            target_size_mb: Target file size in MB (default: 20MB)
        """
        self.target_size_mb = target_size_mb
        self.target_size_bytes = int(target_size_mb * 1024 * 1024)
    
    def get_file_size_mb(self, file_obj) -> float:
        """Get file size in MB"""
        if hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
            current_pos = file_obj.tell()
            file_obj.seek(0, 2)  # Seek to end
            size = file_obj.tell()
            file_obj.seek(current_pos)  # Restore position
            return size / (1024 * 1024)
        return 0.0
    
    def compress_pdf(self, input_file, output_file=None, quality: str = 'medium') -> Tuple[str, float, float]:
        """
        Compress PDF file
        
        Args:
            input_file: Input PDF file object or path
            output_file: Output path (optional, creates temp file if None)
            quality: Compression quality - 'low', 'medium', 'high' (default: medium)
            
        Returns:
            Tuple of (output_path, original_size_mb, compressed_size_mb)
        """
        # Determine quality settings
        quality_settings = {
            'low': {'image_quality': 30, 'remove_duplication': True},
            'medium': {'image_quality': 50, 'remove_duplication': True},
            'high': {'image_quality': 70, 'remove_duplication': False}
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        # Handle file input
        if isinstance(input_file, str):
            with open(input_file, 'rb') as f:
                input_data = f.read()
            original_size = len(input_data) / (1024 * 1024)
            input_stream = BytesIO(input_data)
        else:
            # It's a file-like object
            input_file.seek(0)
            input_data = input_file.read()
            original_size = len(input_data) / (1024 * 1024)
            input_stream = BytesIO(input_data)
        
        # Create output file if not specified
        if output_file is None:
            temp_fd, output_file = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
        
        try:
            # Read PDF
            reader = PyPDF2.PdfReader(input_stream)
            writer = PyPDF2.PdfWriter()
            
            # Copy pages with compression
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Compress content streams
                if settings['remove_duplication']:
                    page.compress_content_streams()
                
                writer.add_page(page)
            
            # Write compressed PDF
            with open(output_file, 'wb') as output_stream:
                writer.write(output_stream)
            
            # Check compressed size
            compressed_size = os.path.getsize(output_file) / (1024 * 1024)
            
            return output_file, original_size, compressed_size
            
        except Exception as e:
            # If compression fails, save original
            with open(output_file, 'wb') as f:
                f.write(input_data)
            return output_file, original_size, original_size
    
    def smart_compress(self, input_file, max_attempts: int = 3) -> Tuple[str, float, float, str]:
        """
        Intelligently compress PDF to target size
        
        Args:
            input_file: Input PDF file object or path
            max_attempts: Maximum compression attempts with different quality levels
            
        Returns:
            Tuple of (output_path, original_size_mb, compressed_size_mb, quality_used)
        """
        # Get original size
        if isinstance(input_file, str):
            original_size = os.path.getsize(input_file) / (1024 * 1024)
        else:
            input_file.seek(0)
            data = input_file.read()
            original_size = len(data) / (1024 * 1024)
            input_file.seek(0)
        
        # If already under target, return as-is
        if original_size <= self.target_size_mb:
            # Save to temp file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            
            if isinstance(input_file, str):
                with open(input_file, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        f_out.write(f_in.read())
            else:
                input_file.seek(0)
                with open(temp_path, 'wb') as f_out:
                    f_out.write(input_file.read())
                input_file.seek(0)
            
            return temp_path, original_size, original_size, 'none'
        
        # Try different compression levels
        quality_levels = ['high', 'medium', 'low']
        
        for quality in quality_levels:
            output_path, orig_size, comp_size = self.compress_pdf(
                input_file, 
                quality=quality
            )
            
            if comp_size <= self.target_size_mb:
                return output_path, orig_size, comp_size, quality
            
            # Reset file pointer for next attempt
            if hasattr(input_file, 'seek'):
                input_file.seek(0)
        
        # Return best attempt (lowest quality)
        return output_path, orig_size, comp_size, 'low'


def compress_pdf_for_upload(uploaded_file, target_mb: float = 20.0) -> Tuple[str, dict]:
    """
    Convenience function to compress uploaded PDF files
    
    Args:
        uploaded_file: Streamlit uploaded file object
        target_mb: Target size in MB
        
    Returns:
        Tuple of (temp_file_path, compression_info_dict)
    """
    compressor = PDFCompressor(target_size_mb=target_mb)
    
    # Check original size
    uploaded_file.seek(0, 2)
    original_size_mb = uploaded_file.tell() / (1024 * 1024)
    uploaded_file.seek(0)
    
    # Compress
    output_path, orig_size, comp_size, quality = compressor.smart_compress(uploaded_file)
    
    compression_info = {
        'original_size_mb': orig_size,
        'compressed_size_mb': comp_size,
        'compression_ratio': (orig_size - comp_size) / orig_size * 100 if orig_size > comp_size else 0,
        'quality_level': quality,
        'was_compressed': comp_size < orig_size,
        'temp_path': output_path
    }
    
    return output_path, compression_info


def format_size(size_mb: float) -> str:
    """Format file size for display"""
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    return f"{size_mb:.1f} MB"
