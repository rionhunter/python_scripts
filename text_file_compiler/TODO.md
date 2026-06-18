# TODO

- [x] Have title animation based on window dragging - with letters having offset delay of motion to manage trailing animation. Align to left side of window
- [x] right click release should not trigger default right click menu if the window has been dragged using right click
- [x] Overhaul GUI ratios and placements
	- [x] Reconfigure file browser into a collapsible file tree with checkboxes next to both files and directories.
	- [x] Remove the 'Included Documents' Section
	- [x] Remove the 'add file', 'move' and 'clear all' buttons (partially done: add/clear removed)
	- [x] have main work space (project tree, compile order, output) expand to take the maximum vertical space.
	- [x] Create settings button that opens settings panel, move checkbox options from gui into there.
	- [x] add a column in between the file tree and the output, where the user can arrange the order of the files with both drag and drop, multiple selection, buttons to change index. By default, compile in order of user selection. By default specified in the settings, selecting a directory will include sub-directory contents, and when porting them into output, ensure it's by logical numerical/alphabetical order first, before the user makes their own changes if desired.
	- [x] update project contents to include order of selected files/settings, etc
- [ ] Add GitHub Actions release artifacts for Windows/macOS/Linux
- [ ] [pending on icon design] Add app icon + metadata resources for packaged binaries

## Work in progress

- [ ] Add GitHub Actions release artifacts for Windows/macOS/Linux (in-progress: workflow added)
- [ ] Add app icon + metadata resources for packaged binaries
 
## Emergent extrapolations

- [ ] Add packaging config for PyInstaller and platform-specific metadata
- [ ] Add README section describing release artifact contents and basics for manual packaging
- [ ] Create .github/workflows/release.yml skeleton for release artifacts
- [ ] Add packaging scripts (build_release.py / build_package.py integration)
- [ ] Add cross-platform icon files: resources/icons/app.ico (Windows), resources/icons/app.icns (macOS), and Linux PNGs

## Emergent extrapolations

- [ ] Add packaging config for PyInstaller and platform-specific metadata
- [ ] Add README section describing release artifact contents and basics for manual packaging


## Emergent follow-ups

	- [x] Add checkbox-based selection directly in the file tree (single source of truth), replacing double-click-to-add behavior.
	- [x] Add dedicated "compile order" column with multi-select, drag/drop, and up/down index controls.
	- [ ] Add GUI-focused tests for right-click drag behavior, settings persistence, and manual file reordering.

- [ ] Add CI badge to README reflecting main branch build/status

- [ ] Remove duplicate ID labels in file tree file entries - show filename only once (currently duplicated)

- [x] [CRITICAL] ensure file tree entries can be toggled to be included in the compile order

- [ ] remove minimize and close button (poor formatting, esc key dedicated anyway)
