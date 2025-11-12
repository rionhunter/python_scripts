# Text Comparison Tools

Tools for comparing text files, showing differences, and calculating similarity scores.

## Tools

### 1. Diff Tool (`diff_tool.py`)

Compare files and show differences in various formats.

**Features:**
- Multiple diff formats (unified, context, HTML, side-by-side)
- Diff statistics
- Similarity scoring
- Customizable context lines
- HTML output for visual comparison

**Usage:**

```bash
# Unified diff (default)
python diff_tool.py file1.txt file2.txt

# Context diff
python diff_tool.py file1.txt file2.txt -f context

# HTML side-by-side diff
python diff_tool.py file1.txt file2.txt -f html -o diff.html

# Text side-by-side
python diff_tool.py file1.txt file2.txt -f side

# Show statistics
python diff_tool.py file1.txt file2.txt --stats

# Show similarity score
python diff_tool.py file1.txt file2.txt --similarity

# Combined stats and similarity
python diff_tool.py file1.txt file2.txt --stats --similarity

# Check if files differ (quiet mode)
python diff_tool.py file1.txt file2.txt --quiet
echo $?  # 0 if identical, 1 if different
```

### 2. Similarity Tool (`similarity_tool.py`)

Calculate text similarity using multiple metrics.

**Features:**
- Multiple similarity metrics
- Word overlap (Jaccard similarity)
- Cosine similarity
- N-gram similarity
- Levenshtein (edit) distance
- Batch comparison of multiple files

**Usage:**

```bash
# All similarity metrics
python similarity_tool.py file1.txt file2.txt

# Word overlap only
python similarity_tool.py file1.txt file2.txt -m word

# Cosine similarity
python similarity_tool.py file1.txt file2.txt -m cosine

# N-gram similarity
python similarity_tool.py file1.txt file2.txt -m ngram

# Compare multiple files (all pairs)
python similarity_tool.py file1.txt file2.txt file3.txt --batch

# Filter by threshold (only show >50% similar)
python similarity_tool.py file1.txt file2.txt -t 0.5

# Sort results by similarity
python similarity_tool.py *.txt --batch --sort
```

## Similarity Metrics

### Word Overlap (Jaccard Similarity)
- Compares unique words in both texts
- Fast and simple
- Good for general text comparison
- Range: 0% (no common words) to 100% (identical word sets)

### Cosine Similarity
- Compares word frequency vectors
- Considers word importance
- Better for longer documents
- Range: 0% (completely different) to 100% (identical)

### N-gram Similarity
- Compares character sequences (default: 3 characters)
- Catches spelling variations
- Good for fuzzy matching
- Range: 0% to 100%

### Levenshtein Distance
- Measures edit distance (insertions, deletions, substitutions)
- Precise character-level comparison
- Good for finding typos
- Range: 0% (completely different) to 100% (identical)

## Examples

### Compare Code Versions

```bash
# Show what changed
python diff_tool.py old_version.py new_version.py

# Get statistics
python diff_tool.py old_version.py new_version.py --stats
# Output:
#   Lines in file 1: 150
#   Lines in file 2: 165
#   Unchanged:       120
#   Changed:         20
#   Added:           15
#   Removed:         10
```

### Find Similar Documents

```bash
# Compare all documents in directory
python similarity_tool.py documents/*.txt --batch --sort

# Find duplicates (>90% similar)
python similarity_tool.py documents/*.txt --batch -t 0.9
```

### Visual HTML Diff

```bash
# Create HTML report
python diff_tool.py original.html modified.html -f html -o comparison.html
# Open comparison.html in browser for side-by-side view
```

### Check for Plagiarism

```bash
# Compare student submissions
python similarity_tool.py submission1.txt submission2.txt -m cosine
```

### Merge Conflict Analysis

```bash
# See differences before merging
python diff_tool.py branch1/file.txt branch2/file.txt --stats
```

## Use Cases

### Development
- Code reviews
- Merge conflict analysis
- Version comparison
- Change tracking

### Content Management
- Document versioning
- Plagiarism detection
- Duplicate detection
- Content similarity

### Data Processing
- File deduplication
- Text clustering
- Quality assurance
- Change detection

## Tips

1. **Large Files**: Use `--stats` for quick overview without full diff
2. **Visual Comparison**: Use HTML format for easier reading
3. **Batch Processing**: Use similarity tool with `--batch` for multiple files
4. **Threshold**: Set threshold to filter out dissimilar files
5. **Sorting**: Use `--sort` to find most similar pairs first

## Output Examples

### Diff Statistics Output
```
Diff Statistics:
  Lines in file 1: 100
  Lines in file 2: 105
  Unchanged:       85
  Changed:         10
  Added:           5
  Removed:         0

Similarity: 91.23%
```

### Similarity Tool Output
```
Similarity between:
  document1.txt
  document2.txt

  Word Overlap         85.50%
  Cosine              91.23%
  Ngram 3             88.75%
  Levenshtein         82.34%
```

### Batch Comparison Output
```
Comparing 5 files...

File Pair                                                    Similarity
------------------------------------------------------------------------
doc1.txt <-> doc2.txt                                            95.5%
doc1.txt <-> doc3.txt                                            42.3%
doc2.txt <-> doc3.txt                                            38.7%

Average similarity: 58.83%
```

## Dependencies

- Standard library only: `difflib`, `re`, `collections`
- No external dependencies required

## Advanced Usage

### Script Integration

```bash
#!/bin/bash
# Check if files differ before processing
if python diff_tool.py file1.txt file2.txt --quiet; then
    echo "Files are identical, skipping..."
else
    echo "Files differ, processing..."
    # Do something
fi
```

### Find Duplicate Files

```bash
# Find documents with >95% similarity
python similarity_tool.py documents/*.txt --batch -t 0.95 --sort > duplicates.txt
```

### Generate Diff Report

```bash
# Create comprehensive diff report
{
    echo "=== Diff Statistics ==="
    python diff_tool.py old.txt new.txt --stats
    echo ""
    echo "=== Detailed Differences ==="
    python diff_tool.py old.txt new.txt
} > report.txt
```

## Exit Codes

**diff_tool.py:**
- 0: Files are identical
- 1: Files differ
- 2: Error occurred

**similarity_tool.py:**
- 0: Success
- 1: Error occurred
