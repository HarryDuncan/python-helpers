#!/usr/bin/env python3
"""
3D Text Stencil Generator

This script creates a 3D stencil by creating a subdivided plane and cutting out text shapes.

Requirements:
- bpy (Blender Python API)
- numpy (install with: pip install numpy)

Usage:
    python stencil.py
    
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
    print("This will create a 3D stencil by cutting text from a subdivided plane.\n")
    print("Please enter the following parameters:\n")
    
    # Get text input
    text = input("Enter the text for the stencil: " ) 
    if not text.strip():
        print("Text cannot be empty. Please try again.")
        return get_user_input()
    
    # Get dimensions
    while True:
        try:
            text_height = float(input("Enter height of the text (mm): ") or "10.0")
            if text_height > 0:
                break
            else:
                print("Text height must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            max_width = float(input("Enter maximum width of the plane (mm): ") or "300.0")
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
    font_path = input("Enter font file path [default: C:/Users/harry/AppData/Local/Microsoft/Windows/Fonts/Harryduncan.otf]: ") or "C:/Users/harry/AppData/Local/Microsoft/Windows/Fonts/Harryduncan.otf"
    
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


def create_3d_text(text, font_path, text_height):
    """
    Create a 3D text object using Blender.
    
    Args:
        text (str): The text to create
        font_path (str): Path to the font file
        text_height (float): Height of the text in mm
    
    Returns:
        bpy.types.Object: The text object
    """
    # Add a text object
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
    text_object = bpy.context.active_object
    text_object.data.body = text
    
    # Set font if provided
    try:
        if font_path and os.path.exists(font_path):
            print(f"Attempting to load font: {font_path}")
            print(f"Font file size: {os.path.getsize(font_path)} bytes")
            
            # First, try to open the font
            bpy.ops.font.open(filepath=font_path)
            
            # Get the font name from the path
            font_name = os.path.basename(font_path)
            print(f"Font name: {font_name}")
            
            # Check if the font was loaded successfully
            if font_name in bpy.data.fonts:
                text_object.data.font = bpy.data.fonts[font_name]
                print(f"Successfully loaded font: {font_name}")
            else:
                print(f"Font '{font_name}' not found in bpy.data.fonts")
                print(f"Available fonts: {list(bpy.data.fonts.keys())}")
                
                # Try alternative approach - look for any font with similar name
                for font_key in bpy.data.fonts.keys():
                    if 'harry' in font_key.lower() or 'duncan' in font_key.lower():
                        text_object.data.font = bpy.data.fonts[font_key]
                        print(f"Found alternative font: {font_key}")
                        break
        else:
            print(f"Font path does not exist: {font_path}")
    except Exception as e:
        print(f"Error loading font {font_path}: {e}")
        print("Continuing with default font...")
    
    # Set text properties for better boolean operations
    text_object.data.size = text_height
    text_object.data.extrude = 2.0  # Fixed depth that will reliably cut through the plane
    text_object.data.fill_mode = 'BOTH'  # Fill both front and back
    text_object.data.bevel_depth = 0.0  # No bevel to avoid complex geometry
    text_object.data.offset = 0.0  # No offset
    text_object.data.shear = 0.0  # No shear
    
    print(f"Text object '{text}' properties set - size: {text_height}, extrude: 2.0")
    
    # Convert to mesh
    bpy.ops.object.convert(target='MESH')
    print(f"Text object '{text}' converted to mesh")

    # Calculate the center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Move the object to the origin
    text_object.location = (0, 0, 0)
    
    # Apply rotations to ensure proper orientation - text should lie flat on the plane
    text_object.rotation_euler = (0, 0, 0)  # No rotation - text should be flat
    
    # Apply the rotation to make it permanent
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Clean up the mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.remove_doubles(threshold=0.001)
   
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Debug: Check if the mesh has vertices
    mesh = text_object.data
    print(f"Text object '{text}' created with {len(mesh.vertices)} vertices, {len(mesh.polygons)} faces")
    
    # Check if mesh is valid for boolean operations
    if len(mesh.vertices) == 0:
        print(f"ERROR: Text object '{text}' has no vertices!")
        return None
    elif len(mesh.polygons) == 0:
        print(f"ERROR: Text object '{text}' has no faces!")
        return None
    else:
        print(f"Text object '{text}' is valid for boolean operations")
    
    return text_object


def calculate_text_layout(text, text_height, max_width, top_margin, side_margin):
    """
    Calculate the layout of text words to fit within the plane.
    
    Args:
        text (str): The text to layout
        text_height (float): Height of each text line
        max_width (float): Maximum width of plane
        top_margin (float): Top and bottom margins
        side_margin (float): Left and right margins
    
    Returns:
        tuple: (plane_width, plane_height, word_positions)
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
    
    # Calculate plane dimensions
    plane_width = max_width
    plane_height = len(lines) * text_height + (len(lines) - 1) * line_spacing + 2 * top_margin
    
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
    
    return plane_width, plane_height, word_positions


