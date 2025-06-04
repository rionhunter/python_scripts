import bpy

# Get the active object (assumed to be a mesh)
obj = bpy.context.active_object

# Check if the active object is a mesh
if obj.type == 'MESH':
    # Create a new collection for the empty objects
    empty_collection = bpy.data.collections.new("EmptyObjects")
    bpy.context.scene.collection.children.link(empty_collection)
    
    # Switch to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Iterate through selected vertices
    for vertex in obj.data.vertices:
        # Create an empty at the vertex location
        empty = bpy.data.objects.new("Empty", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = obj.matrix_world @ vertex.co
        empty.scale = (0.1, 0.1, 0.1)  # Set the scale to 1/10th
        
        # Link the empty to the empty collection
        empty_collection.objects.link(empty)
