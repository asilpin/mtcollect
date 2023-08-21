import sys
import os

def delete_files_ending_in(file_types):
    """Deletes any files that have a extension in file_types (List)."""
    dir = os.getcwd()
    for item in os.listdir(dir):
        if item == "requirements.txt":
            continue

        for file_type in file_types:

            if item.endswith(file_type):
                os.remove(os.path.join(dir, item))
                break
