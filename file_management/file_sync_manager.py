"""
File Grab and Sync Manager
A GUI tool for creating persistent project profiles that sync files to a flattened output directory.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import datetime


class FileSyncManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sync Manager")
        self.root.geometry("1000x700")
        
        # Data storage
        self.config_file = Path(__file__).parent / "file_sync_projects.json"
        self.projects: Dict[str, Dict] = self.load_projects()
        self.current_project: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.refresh_project_list()
        
    def setup_ui(self):
        """Create the main UI layout"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Left panel - Project list
        left_panel = ttk.Frame(main_container, padding="5")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(left_panel, text="Projects", font=("", 12, "bold")).pack(pady=5)
        
        # Project listbox
        listbox_frame = ttk.Frame(left_panel)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.project_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, width=25)
        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.project_listbox.yview)
        self.project_listbox.bind('<<ListboxSelect>>', self.on_project_select)
        
        # Project buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="New Project", command=self.new_project).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Delete Project", command=self.delete_project).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Rename Project", command=self.rename_project).pack(fill=tk.X, pady=2)
        
        # Right panel - Project details
        right_panel = ttk.Frame(main_container, padding="5")
        right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(2, weight=1)
        
        # Project name label
        self.project_name_label = ttk.Label(right_panel, text="No Project Selected", 
                                           font=("", 14, "bold"))
        self.project_name_label.grid(row=0, column=0, pady=10, sticky=tk.W)
        
        # Output directory section
        output_frame = ttk.LabelFrame(right_panel, text="Output Directory", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, state='readonly').grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(
            row=0, column=1)
        
        # Files section
        files_frame = ttk.LabelFrame(right_panel, text="Files to Sync", padding="10")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        
        # Files treeview
        tree_frame = ttk.Frame(files_frame)
        tree_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_tree = ttk.Treeview(tree_frame, columns=("Status",), 
                                      yscrollcommand=tree_scroll.set, height=15)
        self.files_tree.heading("#0", text="File Path")
        self.files_tree.heading("Status", text="Status")
        self.files_tree.column("Status", width=100)
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.files_tree.yview)
        
        # File buttons
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(file_btn_frame, text="Add Files", command=self.add_files).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(file_btn_frame, text="Add Folder", command=self.add_folder).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(file_btn_frame, text="Remove Selected", command=self.remove_files).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(file_btn_frame, text="Clear All", command=self.clear_files).pack(
            side=tk.LEFT, padx=2)
        
        # Action buttons
        action_frame = ttk.Frame(right_panel)
        action_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="Sync Files", command=self.sync_files, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Check Status", command=self.check_status).pack(
            side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(right_panel, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def load_projects(self) -> Dict:
        """Load projects from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load projects: {e}")
                return {}
        return {}
    
    def save_projects(self):
        """Save projects to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save projects: {e}")
    
    def refresh_project_list(self):
        """Refresh the project listbox"""
        self.project_listbox.delete(0, tk.END)
        for project_name in sorted(self.projects.keys()):
            self.project_listbox.insert(tk.END, project_name)
    
    def new_project(self):
        """Create a new project"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.geometry("350x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Project Name:").pack(pady=10, padx=10)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5, padx=10)
        name_entry.focus()
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a project name")
                return
            if name in self.projects:
                messagebox.showwarning("Warning", "Project already exists")
                return
            
            self.projects[name] = {
                "output_dir": "",
                "files": [],
                "created": datetime.datetime.now().isoformat(),
                "last_sync": None
            }
            self.save_projects()
            self.refresh_project_list()
            dialog.destroy()
            
            # Select the new project
            idx = sorted(self.projects.keys()).index(name)
            self.project_listbox.selection_clear(0, tk.END)
            self.project_listbox.selection_set(idx)
            self.on_project_select(None)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create", command=create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        name_entry.bind('<Return>', lambda e: create())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def delete_project(self):
        """Delete the selected project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete project '{self.current_project}'?\nThis will not delete the synced files."):
            del self.projects[self.current_project]
            self.save_projects()
            self.current_project = None
            self.refresh_project_list()
            self.update_project_view()
    
    def rename_project(self):
        """Rename the selected project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Rename Project")
        dialog.geometry("350x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="New Project Name:").pack(pady=10, padx=10)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.insert(0, self.current_project)
        name_entry.pack(pady=5, padx=10)
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        def rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Warning", "Please enter a project name")
                return
            if new_name in self.projects and new_name != self.current_project:
                messagebox.showwarning("Warning", "Project already exists")
                return
            
            self.projects[new_name] = self.projects.pop(self.current_project)
            self.current_project = new_name
            self.save_projects()
            self.refresh_project_list()
            self.update_project_view()
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Rename", command=rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        name_entry.bind('<Return>', lambda e: rename())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def on_project_select(self, event):
        """Handle project selection"""
        selection = self.project_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_project = self.project_listbox.get(index)
            self.update_project_view()
    
    def update_project_view(self):
        """Update the right panel with current project details"""
        if not self.current_project:
            self.project_name_label.config(text="No Project Selected")
            self.output_path_var.set("")
            self.files_tree.delete(*self.files_tree.get_children())
            self.status_var.set("Ready")
            return
        
        project = self.projects[self.current_project]
        self.project_name_label.config(text=self.current_project)
        self.output_path_var.set(project.get("output_dir", ""))
        
        # Update files tree
        self.files_tree.delete(*self.files_tree.get_children())
        for file_path in project.get("files", []):
            status = "✓" if os.path.exists(file_path) else "✗ Missing"
            self.files_tree.insert("", tk.END, text=file_path, values=(status,))
        
        # Update status
        last_sync = project.get("last_sync")
        if last_sync:
            sync_time = datetime.datetime.fromisoformat(last_sync)
            self.status_var.set(f"Last sync: {sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.status_var.set("Never synced")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.projects[self.current_project]["output_dir"] = directory
            self.output_path_var.set(directory)
            self.save_projects()
    
    def add_files(self):
        """Add files to the current project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        files = filedialog.askopenfilenames(title="Select Files to Add")
        if files:
            current_files = set(self.projects[self.current_project].get("files", []))
            for file_path in files:
                current_files.add(file_path)
            
            self.projects[self.current_project]["files"] = sorted(list(current_files))
            self.save_projects()
            self.update_project_view()
    
    def add_folder(self):
        """Add all files from a folder to the current project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        folder = filedialog.askdirectory(title="Select Folder to Add")
        if folder:
            current_files = set(self.projects[self.current_project].get("files", []))
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    current_files.add(file_path)
            
            self.projects[self.current_project]["files"] = sorted(list(current_files))
            self.save_projects()
            self.update_project_view()
            messagebox.showinfo("Success", f"Added {len(current_files)} files from folder")
    
    def remove_files(self):
        """Remove selected files from the current project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files to remove")
            return
        
        files_to_remove = [self.files_tree.item(item)["text"] for item in selected_items]
        current_files = self.projects[self.current_project].get("files", [])
        
        for file_path in files_to_remove:
            if file_path in current_files:
                current_files.remove(file_path)
        
        self.projects[self.current_project]["files"] = current_files
        self.save_projects()
        self.update_project_view()
    
    def clear_files(self):
        """Clear all files from the current project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        if messagebox.askyesno("Confirm Clear", "Remove all files from this project?"):
            self.projects[self.current_project]["files"] = []
            self.save_projects()
            self.update_project_view()
    
    def check_status(self):
        """Check the status of all files in the current project"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        project = self.projects[self.current_project]
        files = project.get("files", [])
        
        if not files:
            messagebox.showinfo("Status", "No files in this project")
            return
        
        existing = 0
        missing = 0
        
        for file_path in files:
            if os.path.exists(file_path):
                existing += 1
            else:
                missing += 1
        
        status_msg = f"Total files: {len(files)}\n"
        status_msg += f"Existing: {existing}\n"
        status_msg += f"Missing: {missing}"
        
        messagebox.showinfo("File Status", status_msg)
        self.update_project_view()
    
    def sync_files(self):
        """Sync files to the output directory"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        project = self.projects[self.current_project]
        output_dir = project.get("output_dir")
        files = project.get("files", [])
        
        if not output_dir:
            messagebox.showwarning("Warning", "Please set an output directory")
            return
        
        if not files:
            messagebox.showwarning("Warning", "No files to sync")
            return
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output directory: {e}")
            return
        
        # Sync files
        synced = 0
        skipped = 0
        errors = []
        
        for file_path in files:
            if not os.path.exists(file_path):
                skipped += 1
                continue
            
            try:
                # Get the filename
                filename = os.path.basename(file_path)
                
                # Handle duplicate filenames by adding parent folder name
                output_file = os.path.join(output_dir, filename)
                if os.path.exists(output_file) and os.path.abspath(file_path) != os.path.abspath(output_file):
                    # Add parent folder to filename to avoid conflicts
                    parent_folder = os.path.basename(os.path.dirname(file_path))
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{parent_folder}{ext}"
                    output_file = os.path.join(output_dir, filename)
                    
                    # If still exists, add a number
                    counter = 1
                    while os.path.exists(output_file) and os.path.abspath(file_path) != os.path.abspath(output_file):
                        filename = f"{name}_{parent_folder}_{counter}{ext}"
                        output_file = os.path.join(output_dir, filename)
                        counter += 1
                
                # Copy the file
                shutil.copy2(file_path, output_file)
                synced += 1
                
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        # Update last sync time
        self.projects[self.current_project]["last_sync"] = datetime.datetime.now().isoformat()
        self.save_projects()
        self.update_project_view()
        
        # Show results
        result_msg = f"Sync completed!\n\n"
        result_msg += f"Files synced: {synced}\n"
        result_msg += f"Files skipped (missing): {skipped}\n"
        
        if errors:
            result_msg += f"\nErrors ({len(errors)}):\n"
            result_msg += "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += f"\n... and {len(errors) - 5} more"
        
        if errors:
            messagebox.showwarning("Sync Completed with Errors", result_msg)
        else:
            messagebox.showinfo("Sync Completed", result_msg)


def main():
    root = tk.Tk()
    app = FileSyncManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
