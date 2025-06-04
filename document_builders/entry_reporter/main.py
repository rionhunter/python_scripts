from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph, Table, TableStyle, PageBreak

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from PIL import Image as PILImage
from datetime import datetime
from os.path import isfile
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog, simpledialog
from reportlab.pdfgen import canvas

styles = getSampleStyleSheet()

styles = getSampleStyleSheet()


# Define your custom footer function
def footer(canvas, doc):
    canvas.saveState()
    page_number_text = f"Page {canvas.getPageNumber()}"
    footer_text = f"{datetime.now().strftime('%Y-%m-%d')}"
    canvas.drawRightString(7.25*inch, 0.75*inch, page_number_text)
    canvas.drawString(inch, 0.75 * inch, footer_text)
    canvas.restoreState()

class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add the page number to each page (override the save method)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawString(inch, 0.75 * inch, f"{datetime.now().strftime('%Y-%m-%d')}")
        self.drawRightString(200*mm, 0.75 * inch, f"Page {self._pageNumber} of {page_count}")

# Define your main application class
class QuickPropertyReport:
    def __init__(self, master):
        self.master = master
        self.master.title("Quick Property Report Generator")

        self.image_list = []
        self.categories = ["Living Room", "Kitchen", "Bathroom"]  # Predefined categories
        self.image_category_dict = {}  # To store image paths and their categories
        
        self.category_var = tk.StringVar(master)
        self.category_var.set(self.categories[0])  # Set the default value
        
        tk.Button(master, text="Add Images", command=self.add_images).pack()
        tk.Button(master, text="Add Category", command=self.add_category).pack()
        
        self.category_menu = tk.OptionMenu(master, self.category_var, *self.categories)
        self.category_menu.pack()
        
        tk.Button(master, text="Generate PDF", command=self.generate_pdf).pack()

    def add_images(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            category = self.category_var.get()
            for path in file_paths:
                if isfile(path):
                    self.image_category_dict[path] = category
                else:
                    messagebox.showerror("Error", f"File does not exist: {path}")
            print("Images added:", file_paths)  # Just to give you some feedback in the console

    def add_category(self):
        new_category = simpledialog.askstring("Input", "Enter the new category:")
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_menu['menu'].add_command(label=new_category, command=tk._setit(self.category_var, new_category))
            print("New category added:", new_category)  # Feedback in the console

    def generate_pdf(self):
        pdf_path = "Property_Report.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, bottomMargin=2*inch)
        doc.canvasmaker = FooterCanvas

        Story = []
        # Index array to store category titles and their start page number
        index_entries = []

        # Define the styles for the index and category headings
        index_style = styles['Heading2']
        category_style = styles['Heading1']

        # Add a title for the index page
        Story.append(Paragraph('Index', index_style))
        Story.append(PageBreak())

        # Function to build the index page with category titles and page numbers
        def build_index(Story, index_entries):
            Story.append(Paragraph('Index', category_style))
            Story.append(Spacer(1, 0.2 * inch))
            for entry in index_entries:
                # Add the category title and the page number to the index
                Story.append(Paragraph(f"{entry[0]}: {entry[1]}", styles['Normal']))
                Story.append(Spacer(1, 0.1 * inch))
            Story.append(PageBreak())  # Add a page break after the index

        # Main loop to process categories and images
        for idx, category in enumerate(self.categories):
            # Placeholder for the index entry; page number to be determined after the document is built
            index_entries.append([category, '...'])  # Replace '...' with the page number later

            # Add category header on a new page
            Story.append(PageBreak())
            Story.append(Paragraph(f'<b>{category}</b>', category_style))
            Story.append(Spacer(1, 0.2 * inch))

            image_paths = self.image_category_dict.get(category, [])
            image_data = []

            for img_path in image_paths:
                if isfile(img_path):
                    pil_image = PILImage.open(img_path)
                    image_width, image_height = pil_image.size
                    aspect = image_height / float(image_width)

                    # Calculate image dimensions to fit within a certain width while maintaining aspect ratio
                    if aspect > 1:
                        # Portrait orientation
                        img_height = 3.5 * inch
                        img_width = img_height / aspect
                    else:
                        # Landscape orientation
                        img_width = 3.5 * inch
                        img_height = img_width * aspect

                    pil_image.close()

                    # Append the image to the image_data list, resizing it to fit the page
                    img = Image(img_path, width=img_width, height=img_height)

                    # Append two images side by side in the same row if they are both portrait
                    if len(image_data) % 2 == 0 or aspect <= 1:
                        image_data.append([img])
                    else:
                        image_data[-1].append(img)
                else:
                    print(f"File does not exist: {img_path}")

            # If the last row has only one image, fill the next cell with a blank string
            if image_data and len(image_data[-1]) == 1:
                image_data[-1].append('')

            # Add images to the story
            for row in image_data:
                Story.append(Table([row], colWidths=[3.5 * inch, 3.5 * inch]))

        # After adding all categories and images, create the index page with placeholders
        build_index(Story, index_entries)

        # Build the PDF with index placeholders
        doc.build(Story, onFirstPage=on_first_page, onLaterPages=on_later_pages)

        # Rebuild the document, now that we know the page numbers for each category
        def rebuild_with_page_numbers(canvas, doc):
            # Add footer
            add_footer(canvas, doc)

            # Grab the page number and update the index entries
            for idx, entry in enumerate(index_entries):
                if canvas.getPageNumber() == idx + 2:  # Index is on page 1, categories start from page 2
                    entry[1] = str(canvas.getPageNumber())

        # Reset the story and add the updated index
        Story = [Paragraph('Index', styles['Heading1'])]
        Story.append(Spacer(1, 12))
        for entry in index_entries:
            Story.append(Paragraph(f'{entry[0]}: {entry[1]}', styles['Normal']))
            Story.append(Spacer(1, 12))
        Story.append(PageBreak())  # Add a page break after the index

        # Re-add the rest of the content
        for category in self.categories:
            Story.append(Paragraph(f'<b>{category}</b>', styles['Heading2']))
            Story.append(Spacer(1, 0.2 * inch))
            # ... [The rest of your report content generation] ...

        # Build the final PDF
        doc.build(Story, onFirstPage=rebuild_with_page_numbers, onLaterPages=rebuild_with_page_numbers)

        print(f"PDF generated at: {pdf_path}")

    def add_page_number(self, canvas, doc):
        """
        Add the page number
        """
        number = canvas.getPageNumber()
        text = f"Page {number} - {datetime.now().strftime('%Y-%m-%d')}"
        canvas.drawRightString(200*mm, 20*mm, text)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickPropertyReport(root)
    root.mainloop()
