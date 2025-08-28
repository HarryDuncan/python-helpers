#!/usr/bin/env python3
"""
Print Tile Mesh Generator

This script creates a simple rectangular mesh for 3D printing.
The mesh is a basic rectangle with specified width, length, and height.

Requirements:
- trimesh (install with: pip install trimesh)
- meshlib (install with: pip install meshlib)
- numpy (install with: pip install numpy)

Usage:
    python print_tile.py
    
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
    print("=== Print Tile Mesh Generator ===")
    print("This will create a simple rectangular mesh for 3D printing.\n")
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
            height = float(input("Enter height of the rectangle (mm): "))
            if height > 0:
                break
            else:
                print("Height must be positive. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get output filename
    output_filename = input("Enter output filename [default: print_tile.stl]: ") or "print_tile.stl"
    
    return {
        'width': width,
        'length': length,
        'height': height,
        'output_filename': output_filename
    }


def create_rectangle_mesh(width, length, height):
    """
    Create a simple rectangular mesh.
    
    Args:
        width (float): Width of the rectangle
        length (float): Length of the rectangle
        height (float): Height of the rectangle
    
    Returns:
        mr.Mesh: The rectangular mesh
    """
    print("Creating rectangular mesh...")
    
    # Create rectangle using makeCube with specified dimensions
    rectangle_mesh = mr.makeCube(mr.Vector3f(width, length, height))
    
    return rectangle_mesh


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
        
        print(f"\nCreating rectangular mesh with dimensions: {params['width']}mm x {params['length']}mm x {params['height']}mm")
        print(f"Output file: {params['output_filename']}\n")
        
        # Create the rectangular mesh
        rectangle_mesh = create_rectangle_mesh(
            params['width'], 
            params['length'], 
            params['height']
        )
        
        # Save the mesh
        print("\nSaving mesh...")
        save_mesh(rectangle_mesh, params['output_filename'])
        
        print("\nRectangular mesh created successfully!")
        print(f"File created: {params['output_filename']}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating mesh: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
