#!/usr/bin/env python3
"""
Create Airflow Mesh Generator

This script creates three rectangular meshes with airflow holes for 3D printing:
1. Top rectangle with airflow holes
2. Bottom rectangle with airflow holes  
3. Wall mesh (sides) with airflow holes

Requirements:
- trimesh (install with: pip install trimesh)
- meshlib (install with: pip install meshlib)
- numpy (install with: pip install numpy)

Usage:
    python create_airflow.py
    
The script will prompt you for all necessary dimensions and parameters.
"""

import sys
import numpy as np
import trimesh
import meshlib
from meshlib import mrmeshpy as mr
from meshlib import mrmeshnumpy as mrn
import tempfile
import os


def get_user_input():
    """
    Prompt user for all necessary input parameters.
    
    Returns:
        dict: Dictionary containing all user inputs
    """
    print("=== Airflow Mesh Generator ===")
    print("This will create 3 meshes: top, bottom, and walls with airflow holes.\n")
    print("Please enter the following parameters:\n")
    
    # Get dimensions
    while True:
        try:
            width = float(input("Enter width of the rectangle (mm): "))
            if width > 0:
                break
            else:
                print("Width must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            length = float(input("Enter length of the rectangle (mm): "))
            if length > 0:
                break
            else:
                print("Length must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            height = float(input("Enter height of the box (mm): "))
            if height > 0:
                break
            else:
                print("Height must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            thickness = float(input("Enter thickness of the mesh (mm) [default: 1.5]: ") or "1.5")
            if thickness > 0:
                break
            else:
                print("Thickness must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get hole parameters
    while True:
        try:
            hole_radius = float(input("Enter radius of each hole (mm) [default: 1.0]: ") or "1.0")
            if hole_radius > 0:
                break
            else:
                print("Hole radius must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    while True:
        try:
            hole_spacing = float(input("Enter spacing between holes (mm) [default: 5.0]: ") or "5.0")
            if hole_spacing > 0:
                break
            else:
                print("Hole spacing must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get output filename prefix
    output_prefix = input("Enter output filename prefix [default: airflow]: ") or "airflow"
    
    # Ask about wall mesh type
    while True:
        wall_type = input("Create walls as full box or 2 L-shaped meshes? (full/l-shaped) [default: full]: ").lower() or "full"
        if wall_type in ["full", "l-shaped", "l"]:
            break
        else:
            print("Please enter 'full' or 'l-shaped'.")
    
    return {
        'width': width,
        'length': length,
        'height': height,
        'thickness': thickness,
        'hole_radius': hole_radius,
        'hole_spacing': hole_spacing,
        'output_prefix': output_prefix,
        'wall_type': wall_type
    }


def create_top_mesh(width, length, thickness, hole_radius, hole_spacing):
    """
    Create the top rectangle mesh with airflow holes.
    
    Args:
        width (float): Width of the rectangle
        length (float): Length of the rectangle
        thickness (float): Thickness of the mesh
        hole_radius (float): Radius of each hole
        hole_spacing (float): Spacing between holes
    
    Returns:
        mr.Mesh: The top mesh with holes
    """
    print("Creating top mesh...")
    
    # Create top rectangle
    top_mesh = mr.makeCube(mr.Vector3f(width, length, thickness))
    
    # Add holes to top mesh
    top_mesh_with_holes = add_airflow_holes(top_mesh, thickness, hole_radius, hole_spacing)
    
    return top_mesh_with_holes


def create_bottom_mesh(width, length, thickness, hole_radius, hole_spacing):
    """
    Create the bottom rectangle mesh with airflow holes.
    
    Args:
        width (float): Width of the rectangle
        length (float): Length of the rectangle
        thickness (float): Thickness of the mesh
        hole_radius (float): Radius of each hole
        hole_spacing (float): Spacing between holes
    
    Returns:
        mr.Mesh: The bottom mesh with holes
    """
    print("Creating bottom mesh...")
    
    # Create bottom rectangle
    bottom_mesh = mr.makeCube(mr.Vector3f(width, length, thickness))
    
    # Add holes to bottom mesh
    bottom_mesh_with_holes = add_airflow_holes(bottom_mesh, thickness, hole_radius, hole_spacing)
    
    return bottom_mesh_with_holes


def create_wall_mesh(width, length, height, thickness, wall_type="full"):
    """
    Create the wall mesh (sides) by subtracting an inner box from an outer box.
    
    Args:
        width (float): Width of the box
        length (float): Length of the box
        height (float): Height of the box
        thickness (float): Thickness of the walls
        wall_type (str): "full" for complete box walls, "l-shaped" for 2 L-shaped pieces
    
    Returns:
        mr.Mesh or list: The wall mesh(s) (no holes)
    """
    print("Creating wall mesh...")
    
    # Create outer box (full size)
    outer_box = mr.makeCube(mr.Vector3f(width, length, height))
    
    # Create inner box with modified dimensions
    inner_width = width - 2 * thickness
    inner_length = length - 2 * thickness
    inner_height = height + 2  # Add 2mm to height
    
    inner_box = mr.makeCube(mr.Vector3f(inner_width, inner_length, inner_height))
    
    # Position the inner box so it is thickness away from all sides except top and bottom
    # The inner box should be shifted by +thickness in x and y, and by -1 in z (so it extends 1mm above and below)
    transform = mr.AffineXf3f().translation(mr.Vector3f(thickness, thickness, 0))
    
    # Apply transformation to inner box
    inner_box.transform(transform)
    
    # Subtract inner box from outer box to create walls
    walls_mesh_1 = mr.boolean(outer_box, inner_box, mr.BooleanOperation.DifferenceAB).mesh
    walls_mesh_2 = mr.boolean(outer_box, inner_box, mr.BooleanOperation.DifferenceAB).mesh
    
    # if wall_type is l-shaped, create 2 L-shaped meshes
  
    print("Creating 2 L-shaped wall meshes...")
 
    
    # 2. Create a subtraction box - width - thickness and length - thickness
   
    
    # 3. On first mesh - subtract north-east walls (offset to top-right)
    # Position the subtraction box to remove north and east walls
    ne_transform = mr.AffineXf3f().translation(mr.Vector3f(thickness, thickness, -1))
    subtraction_box_ne = mr.makeCube(mr.Vector3f(width , length , height + 2))
    subtraction_box_ne.transform(ne_transform)
    walls_mesh_1 = mr.boolean(walls_mesh_1, subtraction_box_ne, mr.BooleanOperation.DifferenceAB).mesh
    
    # 4. On second mesh - subtract south-west walls (offset to bottom-left)
    # Position the subtraction box to remove south and west walls
    sw_transform = mr.AffineXf3f().translation(mr.Vector3f(-thickness, -thickness, -1))
    subtraction_box_sw = mr.makeCube(mr.Vector3f(width , length, height + 2))
    subtraction_box_sw.transform(sw_transform)
    walls_mesh_2 = mr.boolean(walls_mesh_2, subtraction_box_sw, mr.BooleanOperation.DifferenceAB).mesh
    
    # Return the two L-shaped meshes
    return [walls_mesh_1, walls_mesh_2]
        
  





def add_airflow_holes(mesh, thickness=1.5, hole_radius=1.0, hole_spacing=5.0):
    """
    Add airflow holes to the mesh using boolean operations.
    
    Args:
        mesh (mr.Mesh): The base rectangular mesh
        thickness (float): Thickness of the mesh in mm
        hole_radius (float): Radius of each hole in mm
        hole_spacing (float): Spacing between holes in mm
    
    Returns:
        mr.Mesh: The mesh with holes
    """
    # Get mesh bounds to determine hole placement
    bbox = mesh.getBoundingBox()
    min_x, max_x = bbox.min.x, bbox.max.x
    min_y, max_y = bbox.min.y, bbox.max.y
    center_z = bbox.center().z
    
    # Create hole positions in a grid pattern
    x_positions = np.arange(min_x + hole_spacing, max_x - hole_spacing, hole_spacing)
    y_positions = np.arange(min_y + hole_spacing, max_y - hole_spacing, hole_spacing)
    
    # Create a grid of holes
    hole_positions = []
    for x in x_positions:
        for y in y_positions:
            hole_positions.append((x, y))
    
    print(f"Creating {len(hole_positions)} holes...")
    
    # Subtract each hole from the main mesh
    result_mesh = mesh
    for i, (x, y) in enumerate(hole_positions):
        # Create hole cylinder
        hole = mr.makeCylinder(hole_radius, thickness + 2.0)
        
        # Position the hole
        transform = mr.AffineXf3f().translation(mr.Vector3f(x, y, center_z - thickness/2 - 1.0))
        # Apply transformation to hole
        hole.transform(transform)
        
        # Subtract hole from main mesh using boolean operation
        try:
            operation = mr.boolean(result_mesh, hole, mr.BooleanOperation.DifferenceAB)
            if not operation.valid():
                print(operation.errorString())
                continue
            result_mesh = operation.mesh
            if i % 10 == 0:
                print(f"Processed {i+1}/{len(hole_positions)} holes...")
        except Exception as e:
            print(f"Warning: Could not create hole at position ({x}, {y}): {e}")
            continue
    
    return result_mesh


def save_mesh(mesh, filename):
    """
    Save the mesh to a file.
    
    Args:
        mesh (mr.Mesh): The mesh to save
        filename (str): Output filename
    """
    try:
        mr.saveMesh(mesh, filename)
        print(f"Mesh saved successfully to: {filename}")
    except Exception as e:
        print(f"Error saving mesh: {e}")
        sys.exit(1)


def main():
    try:
        # Get user input
        params = get_user_input()
        
        print(f"\nCreating airflow meshes with dimensions: {params['width']}mm x {params['length']}mm x {params['height']}mm")
        print(f"Thickness: {params['thickness']}mm")
        print(f"Hole radius: {params['hole_radius']}mm, Spacing: {params['hole_spacing']}mm")
        print(f"Output prefix: {params['output_prefix']}\n")
        
        # Create the three meshes
        top_mesh = create_top_mesh(
            params['width'], 
            params['length'], 
            params['thickness'],
            params['hole_radius'],
            params['hole_spacing']
        )
        
        bottom_mesh = create_bottom_mesh(
            params['width'], 
            params['length'], 
            params['thickness'],
            params['hole_radius'],
            params['hole_spacing']
        )
        
        wall_meshes = create_wall_mesh(
            params['width'],
            params['length'],
            params['height'],
            params['thickness'],
            params['wall_type']
        )
        
        # Save all meshes
        print("\nSaving meshes...")
        save_mesh(top_mesh, f"{params['output_prefix']}_top.stl")
        save_mesh(bottom_mesh, f"{params['output_prefix']}_bottom.stl")
        
        save_mesh(wall_meshes[0], f"{params['output_prefix']}_walls_l1.stl")
        save_mesh(wall_meshes[1], f"{params['output_prefix']}_walls_l2.stl")
        print(f"  - {params['output_prefix']}_walls_l1.stl (L-shaped wall piece 1)")
        print(f"  - {params['output_prefix']}_walls_l2.stl (L-shaped wall piece 2)")
        
        print("\nAll airflow meshes created successfully!")
        print(f"Files created:")
        print(f"  - {params['output_prefix']}_top.stl (top rectangle with holes)")
        print(f"  - {params['output_prefix']}_bottom.stl (bottom rectangle with holes)")
        if params['wall_type'] == "full":
            print(f"  - {params['output_prefix']}_walls.stl (full wall box)")
        else:
            print(f"  - {params['output_prefix']}_walls_l1.stl (L-shaped wall piece 1)")
            print(f"  - {params['output_prefix']}_walls_l2.stl (L-shaped wall piece 2)")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating mesh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 