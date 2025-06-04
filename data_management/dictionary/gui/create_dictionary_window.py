import PyQt5.QtWidgets as QtWidgets

class CreateDictionaryWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Dictionary")

        self.setup_ui()
    
    def setup_ui(self):
        # Create the main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Add a label for the dictionary name
        name_label = QtWidgets.QLabel("Dictionary Name:")
        main_layout.addWidget(name_label)

        # Add a line edit for the dictionary name
        self.name_line_edit = QtWidgets.QLineEdit()
        main_layout.addWidget(self.name_line_edit)

        # Add a button to create the dictionary
        create_button = QtWidgets.QPushButton("Create")
        create_button.clicked.connect(self.create_dictionary)
        main_layout.addWidget(create_button)

    def create_dictionary(self):
        # Get the dictionary name from the line edit
        dictionary_name = self.name_line_edit.text()

        # Validate the dictionary name
        if not dictionary_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a dictionary name.")
            return

        # TODO: Create the dictionary and pass it to the main application window

        # Close the create dictionary window
        self.accept()
