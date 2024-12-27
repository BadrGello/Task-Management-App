import os
import shutil
import glob

# Define the source and destination paths
source_dir = 'dist/main/_internal'
destination_dir = 'dist/main/APP'

# List of folders and files to move
items_to_move = ['Audio', 'Icons', 'Images', '*.qss','sort.png']

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Move the folders and files
for item in items_to_move:
    src = os.path.join(source_dir, item)
    dest = os.path.join(destination_dir, item)
    if os.path.exists(src):
        shutil.move(src, dest)
    else:
        # Handle wildcard patterns
        for file in glob.glob(os.path.join(source_dir, item)):
            shutil.move(file, destination_dir)

print("Folders and files moved successfully!")
