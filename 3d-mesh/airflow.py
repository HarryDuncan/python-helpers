#!/usr/bin/env python3
"""
Airflow Mesh Generator
Creates a 3D printable rectangular mesh with holes for airflow.
"""

import pymeshlab as ml
import trimesh
import numpy as np
import os
import tempfile

def create_airflow_mesh(width, length, thickness=1.5, hole_diameter=2.0, hole_spacing=5.0):
    """
    Create a rectangular mesh with holes for airflow using trimesh for creation and pymeshlab for boolean operations.
    
    Args:
        width (float): Width of the rectangle in mm
        length (float): Length of the rectangle in mm
        thickness (float): Thickness of the mesh in mm (default: 1.5)
        hole_diameter (float): Diameter of each hole in mm (default: 2.0)
        hole_spacing (float): Spacing between hole centers in mm (default: 5.0)
    
    Returns:
        pymeshlab.MeshSet: The generated mesh
    """
    
    print("Creating base rectangular box with trimesh...")
    try:
        # Create base box using trimesh
        base_mesh = trimesh.creation.box(extents=[width, length, thickness])
        print(f"✓ Base box created successfully with trimesh")
    except Exception as e:
        print(f"✗ Error creating base box: {e}")
        raise
    
    print("Calculating hole positions...")
    try:
        # Calculate hole positions
        # Start from a margin to avoid holes at the very edge
        margin = hole_spacing
        x_positions = np.arange(margin, width - margin, hole_spacing)
        y_positions = np.arange(margin, length - margin, hole_spacing)
        
        # Create a grid of hole positions
        hole_positions = []
        
        for x in x_positions:
            for y in y_positions:
                # Center the holes on the rectangle
                hole_positions.append([x - width/2, y - length/2, 0])
        
        total_holes = len(hole_positions)
        print(f"✓ Calculated {total_holes} hole positions")
    except Exception as e:
        print(f"✗ Error calculating hole positions: {e}")
        raise
    
    print("Loading base mesh into pymeshlab...")
    try:
        # Create a new MeshSet
        ms = ml.MeshSet()
        
        # Save base mesh to temporary file and load into pymeshlab
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp_file:
            base_mesh.export(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Load the saved file into pymeshlab (after the file is closed)
        ms.load_new_mesh(tmp_file_path)
        os.unlink(tmp_file_path)  # Clean up temp file
        
        print(f"✓ Base mesh loaded into pymeshlab successfully")
    except Exception as e:
        print(f"✗ Error loading base mesh into pymeshlab: {e}")
        raise
    
    print("Creating and subtracting holes one by one...")
    try:
        # Process each hole individually
        for i, pos in enumerate(hole_positions, 1):
            try:
                # Create cylinder using trimesh
                cylinder_mesh = trimesh.creation.cylinder(
                    radius=hole_diameter/2,
                    height=thickness + 2,  # Make it slightly taller to ensure it goes through
                    transform=trimesh.transformations.translation_matrix([pos[0], pos[1], 0])
                )
                
                # Save cylinder to temporary file and load into pymeshlab
                with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp_file:
                    cylinder_mesh.export(tmp_file.name)
                    tmp_file_path = tmp_file.name
                
                # Load the saved file into pymeshlab (after the file is closed)
                ms.load_new_mesh(tmp_file_path)
                os.unlink(tmp_file_path)  # Clean up temp file
                
                # Get the cylinder mesh (it's the last one added)
                cylinder_id = ms.number_meshes() - 1
                
                # Verify cylinder was created successfully
                if ms.mesh(cylinder_id).vertex_number() == 0:
                    print(f"✗ Failed to create cylinder for hole {i}")
                    ms.delete_mesh(cylinder_id)
                    continue
                print(f"✓ Cylinder {i} created successfully with {ms.mesh(cylinder_id).vertex_number()} vertices")
                
                # Subtract this cylinder from the base mesh
                ms.generate_boolean_intersection()
                
                # Check if the subtraction was successful
                if ms.mesh(0).vertex_number() == 0:
                    print(f"⚠ Boolean subtraction failed for hole {i}, skipping...")
                    # Recreate the base box if subtraction failed
                    ms.clear()
                    with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp_file:
                        base_mesh.export(tmp_file.name)
                        ms.load_new_mesh(tmp_file.name)
                        os.unlink(tmp_file.name)
                    continue
                
                if i % 10 == 0 or i == total_holes:  # Show progress every 10 holes
                    print(f"  Processed {i}/{total_holes} holes...")
                    
            except Exception as e:
                print(f"✗ Error processing hole {i}: {e}")
                continue
        
        print(f"✓ Successfully processed {total_holes} holes")
    except Exception as e:
        print(f"✗ Error in hole processing: {e}")
        print("⚠ Falling back to base box without holes")
        # Recreate the base box
        ms.clear()
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp_file:
            base_mesh.export(tmp_file.name)
            ms.load_new_mesh(tmp_file.name)
            os.unlink(tmp_file.name)
    
    # Ensure the mesh is valid
    if ms.number_meshes() == 0 or ms.mesh(0).vertex_number() == 0:
        print("⚠ Generated mesh is empty, using base box")
        ms.clear()
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as tmp_file:
            base_mesh.export(tmp_file.name)
            ms.load_new_mesh(tmp_file.name)
            os.unlink(tmp_file.name)
    
    # Fix mesh if needed
    try:
        print("⚠ Fixing mesh validity...")
        ms.meshing_remove_duplicate_vertices()
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_null_faces()
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_repair_non_manifold_vertices()
    except Exception as cleanup_error:
        print(f"⚠ Basic cleanup failed: {cleanup_error}")
    
    return ms

def save_mesh(mesh_set, filename, format='stl'):
    """
    Save the mesh to a file.
    
    Args:
        mesh_set (pymeshlab.MeshSet): The mesh to save
        filename (str): Output filename
        format (str): File format ('stl', 'obj', 'ply')
    """
    print(f"Saving mesh to {filename}...")
    try:
        # Ensure mesh is valid before saving
        try:
            print("⚠ Fixing mesh before saving...")
            mesh_set.meshing_remove_duplicate_vertices()
            mesh_set.meshing_remove_duplicate_faces()
            mesh_set.meshing_remove_null_faces()
            mesh_set.meshing_repair_non_manifold_edges()
            mesh_set.meshing_repair_non_manifold_vertices()
        except Exception as cleanup_error:
            print(f"⚠ Basic cleanup failed: {cleanup_error}")
        
        if format.lower() == 'stl':
            mesh_set.save_current_mesh(filename)
        elif format.lower() == 'obj':
            mesh_set.save_current_mesh(filename)
        elif format.lower() == 'ply':
            mesh_set.save_current_mesh(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
        print(f"✓ Mesh saved successfully")
    except Exception as e:
        print(f"✗ Error saving mesh: {e}")
        raise

def get_user_input():
    """
    Prompt user for mesh dimensions and parameters.
    
    Returns:
        dict: Dictionary containing all user inputs
    """
    print("Airflow Mesh Generator")
    print("=" * 30)
    
    # Get basic dimensions
    width = float(input("Enter width (mm): "))
    length = float(input("Enter length (mm): "))
    
    # Get optional parameters with defaults
    print("\nOptional parameters (press Enter for defaults):")
    thickness = input("Enter thickness (mm) [default: 1.5]: ")
    thickness = float(thickness) if thickness.strip() else 1.5
    
    hole_diameter = input("Enter hole diameter (mm) [default: 2.0]: ")
    hole_diameter = float(hole_diameter) if hole_diameter.strip() else 2.0
    
    hole_spacing = input("Enter hole spacing (mm) [default: 5.0]: ")
    hole_spacing = float(hole_spacing) if hole_spacing.strip() else 5.0
    
    # Get output settings
    print("\nOutput settings:")
    output_file = input("Enter output filename [default: airflow_mesh.stl]: ")
    output_file = output_file if output_file.strip() else "airflow_mesh.stl"
    
    format_choice = input("Enter output format (stl/obj/ply) [default: stl]: ")
    format_choice = format_choice.lower() if format_choice.strip() else "stl"
    
    return {
        'width': width,
        'length': length,
        'thickness': thickness,
        'hole_diameter': hole_diameter,
        'hole_spacing': hole_spacing,
        'output_file': output_file,
        'format': format_choice
    }

def main():
    try:
        # Get user input
        params = get_user_input()
        
        print(f"\nGenerating airflow mesh...")
        print(f"Dimensions: {params['width']}mm x {params['length']}mm x {params['thickness']}mm")
        print(f"Hole diameter: {params['hole_diameter']}mm")
        print(f"Hole spacing: {params['hole_spacing']}mm")
        
        # Create the mesh
        mesh = create_airflow_mesh(
            width=params['width'],
            length=params['length'],
            thickness=params['thickness'],
            hole_diameter=params['hole_diameter'],
            hole_spacing=params['hole_spacing']
        )
        
        # Save the mesh
        output_file = params['output_file']
        if not output_file.endswith(f'.{params["format"]}'):
            output_file += f'.{params["format"]}'
        
        save_mesh(mesh, output_file, params['format'])
        print(f"Mesh saved to: {output_file}")
        
        # Print mesh statistics
        print(f"\nMesh statistics:")
        print(f"Vertices: {len(mesh.vertices)}")
        print(f"Faces: {len(mesh.faces)}")
        print(f"Volume: {mesh.volume:.2f} mm³")
        print(f"Surface area: {mesh.area:.2f} mm²")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("Mesh generation failed. Please check your input parameters and try again.")

if __name__ == "__main__":
    main()