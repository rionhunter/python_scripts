import bpy

# Select the object you want to work with
obj = bpy.context.active_object

# Store the object's current location, rotation, and scale
location = obj.location.copy()
rotation = obj.rotation_euler.copy()
scale = obj.scale.copy()

# Create an empty at the object's location
bpy.ops.object.empty_add(location=location)

# Get the newly created empty
empty = bpy.context.active_object

# Apply constraints to the original object
constraint_location = obj.constraints.new(type='COPY_LOCATION')
constraint_location.target = empty
constraint_scale = obj.constraints.new(type='COPY_SCALE')
constraint_scale.target = empty
constraint_rotation = obj.constraints.new(type='COPY_ROTATION')
constraint_rotation.target = empty

# Set the influence to 1 for all constraints
for constraint in [constraint_location, constraint_scale, constraint_rotation]:
    constraint.influence = 1

# Clear the object's location, rotation, and scale
obj.location = (0, 0, 0)
obj.rotation_euler = (0, 0, 0)
obj.scale = (1, 1, 1)