def create_subdivided_plane(width, height, thickness=1.0):
    """
    Create a subdivided plane mesh using Blender.
    
    Args:
        width (float): Width of the plane
        height (float): Height of the plane
        thickness (float): Thickness of the plane
    
    Returns:
        bpy.types.Object: The subdivided plane object
    """
    print(f"Creating subdivided plane: {width}mm x {height}mm")
    
    # Calculate subdivisions (max 50 as requested)
    x_subdivisions = min(50, max(10, int(width / 10)))  # At least 10, max 50
    y_subdivisions = min(50, max(10, int(height / 10)))
    
    print(f"Creating plane with {x_subdivisions} x {y_subdivisions} subdivisions")
    
    # Create a plane
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
    
    return plane


def create_word_mesh(word, font_path, text_height):
    """
    Create a 3D mesh for a single word using Blender.

    Args:
        word (str): The word to create
        font_path (str): Path to the font file
        text_height (float): Height of the text

    Returns:
        bpy.types.Object: The word mesh object
    """
    # Create text object in Blender
    text_obj = create_3d_text(word, font_path, text_height)
    
    # Save the text mesh as an OBJ file for inspection
    if text_obj is not None:
        try:
            safe_word = "".join(c if c.isalnum() else "_" for c in word)
            obj_filename = f"debug_text_mesh_{safe_word}.obj"
            obj_filepath = os.path.join("C:/Users/harry/Projects/python-helpers/printing", obj_filename)
            
            bpy.ops.object.select_all(action='DESELECT')
            text_obj.select_set(True)
            bpy.context.view_layer.objects.active = text_obj
            bpy.ops.export_scene.obj(filepath=obj_filepath, use_selection=True)
            print(f"Saved debug text mesh '{word}' to: {obj_filepath}")
        except Exception as e:
            print(f"Warning: Could not save debug mesh for '{word}': {e}")
    
    return text_obj


