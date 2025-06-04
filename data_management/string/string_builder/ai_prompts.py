import sqlite3
import tkinter as tk

# create a database connection
conn = sqlite3.connect('ai_prompts.db')

# create a window
root = tk.Tk()

# create a database cursor
cursor = conn.cursor()

# create the ai_prompts table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_prompts (
        snippet TEXT,
        category TEXT
    )
''')
conn.commit()

# create a function to add new snippets to the database
def add_snippet():
    # get the user-entered snippet and category
    snippet = snippet_input.get()
    category = category_var.get()

    # insert the snippet into the database
    cursor.execute('INSERT INTO ai_prompts VALUES (?, ?)', (snippet, category))
    conn.commit()

    # clear the input fields
    snippet_input.delete(0, tk.END)
    category_var.set('')

    # update the list of categories
    update_categories()

# create a function to search for snippets
def search_snippets():
    # get the user-entered search query
    query = search_input.get()

    # search the database for snippets matching the query
    cursor.execute('SELECT * FROM ai_prompts WHERE snippet LIKE ?', (f'%{query}%',))

    # display the search results in the listbox
    search_results = cursor.fetchall()
    search_list.delete(0, tk.END)
    for result in search_results:
        search_list.insert(tk.END, result)

# create a function to add selected snippets to the string
def add_to_string(event):
    # get the selected snippet
    snippet = search_list.get(search_list.curselection())

    # add the snippet to the string
    string_text.insert(tk.END, snippet)

# create a function to replace underscores with other snippets or custom strings
def replace_underscores():
    # get the string with underscores
    string = string_text.get(1.0, tk.END)

    # get the user-entered replacement snippet or string
    replacement = replace_input.get()

    # replace the underscores in the string with the replacement
    new_string = string.replace('_', replacement)

    # update the string text with the new string
    string_text.delete(1.0, tk.END)
    string_text.insert(1.0, new_string)

# create a function to update the list of categories
def update_categories():
    # get the unique categories from the database
    cursor.execute('SELECT DISTINCT category FROM ai_prompts')
    categories = cursor.fetchall()

    # clear the current categories in the dropdown
    category_var.set('')
    category_input['menu'].delete(0, 'end')

    # add the new categories to the dropdown
    for category in categories:
        category_input['menu'].add_command(label=category[0], command=lambda value=category[0]: category_var.set(value))

# create input fields for adding new snippets
snippet_input = tk.Entry(root)
snippet_label = tk.Label(root, text='Snippet:')
category_var = tk.StringVar(root)
category_input = tk.OptionMenu(root, category_var, '')
category_label = tk.Label(root, text='Category:')

# create a button to add new snippets
add_button = tk.Button(root, text='Add', command=add_snippet)

# create an input field for searching snippets
search_input = tk.Entry(root)
search_label = tk.Label(root, text='Search:')

# create a button to search for snippets
search_button = tk.Button(root, text='Search', command=search_snippets)

# create a listbox to display search results
search_list = tk.Listbox(root)
search_list.bind('<<ListboxSelect>>', add_to_string)

# create an input field for replacing underscores
replace_input = tk.Entry(root)
replace_label = tk.Label(root, text='Replace:')

# create a button to replace underscores
replace_button = tk.Button(root, text='Replace', command=replace_underscores)

# create a text field to display the string
string_label = tk.Label(root, text='String:')
string_text = tk.Text(root, height=10, width=50)

# lay out the widgets in the window
snippet_label.grid(row=0, column=0)
snippet_input.grid(row=0, column=1)
category_label.grid(row=1, column=0)
category_input.grid(row=1, column=1)
add_button.grid(row=0, column=2, rowspan=2)
search_label.grid(row=2, column=0)
search_input.grid(row=2, column=1)
search_button.grid(row=2, column=2)
search_list.grid(row=3, column=0, columnspan=3)
replace_label.grid(row=4, column=0)
replace_input.grid(row=4, column=1)
replace_button.grid(row=4, column=2)
string_label.grid(row=5, column=0)
string_text.grid(row=5, column=1, columnspan=2)

# update the list of categories
update_categories()

# start the event loop
root.mainloop()
