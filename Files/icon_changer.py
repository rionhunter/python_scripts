import easygui as gui

def create_desktop_file(icon_path, script_path):
    desktop_content = f'''[Desktop Entry]
Type=Application
Name=My Script
Exec={script_path}
Icon={icon_path}
'''

    script_name = script_path.split("/")[-1]
    desktop_filename = script_name.replace(".sh", ".desktop")

    desktop_path = f'~/.local/share/applications/{desktop_filename}'
    desktop_path = desktop_path.replace("~", "/home/rion")  # Replace with your actual home directory

    with open(desktop_path, "w") as desktop_file:
        desktop_file.write(desktop_content)

def main():
    icon_path = gui.fileopenbox(msg="Select an Icon", filetypes=["*.png", "*.svg"])
    script_path = gui.fileopenbox(msg="Select a Shell Script", filetypes=["*.sh"])

    if icon_path and script_path:
        create_desktop_file(icon_path, script_path)
        gui.msgbox("Desktop file created successfully!")

if __name__ == "__main__":
    main()
