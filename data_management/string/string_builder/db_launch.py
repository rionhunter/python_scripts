import sqlite3

# connect to the database
conn = sqlite3.connect('ai_prompts.db')

# create the table for storing the AI prompts
conn.execute('''
    CREATE TABLE prompts (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL,
        prompt TEXT NOT NULL
    );
''')

# create the table for storing the built-up string
conn.execute('''
    CREATE TABLE string (
        id INTEGER PRIMARY KEY,
        string TEXT NOT NULL
    );
''')

# commit the changes and close the connection
conn.commit()
conn.close()
