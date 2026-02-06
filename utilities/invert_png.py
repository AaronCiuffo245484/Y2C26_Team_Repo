#!/usr/bin/env python3
"""
Invert PNG images: convert to grayscale and invert colors (dark->light, light->dark)
Recursively processes subdirectories up to depth 4.
Usage: python invert_images.py <input_dir> <output_dir>
"""

import sys
from pathlib import Path
from PIL import Image, ImageOps

def get_depth(path, root):
    """Calculate depth of path relative to root"""
    try:
        relative = path.relative_to(root)
        return len(relative.parts)
    except ValueError:
        return 0

def invert_images(input_dir, output_dir, max_depth=4):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all PNG files up to max_depth
    png_files = []
    for png_file in input_path.rglob('*.png'):
        depth = get_depth(png_file.parent, input_path)
        if depth <= max_depth:
            png_files.append(png_file)
    
    if not png_files:
        print(f"No PNG files found in '{input_dir}' (max depth: {max_depth})")
        sys.exit(1)
    
    print(f"Found {len(png_files)} PNG files (max depth: {max_depth})")
    print(f"Output directory: {output_path}")
    
    for img_path in png_files:
        # Get relative path from input directory
        relative_path = img_path.relative_to(input_path)
        
        # Create output subdirectory structure
        output_subdir = output_path / relative_path.parent
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        # Prepend inv_ to filename
        output_filename = f"inv_{img_path.name}"
        output_file = output_subdir / output_filename
        
        # Process image
        img = Image.open(img_path).convert('L')
        inverted = ImageOps.invert(img)
        inverted.save(output_file)
        
        print(f"Processed: {relative_path} -> {relative_path.parent / output_filename}")
    
    print(f"Done. {len(png_files)} images inverted and saved to '{output_dir}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python invert_images.py <input_dir> <output_dir>")
        sys.exit(1)
    
    invert_images(sys.argv[1], sys.argv[2])
