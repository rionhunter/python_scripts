- [x] make it so the file browser is the dominant component of the GUI, with the list of included documents populating below
- [x] automatic population of directory contents by selecting a directory, with option to exclude any empty documents that might exist
- [x] make the background slightly more opaque
- [x] Remove the title (Text File Compiler) & move the 'Ready', zoom and scale buttons to be after the project options on the bar at the top.

## Emergent Tasks

- [x] Add option to toggle auto-populate on/off for directory selection
- [x] Implement sort/filter options for included documents list
- [x] Add keyboard shortcuts for common operations (Ctrl+N for New Project, Ctrl+S for Save, etc.)
- [x] Display project name above the title bar, hovering outside the frame of the application. add flourish animation where each letter is delayed in movement by a fraction of a second so that they trail and rejoin

## New Emergent Tasks

- [x] Persist auto-populate and filter preferences in settings
- [x] Add explicit project rename action in the top bar

## Further Emergent Tasks

- [x] Ensure compile uses canonical included-files set even when filtered view is active
- [x] Address Qt font deployment warning for offscreen/runtime environments

## Packaging Emergent Tasks

- [x] Add Windows export build workflow using PyInstaller
- [x] Add cross-platform packaging entry point/script