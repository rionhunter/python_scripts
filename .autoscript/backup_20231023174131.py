from AI import Agent
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys
import asyncio
from data import roles
import os
from ast import literal_eval
import traceback

import autoscript

pre_dev_data = {"idea":'', 'outline':'', 'tree':''}


plan = [[{'project_outliner':['idea', 'outline', 'README.md']}], 
        [{'tree_mapper':['outline', 'tree', "tree.md"]}],
        [{'tree_to_list':['tree', 'file_list', 'file_list.txt']}], 
        ]



project_path = ''

def extract_script(string):
    output = ''
    key = '```'
    if key in string:
        lines = string.split('\n')
        within_script = False
        for line in lines:
            if line.startswith(key):
                within_script = ~within_script
                continue
            if within_script:
                output += line + '\n'
    else: return string
    return output

def actualize_data_from_string(string):
# Create an empty dictionary to store the arrays
    arrays_dict = {}
    # Safely execute the code, storing arrays in the dictionary
    exec(string, {}, arrays_dict)
    return arrays_dict

def create_directory(incoming_path):
    try:
        if not os.path.exists(incoming_path):
            os.makedirs(incoming_path)
        else:
            print("Directory already exists!")
    except OSError:
        print("Failed to create the directory!")

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys

def get_user_idea():
    def on_submit():
        user_input.set(text_box.get("1.0", tk.END).strip())
        popup.quit()

    def on_cancel():
        sys.exit("User cancelled.")
        quit()

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    popup = tk.Toplevel(root)
    popup.title("Initial Objective")

    radio_var = tk.StringVar()
    radio_var.set("text")

    def select_file():
        file_path = filedialog.askopenfilename(parent=popup, title="Select File")
        if file_path:
            user_input.set(file_path)
        else:
            user_input.set("")

    ttk.Radiobutton(popup, text="Text", variable=radio_var, value="text").pack(side='left', padx=10, pady=10)
    ttk.Radiobutton(popup, text="File", variable=radio_var, value="file").pack(side='right', padx=10, pady=10)

    user_input = tk.StringVar()

    def show_text_entry():
        text_box.pack(padx=10, pady=10)
        file_button.pack_forget()

    def show_file_selection():
        text_box.pack_forget()
        file_button.pack(padx=10, pady=10)

    ttk.Button(popup, text="Submit", command=on_submit).pack(side='left', padx=10, pady=10)
    ttk.Button(popup, text="Cancel", command=on_cancel).pack(side='right', padx=10, pady=10)

    text_box = tk.Text(popup, wrap='word', width=40, height=10)

    file_button = ttk.Button(popup, text="Select File", command=select_file)

    radio_var.trace("w", lambda *args: show_text_entry() if radio_var.get() == "text" else show_file_selection())

    show_text_entry()

    popup.mainloop()
    popup.destroy()
    root.destroy()

    return user_input.get()


def does_go_to_file(packet):
    if len(packet) > 2:
        return True
    else: return False

def deconstruct_step(incoming_step, dict):
    step_role = list(incoming_step.keys())[0]
    packet = incoming_step[step_role]
    data_key = packet[0]
    output_key = packet[1]
    if does_go_to_file(packet):
        file_key = packet[2]
    else:
        file_key = ''
    
    output = ''
    if data_key in list(dict.keys()):
        output = dict[data_key]
    else:
        output = data_key
    
    return step_role, output, output_key, file_key

async def action(role_title, prompt, output_key):
    agent = Agent.New(roles[role_title])
    
    # Assuming agent.task is also made asynchronous
    output = extract_script(await agent.task(prompt, "gpt-3.5-turbo"))
    
    return output


async def run_step(step_dictionary, dict):
    role, packet, destination, location = deconstruct_step(step_dictionary, dict)
    
    step_results = await action(role, packet, destination)
    dict[destination] = step_results
    if location != '':
        full_location = local_path(location)
        await write_to_file(full_location, step_results)
    return step_results


async def run_phase(array_of_steps, dict):
    output = ''
    for entry in array_of_steps:
        output += await run_step(entry, dict) + '\n\n'
    return output


def local_path(file):
    return str(project_path + '/' + file)

async def write_to_file(path, content):
    # print('writing file: ' + path)
    with open(path, 'w') as file:
        file.write(content)

