import json
import os

# Prompt user for JSON file path
json_path = input('Enter the path to your JSON file: ').strip()
if not os.path.isfile(json_path):
    print('File not found.')
    exit(1)

# Load JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

if not isinstance(data, dict):
    print('JSON root is not an object/dictionary.')
    exit(1)

# Show available keys
keys = list(data.keys())
print('Available keys:')
for idx, key in enumerate(keys):
    print(f'{idx+1}: {key}')

# Prompt user to select a key
try:
    choice = int(input('Select a key by number: ')) - 1
    if choice < 0 or choice >= len(keys):
        raise ValueError
except ValueError:
    print('Invalid selection.')
    exit(1)

selected_key = keys[choice]
selected_value = data[selected_key]

# Prompt user for export file path
export_path = input('Enter the export file path: ').strip()

# Write the value to the export file
with open(export_path, 'w', encoding='utf-8') as f:
    if isinstance(selected_value, (dict, list)):
        json.dump(selected_value, f, indent=2, ensure_ascii=False)
    else:
        f.write(str(selected_value))

print(f'Value for key "{selected_key}" exported to {export_path}')
