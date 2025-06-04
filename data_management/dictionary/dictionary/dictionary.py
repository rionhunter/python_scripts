# dictionary.py

import json

class Dictionary:
    def __init__(self, name):
        self.name = name
        self.slots = {}

    def add_slot(self, slot_name, value_type):
        self.slots[slot_name] = value_type

    def edit_slot_value(self, slot_name, new_value):
        if slot_name in self.slots:
            self.slots[slot_name] = new_value
        else:
            raise ValueError(f"Slot '{slot_name}' does not exist in the dictionary.")

    def duplicate(self):
        new_dict = Dictionary(self.name + "_copy")
        new_dict.slots = self.slots.copy()
        return new_dict

    def export_to_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump({self.name: self.slots}, f)

    def __str__(self):
        return f"Dictionary '{self.name}' with slots: {self.slots}"


# Usage Example

# Create a dictionary
my_dict = Dictionary("MyDictionary")

# Add slots
my_dict.add_slot("Name", str)
my_dict.add_slot("Age", int)
my_dict.add_slot("Height", float)
my_dict.add_slot("IsStudent", bool)
my_dict.add_slot("NestedDict", dict)

# Edit slot value
my_dict.edit_slot_value("Name", "John Doe")

# Duplicate dictionary
copied_dict = my_dict.duplicate()

# Export dictionary to JSON file
my_dict.export_to_json("my_dict.json")

# Print dictionary details
print(my_dict)