async def establish_documentation(script_path, data_packet):
    path_pieces = entry.split('/')
    output_name = path_pieces[-1].split('.')[0:-1] + '_documentation.md'
    output_path = path_pieces[0:-1]

import os

async def establish_documentation_location(script_path, data_packet):
    path_pieces = script_path.split('/')
    output_name = os.path.splitext(path_pieces[-1])[0] + '_documentation.md'
    output_path = '/'.join(path_pieces[:-1])
    return output_path

async def create_documentation_by_script_path(script_path, data_packet):
    doc_path = establish_documentation_location(script_path)
    request = f"write the markdown documentation for the yet-to-be-written {script_path}, exploring all the potential and/or necessary objects/functions/classes, debugging avenues, list of test functions to be created, and its compatibility with the rest of the project detailed below. Then with all avenues and options explored, choose the wisest outcomes and return just the markdown documentation in succinctness: \n' + {data_packet}"
    response = await action('documentor', request)
    await write_to_file(doc_path, response)
    return response


async def launch_python_programmers(entry, incoming):
    # print(f'creating {entry} with {incoming}')
    package = "\n" + incoming['outline'] + '\n\n' + incoming['tree']
    documentation = create_documentation_by_script_path(entry, package)
    script_request = f"Write the contents of {entry} for the following project: {package} \n {entry} has the following independent plan: \n {documentation}"
    incoming_script = await action('python_programmer', script_request, entry)
    incoming_script = extract_script(incoming_script)
    
    ## inject here
    
    
    await write_to_file(entry, incoming_script)



async def launch_python_programmers(entry : dict, incoming):
    package = "\n" + incoming['outline'] + '\n\n' + incoming['tree']
    documentation = create_documentation_by_script_path(entry, package)
    script_request = f"Write the contents of {entry} for the following project: {package} \n {entry} has the following independent plan: \n {documentation}"
    incoming_script = await action('python_programmer', script_request, entry)
    incoming_script = extract_script(incoming_script)

    try:
        await write_to_file(entry, incoming_script)
    except Exception as e:
        print(f"Failed to launch: {entry}")
        print(f"Error: {type(e).__name__}: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        print("Retrying with automatic execution...")
        
        try:
            exec(incoming_script)
            print("Script executed successfully.")
        except Exception as e:
            print(f"Failed to execute script: {type(e).__name__}: {str(e)}")
            traceback.print_exc(file=sys.stdout)

def get_filetype(path):
    return path.split("/")[-1].split(".")[-1]

async def delegate_by_filetype(filepath, d):
    extension = get_filetype(filepath)
    if extension == 'py':
        return await launch_python_programmers(filepath, d)
    if extension == 'md':
        return await action('documentor', f'write {filepath} for {d}')

def create_directories(files):
    for folder in files['directories']:
        current_path = local_path(folder)
        create_directory(current_path)

async def create_empty_files(paths):
    for entry in paths:
        with open(local_path(entry), 'w') as file:
            file.write('')

def write_idea_to_file(project_path, results):
    with open(f"{project_path}/idea.txt", 'w') as project_idea:
        project_idea.write(results['idea'])

async def run_phases(plan, results):
    outcome = ''
    for phase in plan:
        outcome += await run_phase(phase, results) + '\n'
    return outcome


temp_main = ''
async def main():

    write_idea_to_file(project_path, pre_dev_data)
    outcome = await run_phases(plan, pre_dev_data)
    
    files = actualize_data_from_string(pre_dev_data['file_list'])
    create_directories(files)
    await create_empty_files(files['empty_files'])
    await asyncio.gather(*(delegate_by_filetype(local_path(entry), pre_dev_data) for entry in files['project_files']))



temp_prompt = "Dictionary Constructor GUI - python gui interface that allows the user to build up a dictionary, adding new slots of differing value types, including further nested dictionaries - which open in a new window. User can save, load, edit and duplicate the resulting dictionary structures, and export to various formats including json, csv, python, .txt, or python compatible straight to the clipboard. External modules will need to be able to summon the user created dictionaries by identifying the structure's name"
# results['idea'] = temp_prompt
project_path = filedialog.askdirectory()
pre_dev_data['idea'] = get_user_idea()
# project_path = '/media/rion/110eca41-fdfe-487d-ae01-bd5eb58d47c3/Catalogue/scripts/Python/data_management/dictionary/'

if __name__ == '__main__':
    asyncio.run(main())
    
    
autoscript.run(__file__)
