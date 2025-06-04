import argparse
import json
import tkinter as tk
from tkinter import simpledialog, filedialog
import webbrowser
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class ScreenplayCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self._pageNumber > 1:  # Start page numbering from the second page
                self.drawPageNumber(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def drawPageNumber(self, page_count):
        self.setFont("Helvetica", 10)
        self.drawRightString(750, 800, f"Page {self._pageNumber} of {page_count}")
        # Add any additional headers or footers here, like draft date or version number


def generate_screenplay(data, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            leftMargin=1.5*72, rightMargin=1*72,
                            topMargin=1*72, bottomMargin=1*72,
                            canvasmaker=ScreenplayCanvas)  # Setting margins
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Courier'
    styles['Normal'].fontSize = 12
    styles.add(ParagraphStyle(name='Center', alignment=1, spaceAfter=12, fontName="Courier", fontSize=12))
    
    styles.add(ParagraphStyle(name='SceneHeader', 
                          fontName='Courier', 
                          fontSize=12, 
                          leading=14,  # Leading is line spacing
                          spaceAfter=6,  # Space after the header
                          spaceBefore=6,  # Space before the header
                          leftIndent=0, 
                          rightIndent=0,
                          firstLineIndent=0,
                          alignment=0,  # Left align
                          textColor=colors.black,
                          backColor=None,
                          wordWrap=None,
                          borderWidth=0,
                          borderPadding=0,
                          borderColor=None,
                          borderRadius=None,
                          allowWidows=1,
                          allowOrphans=0,
                          textTransform='uppercase',  # This makes the text uppercase
                          endDots=None,
                          splitLongWords=1,
                          underline=False,
                          bulletFontName='Courier',
                          bulletFontSize=10,
                          bulletIndent=0,
                          bulletColor=colors.black))

    
    
    story = []
    title = Paragraph(f"<u><b>{data['title']}</b></u>", styles['Title'])
    story.append(title)
    

    for scene in data['scenes']:
        for entry in ['int_ext', 'location', 'time_of_day']:
            scene[entry] = scene[entry].upper()
        scene_header = Paragraph(f"<u>{scene['int_ext']} - {scene['location']} - {scene['time_of_day']}</u>", styles['SceneHeader'])
        story.append(scene_header)
        story.append(Spacer(1, 24))  # Two-line space

        description = Paragraph(scene.get('description', ''), styles['Normal'])
        story.append(description)

        for action in scene.get('actions', []):
            char = Paragraph(f"<b>{action['character']}</b>", styles['Center'])
            story.append(char)

            act = Paragraph(action.get('action', ''), styles['Normal'])
            story.append(act)

            dialogue = Paragraph(action.get('dialogue', ''), styles['Normal'])
            story.append(dialogue)

    ending = Paragraph(data['ending'], styles['Normal'])
    story.append(ending)
    
    doc.build(story)
    
    webbrowser.open(output_path)  # Open the PDF




def get_json_from_text():
    root = tk.Tk()
    root.title("Paste your JSON string here")
    text = tk.Text(root, wrap='word')  # word wrap
    text.pack(expand=1, fill='both')  # fill the window
    button = tk.Button(root, text="Submit", command=lambda: root.quit())
    button.pack(side='bottom')
    root.mainloop()
    json_string = text.get("1.0", 'end-1c')  # get text from Text widget
    root.destroy()
    return json_string


def get_output_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Generate a screenplay from JSON data.')
    parser.add_argument('--json-file', help='Path to the JSON file containing the screenplay data.')
    parser.add_argument('--json-string', help='JSON string containing the screenplay data.')
    parser.add_argument('--output', help='Path to save the generated screenplay PDF.')
    args = parser.parse_args()

    output_path = args.output if args.output else get_output_path()
    if not output_path:
        print("Output path is required.")
        return

    if args.json_file:
        with open(args.json_file, 'r') as f:
            data = json.load(f)
            generate_screenplay(data, output_path)
    elif args.json_string:
        data = json.loads(args.json_string)
        generate_screenplay(data, output_path)
    else:
        json_string = get_json_from_text()
        if json_string:
            data = json.loads(json_string)
            generate_screenplay(data, output_path)
        else:
            filepath = filedialog.askopenfilename(title="Select your JSON file", filetypes=[("JSON files", "*.json")])
            if filepath:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    generate_screenplay(data, output_path)

if __name__ == '__main__':
    main()
