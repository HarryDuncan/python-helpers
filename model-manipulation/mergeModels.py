import open3d as o3d

def merge_obj_files(file_prefix, num_files):
    # Initialize lists to store vertices, normals, and faces
    vertices = []
    normals = []
    faces = []
    folder_root = "C:/Users/harry/Projects/python-helpers/3d-mesh/files-to-merge/"
    # Iterate through each file
    for i in range(num_files):
        current_file_path = f"{folder_root}{file_prefix}-{i}.obj"
        
        # Read the current file
        with open(current_file_path, 'r') as file:
            lines = file.readlines()

        # Extract vertices, normals, and faces
        for line in lines:
            if line.startswith('v '):
                vertices.append(line.strip())
            elif line.startswith('vn '):
                normals.append(line.strip())
            elif line.startswith('f '):
                faces.append(line.strip())

    # Combine all data into a single list
    merged_data = vertices + normals + faces

    # Save the merged data to a new OBJ file
    output_filename = f"{file_prefix}-merged.obj"
    with open(output_filename, 'w') as output_file:
        output_file.write('\n'.join(merged_data))

    print(f"Merged file saved to {output_filename}")

def save_merged_obj(merged_mesh, output_filename):
    # Save the merged mesh to a new OBJ file
    o3d.io.write_triangle_mesh(output_filename, merged_mesh)

if __name__ == "__main__":


    file_prefix = "lotus"
    num_files = 3

    merged_mesh = merge_obj_files(file_prefix, num_files)


