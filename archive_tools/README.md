# Archive Tools

Comprehensive archive management utilities for creating, extracting, and managing ZIP and TAR archives.

## Features

- **Create Archives**: ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ
- **Extract Archives**: All common formats with auto-detection
- **List Contents**: View files and compression statistics
- **Batch Operations**: Archive multiple directories at once
- **Password Protection**: Support for encrypted ZIP files
- **Large File Support**: Efficient handling of large archives

## Usage

### Archive Tool (`archive_tool.py`)

#### Create Archives

```bash
# Create ZIP archive
python archive_tool.py -c file.txt -o archive.zip

# Create ZIP from directory
python archive_tool.py -c my_directory/ -o archive.zip

# Create TAR.GZ archive
python archive_tool.py -c directory/ -o archive.tar.gz --tar

# Create TAR.BZ2 archive
python archive_tool.py -c directory/ -o archive.tar.bz2 --tar --compression bz2

# Auto-generate output name
python archive_tool.py -c my_project/
# Creates: my_project.zip
```

#### Extract Archives

```bash
# Extract ZIP archive
python archive_tool.py -x archive.zip -o output_directory/

# Extract to current directory
python archive_tool.py -x archive.zip -o .

# Extract TAR archive (auto-detected)
python archive_tool.py -x archive.tar.gz -o output_directory/

# Extract password-protected ZIP
python archive_tool.py -x secure.zip -o output/ -p mypassword
```

#### List Contents

```bash
# List ZIP contents
python archive_tool.py -l archive.zip

# List TAR contents
python archive_tool.py -l archive.tar.gz --tar

# Output shows:
# - File names
# - Original sizes
# - Compressed sizes (ZIP)
# - Compression ratio
```

#### Batch Operations

```bash
# Create individual archives for each item in directory
python archive_tool.py --batch source_dir/ -o archives_dir/

# Batch with TAR format
python archive_tool.py --batch source_dir/ -o archives_dir/ --tar
```

## Examples

### Backup Important Files
```bash
# Create compressed backup
python archive_tool.py -c ~/Documents/important/ -o backup_$(date +%Y%m%d).tar.gz --tar

# Extract backup
python archive_tool.py -x backup_20231215.tar.gz -o ~/restore/
```

### Archive Each Project
```bash
# Create separate archives for each project
python archive_tool.py --batch ~/projects/ -o ~/archives/
```

### Inspect Archive
```bash
# View what's inside without extracting
python archive_tool.py -l download.zip
```

### Password-Protected Archive
```bash
# Note: Creating password-protected ZIP requires additional setup
# Extract password-protected ZIP
python archive_tool.py -x secure.zip -o output/ -p "my_password"
```

## Compression Methods

### ZIP
- **Deflate**: Standard compression (default)
- Good balance of speed and compression
- Universal compatibility

### TAR
- **none**: No compression
- **gz**: Gzip (default) - fast, good compression
- **bz2**: Bzip2 - slower, better compression
- **xz**: XZ/LZMA - slowest, best compression

## Tips

1. **Large Files**: Use TAR with XZ compression for best space savings
2. **Speed**: Use ZIP or TAR.GZ for faster operations
3. **Compatibility**: Use ZIP for Windows compatibility
4. **Backups**: Use TAR.GZ for Unix/Linux backups
5. **Batch**: Archive multiple directories efficiently with `--batch`

## Common Use Cases

### Website Backup
```bash
python archive_tool.py -c /var/www/mysite/ -o mysite_backup.tar.gz --tar
```

### Source Code Archive
```bash
python archive_tool.py -c my_project/ -o my_project_v1.0.zip
```

### Log File Compression
```bash
python archive_tool.py -c /var/log/ -o logs_archive.tar.xz --tar --compression xz
```

### Extract Download
```bash
python archive_tool.py -x download.zip -o ./extracted/
```

## Dependencies

- Standard library only: `zipfile`, `tarfile`, `shutil`, `pathlib`
- No external dependencies required

## Supported Formats

**Read/Write:**
- ZIP (.zip)
- TAR (.tar)
- TAR+GZIP (.tar.gz, .tgz)
- TAR+BZIP2 (.tar.bz2, .tbz2)
- TAR+XZ (.tar.xz)

**Note**: 7Z format requires external `py7zr` library (not included by default)
