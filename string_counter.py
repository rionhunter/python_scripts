"""
1. using easyGUI, ask the user for a body of text (that will be a combination of numbers with decimal points jumbled up amongst text)
2. scrape all the figures from the text
3. add all the values from the text together
4. display the resulting figure, and give the user the option - with a button - to copy the resulting sum to the clipboard
"""

import easygui
import re

def get_text():
    text = easygui.enterbox("Please enter some text with numbers and decimal points jumbled up amongst it")
    return text

def get_numbers(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return numbers

def add_numbers(numbers):
    total = 0
    for number in numbers:
        total += float(number)
    return total

def display_total(total):
    easygui.msgbox("The total is: " + str(total))

def copy_to_clipboard(total):
    easygui.buttonbox("The total is: " + str(total) + "\n\nCopy to clipboard?", choices = ["Yes", "No"])
    return

def main():
    text = get_text()
    numbers = get_numbers(text)
    total = add_numbers(numbers)
    display_total(total)
    copy_to_clipboard(total)

main()
