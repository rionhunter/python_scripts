#!/usr/bin/env python3
import easygui

def intersperse(s):
    """
    >>> intersperse('abc')
    'a:b:c'
    >>> intersperse('Alt+a')
    'Alt+a'
    >>> intersperse('Ctrl+Alt+k')
    'Ctrl+Alt+k'
    """
    if s.find('+') != -1:
        return s
    else:
        return ':'.join(s)

def main():
    s = easygui.enterbox('Enter a string:')
    easygui.textbox('Result', '', intersperse(s))

if __name__ == '__main__':
    main()
