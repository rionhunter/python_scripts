#!/usr/bin/env python3
"""
Simple GUI to set a global (system) environment variable on Windows.

Run this script as administrator to modify system environment variables.
"""
import sys
import tkinter as tk
from tkinter import messagebox

if sys.platform != "win32":
    messagebox.showerror("Unsupported OS", "This script only works on Windows.")
    sys.exit(1)

import winreg
import ctypes

def set_system_environment_variable(name, value):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0, "Environment",
            SMTO_ABORTIFHUNG, 5000,
            ctypes.byref(result)
        )
        return True, None
    except PermissionError:
        return False, "Permission denied. Please run this script as administrator."
    except Exception as e:
        return False, str(e)

def on_set():
    name = entry_name.get().strip()
    value = entry_value.get().strip()
    if not name:
        messagebox.showwarning("Input error", "Please enter a variable name.")
        return
    success, error = set_system_environment_variable(name, value)
    if success:
        messagebox.showinfo("Success", f"'{name}' set to '{value}'.")
    else:
        messagebox.showerror("Error", f"Failed to set variable:\n{error}")

root = tk.Tk()
root.title("Set System Environment Variable")
tk.Label(root, text="Variable Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_name = tk.Entry(root, width=40)
entry_name.grid(row=0, column=1, padx=5, pady=5)
tk.Label(root, text="Variable Value:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_value = tk.Entry(root, width=40)
entry_value.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Set Variable", command=on_set).grid(row=2, column=0, columnspan=2, pady=10)
root.resizable(False, False)
root.mainloop()