import dictionary.dictionary as dict

def access_dictionary_structure(structure_name):
    """
    Accesses a user-created dictionary structure by identifying its structure name.

    Args:
    - structure_name: A string representing the name of the dictionary structure.

    Returns:
    - A dictionary object representing the requested dictionary structure if found.
    - None if the dictionary structure is not found.
    """
    return dict.get_dictionary_structure(structure_name)
