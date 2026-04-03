# File Sync Manager

A GUI application for managing persistent project profiles that sync files to a flattened output directory.

## Features

- **Project Management**: Create, rename, and delete project profiles
- **Persistent Storage**: Projects are saved to `file_sync_projects.json`
- **File Selection**: Add individual files or entire folders to projects
- **Flattened Sync**: All selected files are copied to a single output directory (no subdirectories)
- **File Status Tracking**: Check which files exist and which are missing
- **Duplicate Handling**: Automatically renames files with the same name to avoid conflicts
- **Last Sync Timestamp**: Track when each project was last synced

## Usage

1. **Run the application**:
   ```bash
   python file_sync_manager.py
   ```

2. **Create a Project**:
   - Click "New Project" in the left panel
   - Enter a project name
   - Click "Create"

3. **Set Output Directory**:
   - Select your project from the list
   - Click "Browse" next to the Output Directory field
   - Select where you want synced files to be copied

4. **Add Files**:
   - **Add Files**: Select individual files to add to the project
   - **Add Folder**: Add all files from a folder (recursively)
   - Files are listed in the main view with their status (✓ exists or ✗ missing)

5. **Sync Files**:
   - Click "Sync Files" to copy all existing files to the output directory
   - Files are copied with a flattened structure (all in one directory)
   - Duplicate filenames are handled by appending the parent folder name

6. **Check Status**:
   - Click "Check Status" to see how many files exist vs. are missing
   - Status updates automatically when viewing file list

## File Handling

### Duplicate Filenames
When multiple files have the same name, the tool automatically handles conflicts:
1. Appends the parent folder name: `file.txt` → `file_parentfolder.txt`
2. If still duplicate, adds a number: `file_parentfolder_1.txt`

### Missing Files
Files that no longer exist at their original location are marked as "✗ Missing" and are skipped during sync.

## Data Storage

Projects are saved in `file_sync_projects.json` in the same directory as the script. Each project stores:
- Project name
- Output directory path
- List of file paths to sync
- Creation timestamp
- Last sync timestamp

## Example Workflow

1. Create a project called "Work Documents"
2. Set output to `C:\Backup\WorkDocs`
3. Add files from various locations:
   - `C:\Users\You\Documents\report.docx`
   - `C:\Projects\Code\readme.txt`
   - `D:\Archive\notes.txt`
4. Click "Sync Files"
5. All files are now in `C:\Backup\WorkDocs` in a flat structure

## Tips

- Use projects as different "profiles" for different sync needs
- Add entire folders to quickly include many files
- Run "Check Status" before syncing to verify all files still exist
- The last sync timestamp helps you track when files were last updated