def create_text_stencil(text, text_height, max_width, top_margin, side_margin, font_path):
    """
    Create a text stencil by cutting text from a subdivided plane.
    
    Args:
        text (str): The text for the stencil
        text_height (float): Height of the text
        max_width (float): Maximum width of the plane
        top_margin (float): Top and bottom margins
        side_margin (float): Left and right margins
        font_path (str): Path to the font file
    
    Returns:
        bpy.types.Object: The final stencil object
    """
    print("Calculating text layout...")
    plane_width, plane_height, word_positions = calculate_text_layout(
        text, text_height, max_width, top_margin, side_margin
    )
    
    print(f"Plane dimensions: {plane_width}mm x {plane_height}mm")
    print(f"Number of words: {len(word_positions)}")
    
    # Clear all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create the base subdivided plane
    print("Creating base subdivided plane...")
    base_plane = create_subdivided_plane(plane_width, plane_height)
    
    # Create and position word meshes
    print("Creating word meshes...")
    
    for i, word_info in enumerate(word_positions):
        print(f"Processing word {i+1}/{len(word_positions)}: '{word_info['word']}'")
        
        # Create word mesh
        word_mesh = create_word_mesh(word_info['word'], font_path, text_height)
        
        # Check if word mesh was created successfully
        if word_mesh is None:
            print(f"ERROR: Failed to create word mesh for '{word_info['word']}' - skipping")
            continue
        
        # Position the word mesh
        try:
            # Get word mesh bounds properly
            bpy.context.view_layer.objects.active = word_mesh
            bpy.ops.object.select_all(action='DESELECT')
            word_mesh.select_set(True)
            
            # Calculate bounds from the mesh data
            mesh = word_mesh.data
            if len(mesh.vertices) > 0:
                # Get all vertex coordinates
                verts = [word_mesh.matrix_world @ v.co for v in mesh.vertices]
                x_coords = [v.x for v in verts]
                y_coords = [v.y for v in verts]
                z_coords = [v.z for v in verts]
                
                word_width = max(x_coords) - min(x_coords)
                word_height = max(y_coords) - min(y_coords)
                word_depth = max(z_coords) - min(z_coords)
                
                print(f"Word '{word_info['word']}' dimensions: {word_width:.2f} x {word_height:.2f} x {word_depth:.2f}")
            else:
                # Fallback to estimated dimensions
                word_width = len(word_info['word']) * text_height * 0.6
                word_height = text_height
                print(f"Using estimated dimensions for '{word_info['word']}': {word_width:.2f} x {word_height:.2f}")
            
            # Position the text so it's centered at the specified coordinates
            x_pos = word_info['x'] + word_width / 2
            y_pos = word_info['y'] + word_height / 2
            z_pos = 1.0  # Position above the plane for cutting
            
            print(f"Positioning at: ({x_pos:.2f}, {y_pos:.2f}, {z_pos:.2f})")
            
            word_mesh.location = (x_pos, y_pos, z_pos)
            
        except Exception as e:
            print(f"Could not calculate word bounds, using fallback positioning: {e}")
            word_mesh.location = (word_info['x'], word_info['y'], 1.0)
        
        # Use boolean modifier to subtract word from plane
        try:
            print(f"Attempting boolean subtraction for word '{word_info['word']}' at position ({word_info['x']}, {word_info['y']})")
            
            # Add boolean modifier to plane
            bool_mod = base_plane.modifiers.new(name=f"Boolean_{i}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = word_mesh
            
            # Apply the boolean modifier
            bpy.context.view_layer.objects.active = base_plane
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
            
            print(f"Successfully subtracted word '{word_info['word']}'")
            
        except Exception as e:
            print(f"Warning: Could not subtract word '{word_info['word']}': {e}")
            print(f"Creating simple rectangular hole as fallback for word '{word_info['word']}'")
            
            # Create a simple rectangular hole as fallback
            try:
                # Estimate word dimensions
                word_width = len(word_info['word']) * text_height * 0.6
                word_height = text_height
                
                # Create a simple rectangular cutting mesh
                bpy.ops.mesh.primitive_cube_add(size=1, location=(word_info['x'] + word_width/2, word_info['y'] + word_height/2, 1.0))
                cutting_mesh = bpy.context.active_object
                cutting_mesh.scale = (word_width, word_height, 2.0)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
                # Try boolean operation with simple mesh
                bool_mod = base_plane.modifiers.new(name=f"Boolean_Fallback_{i}", type='BOOLEAN')
                bool_mod.operation = 'DIFFERENCE'
                bool_mod.object = cutting_mesh
                
                bpy.context.view_layer.objects.active = base_plane
                bpy.ops.object.modifier_apply(modifier=bool_mod.name)
                
                # Delete the cutting mesh
                bpy.data.objects.remove(cutting_mesh, do_unlink=True)
                
                print(f"Successfully created rectangular hole for word '{word_info['word']}'")

            except Exception as fallback_error:
                print(f"Fallback approach also failed for word '{word_info['word']}': {fallback_error}")
        
        # Delete the word mesh object (it's no longer needed)
        bpy.data.objects.remove(word_mesh, do_unlink=True)
    
    return base_plane


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
      
        font_path = "C:/Users/harry/AppData/Local/Microsoft/Windows/Fonts/Harryduncan.otf"
        
        # Create the text stencil
        stencil_obj = create_text_stencil(
            params['text'],
            params['text_height'],
            params['max_width'],
            params['top_margin'],
            params['side_margin'],
            font_path
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
    