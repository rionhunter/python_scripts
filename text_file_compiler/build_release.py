"""Helper to produce release zips after building with PyInstaller.

This script is a lightweight wrapper that calls the existing packaging
entry (`build_package.py`) and packages the `dist/` output into a
platform-tagged zip for releases. It intentionally does not run
PyInstaller itself in CI; it's safe to run locally after building.
"""

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def make_release(onefile: bool, output: Path) -> int:
    # Run the local build script which invokes PyInstaller
    build_cmd = [sys.executable, str(ROOT / 'build_package.py')]
    if onefile:
        build_cmd.append('--onefile')

    print('Running:', ' '.join(build_cmd))
    rc = shutil.os.system(' '.join(build_cmd))
    if rc != 0:
        print('Build step returned non-zero exit code:', rc)

    # Collect dist contents
    dist_dir = ROOT / 'dist'
    if not dist_dir.exists():
        print('No dist/ directory found; nothing to package.')
        return 2

    # Make output zip
    output = output or (ROOT / f'release-{sys.platform}.zip')
    print('Creating release zip at', output)
    if output.exists():
        output.unlink()

    shutil.make_archive(str(output.with_suffix('')), 'zip', root_dir=dist_dir)
    print('Release created:', output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Create a release zip after building')
    parser.add_argument('--onefile', action='store_true')
    parser.add_argument('--output', type=Path, help='Output zip path')
    args = parser.parse_args()
    return make_release(args.onefile, args.output)


if __name__ == '__main__':
    raise SystemExit(main())
