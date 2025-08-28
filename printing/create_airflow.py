#!/usr/bin/env python3
"""
Create Airflow Mesh Generator

This script creates a rectangular mesh with airflow holes for 3D printing.
The mesh is 1.5mm thick with small holes distributed across the surface.

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
    
    # Get output filename
    output_file = input("Enter output filename [default: airflow_mesh.stl]: ") or "airflow_mesh.stl"
    
    return {
        'width': width,
        'length': length,
        'thickness': thickness,
        'hole_radius': hole_radius,
        'hole_spacing': hole_spacing,
        'output_file': output_file
    }



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
        
        print(f"\nCreating airflow mesh with dimensions: {params['width']}mm x {params['length']}mm x {params['thickness']}mm")
        print(f"Hole radius: {params['hole_radius']}mm, Spacing: {params['hole_spacing']}mm")
        print(f"Output file: {params['output_file']}\n")
        
        # Create the base rectangular mesh
        print("Creating base rectangular mesh...")
        base_mesh =  mr.makeCube(mr.Vector3f(params['width'], params['length'], params['thickness']))
        
        # Add airflow holes
        print("Adding airflow holes...")
        final_mesh = add_airflow_holes(
            base_mesh, 
            thickness=params['thickness'],
            hole_radius=params['hole_radius'],
            hole_spacing=params['hole_spacing']
        )
        
        # Save the mesh
        print("Saving mesh...")
        save_mesh(final_mesh, params['output_file'])
        
        print("Airflow mesh creation completed successfully!")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating mesh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 