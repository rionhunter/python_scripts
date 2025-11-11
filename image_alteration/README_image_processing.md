# Image Processing Scripts

This folder contains a comprehensive set of scripts for handling image files, converting between formats, and applying filters.

## Scripts Overview

### 1. `raw_converter.py`
Converts RAW image files to common formats (JPEG, PNG, TIFF, WEBP).

**Features:**
- Support for major RAW formats (ARW, CR2, CR3, DNG, NEF, ORF, RAF, RW2, PEF, SRW)
- Single file and batch conversion
- Quality control for JPEG/WEBP output
- GUI and command-line interfaces

**Usage:**
```bash
# GUI mode
python raw_converter.py

# Command-line mode
python raw_converter.py input_file.arw
```

### 2. `image_converter.py`
Converts between common image formats with format-specific optimizations.

**Features:**
- Support for JPEG, PNG, TIFF, WEBP, BMP, GIF, ICO formats
- Automatic transparency handling
- Quality settings for lossy formats
- ICO multi-size support
- Batch folder processing

**Usage:**
```bash
# GUI mode
python image_converter.py

# Command-line mode
python image_converter.py input.png JPEG output.jpg
```

### 3. `image_filter_system.py`
Create, save, and apply custom filters to images.

**Features:**
- Built-in filter presets (Vintage, Sepia, Grayscale, etc.)
- Custom filter creation with adjustable parameters
- Filter saving/loading system
- Batch filter application
- Real-time preview

**Built-in Filters:**
- **Enhancement**: Brightness, contrast, saturation, sharpness
- **Artistic**: Sepia, grayscale, vintage effect
- **Color**: Cool/warm tone adjustments, color balance
- **Effects**: Blur, vignette, emboss, edge enhancement

**Usage:**
```bash
python image_filter_system.py
```

### 4. `batch_image_processor.py`
Central script for complex batch processing workflows.

**Features:**
- Chain multiple operations (RAW conversion → format conversion → filtering)
- Operation ordering and management
- Progress tracking
- Configuration save/load
- Command-line and GUI modes

**Usage:**
```bash
# GUI mode
python batch_image_processor.py

# Command-line mode
python batch_image_processor.py input_folder output_folder --convert-raw JPEG --filter Vintage --quality 90
```

## Installation Requirements

Install required dependencies:

```bash
pip install Pillow rawpy imageio numpy tkinter
```

**Note**: `tkinter` is usually included with Python installations.

## File Processing Workflow

### Basic Workflow:
1. **RAW Conversion** (if needed) → **Format Conversion** (if needed) → **Filter Application**

### Example Workflows:

**Workflow 1: RAW to Instagram-ready JPEG**
```
RAW file → JPEG conversion (quality 95) → Vintage filter → Final output
```

**Workflow 2: Batch photo enhancement**
```
Mixed formats → PNG conversion → Brightness/contrast enhancement → Output
```

**Workflow 3: Web optimization**
```
Large images → WEBP conversion (quality 85) → Slight sharpening → Web-ready files
```

## GUI Features

### Raw Converter GUI:
- File/folder selection
- Format and quality settings
- Progress tracking
- Batch results display

### Image Converter GUI:
- Format-specific options (ICO sizes, quality settings)
- Preview capabilities
- Batch processing with progress

### Filter System GUI:
- **Filter Editor Tab**: Create and test custom filters with real-time preview
- **Batch Processing Tab**: Apply filters to entire folders
- Filter presets library
- Parameter adjustment sliders

### Batch Processor GUI:
- Operation chain builder
- Drag-and-drop operation ordering
- Comprehensive progress tracking
- Detailed results logging

## Command-Line Usage

### Batch Processor with Config File:

Create a configuration file `workflow.json`:
```json
{
  "operations": [
    {
      "type": "convert_raw",
      "format": "JPEG",
      "quality": 95
    },
    {
      "type": "apply_filter",
      "filter": "Vintage"
    }
  ]
}
```

Run with config:
```bash
python batch_image_processor.py input_folder output_folder --config workflow.json
```

## Filter Configuration

### Custom Filter Example:
```json
{
  "type": "composite",
  "filters": [
    {
      "type": "enhance",
      "brightness": 1.1,
      "contrast": 1.2,
      "color": 0.9
    },
    {
      "type": "vignette",
      "strength": 0.3
    }
  ]
}
```

### Available Filter Types:
- `enhance`: Brightness, contrast, color, sharpness
- `blur`: Gaussian blur with radius control
- `grayscale`: Convert to grayscale
- `sepia`: Sepia tone effect
- `color_balance`: RGB channel adjustment
- `filter`: PIL built-in filters (EDGE_ENHANCE, EMBOSS, etc.)
- `vignette`: Darkened edges effect
- `composite`: Chain multiple filters

## Performance Tips

1. **RAW Processing**: RAW conversion is CPU-intensive. Consider processing in smaller batches.

2. **Memory Usage**: Large images consume significant memory. Close other applications for big batch jobs.

3. **Quality Settings**: 
   - JPEG: 85-95 for high quality, 70-84 for web use
   - WEBP: Generally 10-15% smaller than JPEG at same quality

4. **Batch Processing**: Use the batch processor for complex workflows to avoid intermediate file creation.

## Troubleshooting

### Common Issues:

**"Module not found" errors:**
- Install required packages: `pip install Pillow rawpy imageio numpy`

**RAW files not recognized:**
- Ensure `rawpy` is installed and file extension is supported
- Check if file is corrupted by opening in another RAW processor

**Memory errors with large batches:**
- Process smaller batches
- Reduce image size before applying filters
- Close other applications

**Filter preview not updating:**
- Click "Preview" button after parameter changes
- Ensure image is loaded before applying filters

### File Format Support:

**Input Formats:**
- RAW: ARW, CR2, CR3, DNG, NEF, ORF, RAF, RW2, PEF, SRW
- Standard: JPEG, PNG, TIFF, WEBP, BMP, GIF, ICO

**Output Formats:**
- All standard formats with optimized settings
- ICO with multiple size support
- Quality control for lossy formats

## Integration with Other Scripts

These scripts are designed to work with the existing image processing tools in this folder:

- `cropper.py`: Crop images before processing
- `image_scale_reducer.py`: Resize before conversion
- `png_to_ico_converter.py`: Specialized ICO conversion
- Other image manipulation scripts

## License

These scripts are part of the python_scripts collection and follow the same licensing terms as the parent project.