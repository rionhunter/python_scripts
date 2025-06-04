import bpy

# Make sure Cycles is the active rendering engine
bpy.context.scene.render.engine = 'CYCLES'

# Get and print available devices
cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.get_devices()
for device in cycles_prefs.devices:
    if device.type == 'CUDA' or device.type == 'OPTIX':
        print(f"Device: {device.name}, Type: {device.type}")
