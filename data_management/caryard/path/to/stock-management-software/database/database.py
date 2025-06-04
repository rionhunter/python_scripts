import sqlite3
from datetime import datetime

class StockDatabase:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to the database."""
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """Disconnect from the database and save changes."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_table(self):
        """Create a table to store stock information if it does not already exist."""
        self.connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                availability INTEGER,
                                condition TEXT,
                                price REAL,
                                created_at TEXT,
                                updated_at TEXT
                            )''')
        self.disconnect()

    def add_stock(self, name, availability, condition, price):
        """Add a new stock item to the database."""
        self.connect()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_at = created_at

        self.cursor.execute('''INSERT INTO stock 
                            (name, availability, condition, price, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (name, availability, condition, price, created_at, updated_at))

        self.disconnect()

    def update_stock(self, stock_id, availability=None, condition=None, price=None):
        """Update the details of a stock item in the database."""
        self.connect()
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if availability is not None:
            self.cursor.execute('''UPDATE stock 
                                SET availability = ?, updated_at = ? 
                                WHERE id = ?''',
                                (availability, updated_at, stock_id))

        if condition is not None:
            self.cursor.execute('''UPDATE stock 
                                SET condition = ?, updated_at = ? 
                                WHERE id = ?''',
                                (condition, updated_at, stock_id))

        if price is not None:
            self.cursor.execute('''UPDATE stock 
                                SET price = ?, updated_at = ? 
                                WHERE id = ?''',
                                (price, updated_at, stock_id))

        self.disconnect()

    def search_stock(self, name):
        """Search for stock items based on name."""
        self.connect()
        self.cursor.execute('''SELECT * FROM stock WHERE name LIKE ?''', ('%' + name + '%',))
        results = self.cursor.fetchall()
        self.disconnect()
        return results

    def get_stock_details(self, stock_id):
        """Retrieve the details of a specific stock item."""
        self.connect()
        self.cursor.execute('''SELECT * FROM stock WHERE id = ?''', (stock_id,))
        result = self.cursor.fetchone()
        self.disconnect()
        return result

    def get_stock_count(self):
        """Get the total number of stock items in the database."""
        self.connect()
        self.cursor.execute('''SELECT COUNT(*) FROM stock''')
        count = self.cursor.fetchone()[0]
        self.disconnect()
        return count

    def delete_stock(self, stock_id):
        """Delete a stock item from the database."""
        self.connect()
        self.cursor.execute('''DELETE FROM stock WHERE id = ?''', (stock_id,))
        self.disconnect()

    def delete_all_stock(self):
        """Delete all stock items from the database."""
        self.connect()
        self.cursor.execute('''DELETE FROM stock''')
        self.disconnect()

    def backup_database(self, backup_path):
        """Create a backup of the database."""
        self.disconnect()

        with open(self.database_path, 'rb') as source_file:
            with open(backup_path, 'wb') as dest_file:
                dest_file.write(source_file.read())

        self.connect()