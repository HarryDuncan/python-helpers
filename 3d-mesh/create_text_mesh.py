import bpy
import math


def create_3d_text(text, font_path, extrusion):
    # Add a text object
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
    text_object = bpy.context.active_object
    text_object.data.body = text

    # Set font
    if font_path.endswith(('.ttf', '.otf')):
        bpy.ops.font.open(filepath=font_path)
    else:
        bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')

    text_object.data.font = bpy.data.fonts.load(font_path)

    # Set extrusion
    text_object.data.extrude = extrusion
    text_object.rotation_euler = (0, 0, 0)

    # Convert to mesh
    bpy.ops.object.convert(target='MESH')

    # Calculate the center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Move the object to the origin
    text_object.location = (0, 0, 0)

    return text_object

def export_obj(obj, output_path):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='MESH', keep_original=False)

    # Remove normals if include_normals is set to False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(True)
  
    bpy.ops.wm.obj_export(filepath=output_path,  export_selected_objects=True)

    print(f"OBJ file exported to: {output_path}")

def main(strings, font_path, extrusion):
    for i, text in enumerate(strings):
        bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
        text_obj = create_3d_text(text, font_path, extrusion)
        filename = text.replace(" ", "_")
        output_path = f"C:/Users/harry/Projects/python-helpers/3d-mesh/exported_assets/{filename}.obj"  # Modify the output path accordingly
        export_obj(text_obj, output_path)

if __name__ == "__main__":
    strings_to_create = ['BELU COLOMBO', 'JUANO Z', 'WISER', 'MBVR', 'DÉCADANCE']
    font_file_path = "C:/Users/harry/AppData/Local/Microsoft/Windows/Fonts/AmericanHorrorStory.otf"  # Replace with the path to your font file
    extrusion_value = 0.1  # Adjust the extrusion value as needed

    main(strings_to_create, font_file_path, extrusion_value)