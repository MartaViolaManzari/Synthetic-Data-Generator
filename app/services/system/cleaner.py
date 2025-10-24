import os
import shutil
 
# Remove temporary files from folder
def clean_folder(folder_path: str):
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting files in {folder_path}: {e}")
        print(f"Files in '{folder_path}' were deleted.")
    else:
        raise ValueError(f"Folder '{folder_path}' does not exist.")
 
 
# Remove temporary files and subfolder from folder 
def clean_folder_tree(folder_path: str):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for subdir in os.listdir(folder_path):
            full_subdir_path = os.path.join(folder_path, subdir)
            if os.path.isdir(full_subdir_path):
                shutil.rmtree(full_subdir_path)
                print(f"Subfolders and files in {full_subdir_path} were deleted.")
        