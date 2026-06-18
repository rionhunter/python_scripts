import os
import easygui

def get_file_size(file_path):
    return os.path.getsize(file_path)

def humanize_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "{} {}".format(s, size_name[i])

def get_directory_files_info(directory_path):
    file_info = []

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            size = get_file_size(file_path)
            file_info.append((file_path, size))

    return sorted(file_info, key=lambda x: x[1], reverse=True)

def main():
    title = "Select Directory"
    msg = "Choose a directory to assess files"
    directory = easygui.diropenbox(msg=msg, title=title)

    if directory:
        file_info = get_directory_files_info(directory)

        output_file_path = os.path.join(directory, "file_sizes.txt")
        with open(output_file_path, "w") as f:
            f.write("Directory: {}\n\n".format(directory))
            f.write("File Size List (largest to smallest):\n")
            for file_path, size in file_info:
                size_humanized = humanize_size(size)
                f.write("{:<80}Size: {:>10}\n".format(file_path, size_humanized))

        easygui.msgbox("File sizes compiled successfully!\nOutput file: {}".format(output_file_path))

if __name__ == "__main__":
    import math
    main()
