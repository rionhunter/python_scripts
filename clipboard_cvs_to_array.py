import pyperclip

def cvsToPoolStringArray():
    cvs = pyperclip.paste()
    cvs = cvs.split(',')
    for i in range(len(cvs)):
        cvs[i] = "'" + cvs[i] + "'"
    cvs = '[' + ','.join(cvs) + ']'
    pyperclip.copy(cvs)
    print(cvs)

cvsToPoolStringArray()
