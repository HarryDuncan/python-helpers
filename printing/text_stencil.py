#!/usr/bin/env python3
"""
3D Text Stencil Generator

This script creates a 3D stencil by creating a plane with text texture and removing the text areas.

Requirements:
- bpy (Blender Python API)
- numpy (install with: pip install numpy)

Usage:
    python text_stencil.py
    
The script will prompt you for text, dimensions, and parameters.
"""

import bpy
import math
import sys
import numpy as np
import tempfile
import os


def get_user_input():
    """
    Prompt user for all necessary input parameters.
    
    Returns:
        dict: Dictionary containing all user inputs
    """
    print("=== 3D Text Stencil Generator ===")
    print("This will create a 3D stencil by removing text from a plane.\n")
    print("Please enter the following parameters:\n")
    
    # Get text input
    text = input("Enter the text for the stencil: ")
    if not text.strip():
        print("Text cannot be empty. Please try again.")
        return get_user_input()
    
    # Get dimensions
    while True:
        try:
            text_height = float(input("Enter height of the text (mm): "))
            if text_height > 0:
                break
            else:
                print("Text height must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            max_width = float(input("Enter maximum width of the rectangle (mm): "))
            if max_width > 0:
                break
            else:
                print("Width must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            top_margin = float(input("Enter top and bottom margins (mm) [default: 5.0]: ") or "5.0")
            if top_margin >= 0:
                break
            else:
                print("Margin must be non-negative. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            side_margin = float(input("Enter left and right margins (mm) [default: 5.0]: ") or "5.0")
            if side_margin >= 0:
                break
            else:
                print("Margin must be non-negative. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get font path
    font_path = input("Enter font file path [default: Arial]: ") or "Arial"
    
    # Get output filename
    output_filename = input("Enter output filename [default: text_stencil.stl]: ") or "text_stencil.stl"
    
    return {
        'text': text,
        'text_height': text_height,
        'max_width': max_width,
        'top_margin': top_margin,
        'side_margin': side_margin,
        'font_path': font_path,
        'output_filename': output_filename
    }


def calculate_text_layout(text, text_height, max_width, top_margin, side_margin):
    """
    Calculate the layout of text words to fit within the rectangle.
    
    Args:
        text (str): The text to layout
        text_height (float): Height of each text line
        max_width (float): Maximum width of rectangle
        top_margin (float): Top and bottom margins
        side_margin (float): Left and right margins
    
    Returns:
        tuple: (rectangle_width, rectangle_height, word_positions)
    """
    words = text.split()
    available_width = max_width - 2 * side_margin
    word_spacing = text_height * 0.3  # Space between words
    line_spacing = text_height * 0.5  # Space between lines
    
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        # Estimate word width (rough approximation)
        word_width = len(word) * text_height * 0.6
        
        if current_width + word_width <= available_width:
            current_line.append(word)
            current_width += word_width + word_spacing
        else:
            if current_line:
                lines.append(current_line)
                current_line = [word]
                current_width = word_width + word_spacing
            else:
                # Single word is too long, add it anyway
                lines.append([word])
                current_line = []
                current_width = 0
    
    if current_line:
        lines.append(current_line)
    
    # Calculate rectangle dimensions
    rectangle_width = max_width
    rectangle_height = len(lines) * text_height + (len(lines) - 1) * line_spacing + 2 * top_margin
    
    # Calculate word positions
    word_positions = []
    y_offset = top_margin
    
    for line_idx, line in enumerate(lines):
        x_offset = side_margin
        for word in line:
            word_positions.append({
                'word': word,
                'x': x_offset,
                'y': y_offset,
                'line': line_idx
            })
            # Estimate word width for positioning
            word_width = len(word) * text_height * 0.6
            x_offset += word_width + word_spacing
        
        y_offset += text_height + line_spacing
    
    return rectangle_width, rectangle_height, word_positions


def create_plane_with_texture(width, height, text, text_height, word_positions, font_path):
    """
    Create a plane mesh with high vertex density and add text as a texture.
    
    Args:
        width (float): Width of the plane
        height (float): Height of the plane
        text (str): The text to add
        text_height (float): Height of the text
        word_positions (list): List of word position dictionaries
        font_path (str): Path to the font file
    
    Returns:
        bpy.types.Object: The plane object with text texture
    """
    print(f"Creating plane mesh: {width}mm x {height}mm")
    
    # Create a plane with high vertex density
    # Calculate subdivisions based on text size for good resolution
    x_subdivisions = max(50, int(width / (text_height * 0.1)))  # At least 50 subdivisions or 1 per 0.1*text_height
    y_subdivisions = max(50, int(height / (text_height * 0.1)))
    
    print(f"Creating plane with {x_subdivisions} x {y_subdivisions} subdivisions")
    
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, height/2, 0))
    plane = bpy.context.active_object
    
    # Scale to desired dimensions
    plane.scale = (width, height, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Add subdivisions for high vertex density
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=x_subdivisions-1)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=y_subdivisions-1)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Plane created with {len(plane.data.vertices)} vertices")
    
    # Create text objects for cutting
    text_objects = []
    for word_info in word_positions:
        print(f"Creating text object for word: '{word_info['word']}'")
        
        # Create text object
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
        text_obj = bpy.context.active_object
        text_obj.data.body = word_info['word']
        
        # Set font if provided
        if font_path and font_path != "Arial":
            try:
                if font_path.endswith(('.ttf', '.otf')):
                    bpy.ops.font.open(filepath=font_path)
                    text_obj.data.font = bpy.data.fonts[os.path.basename(font_path)]
            except Exception as e:
                print(f"Warning: Could not load font {font_path}: {e}")
        
        # Set text properties
        text_obj.data.size = text_height
        text_obj.data.extrude = 2.0  # Depth for cutting
        text_obj.data.fill_mode = 'BOTH'
        
        # Convert to mesh
        bpy.ops.object.convert(target='MESH')
        
        # Position the text
        word_width = len(word_info['word']) * text_height * 0.6
        word_height = text_height
        
        x_pos = word_info['x'] + word_width / 2
        y_pos = word_info['y'] + word_height / 2
        z_pos = 1.0  # Position above the plane for cutting
        
        text_obj.location = (x_pos, y_pos, z_pos)
        
        # Clean up the text mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        text_objects.append(text_obj)
    
    # Use boolean modifiers to cut text from plane
    for i, text_obj in enumerate(text_objects):
        try:
            print(f"Cutting text '{text_obj.data.body}' from plane...")
            
            # Add boolean modifier to plane
            bool_mod = plane.modifiers.new(name=f"Boolean_{i}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = text_obj
            
            # Apply the boolean modifier
            bpy.context.view_layer.objects.active = plane
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
            
            print(f"Successfully cut text '{text_obj.data.body}' from plane")
            
        except Exception as e:
            print(f"Warning: Could not cut text '{text_obj.data.body}': {e}")
        
        # Delete the text object
        bpy.data.objects.remove(text_obj, do_unlink=True)
    
    return plane


def create_text_stencil(text, text_height, max_width, top_margin, side_margin, font_path):
    """
    Create a text stencil by removing text from a plane.
    
    Args:
        text (str): The text for the stencil
        text_height (float): Height of the text
        max_width (float): Maximum width of the rectangle
        top_margin (float): Top and bottom margins
        side_margin (float): Left and right margins
        font_path (str): Path to the font file
    
    Returns:
        bpy.types.Object: The final stencil object
    """
    print("Calculating text layout...")
    rectangle_width, rectangle_height, word_positions = calculate_text_layout(
        text, text_height, max_width, top_margin, side_margin
    )
    
    print(f"Rectangle dimensions: {rectangle_width}mm x {rectangle_height}mm")
    print(f"Number of words: {len(word_positions)}")
    
    # Clear all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create the plane with text texture
    print("Creating plane with text texture...")
    stencil_plane = create_plane_with_texture(
        rectangle_width, rectangle_height, text, text_height, word_positions, font_path
    )
    
    return stencil_plane


def save_mesh(obj, filename):
    """
    Save the mesh to a file.
    
    Args:
        obj (bpy.types.Object): The object to save
        filename (str): Output filename
    """
    try:
        # Select only the object to export
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Export as STL
        bpy.ops.export_mesh.stl(filepath=filename, use_selection=True)
        print(f"Stencil saved successfully to: {filename}")
    except Exception as e:
        print(f"Error saving mesh: {e}")
        sys.exit(1)


def main():
    try:
        # Get user input
        params = get_user_input()
        
        print(f"\nCreating text stencil:")
        print(f"Text: '{params['text']}'")
        print(f"Text height: {params['text_height']}mm")
        print(f"Max width: {params['max_width']}mm")
        print(f"Margins: {params['top_margin']}mm top/bottom, {params['side_margin']}mm left/right")
        print(f"Font: {params['font_path']}")
        print(f"Output: {params['output_filename']}\n")
        
        # Create the text stencil
        stencil_obj = create_text_stencil(
            params['text'],
            params['text_height'],
            params['max_width'],
            params['top_margin'],
            params['side_margin'],
            params['font_path']
        )
        
        # Save the stencil
        print("\nSaving stencil...")
        save_mesh(stencil_obj, params['output_filename'])
        
        print("\nText stencil created successfully!")
        print(f"File created: {params['output_filename']}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating stencil: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    