#!/usr/bin/env python3
"""
Text Similarity Tool
Calculate similarity between text files using various metrics
"""

import argparse
import sys
import re
from pathlib import Path
from typing import List, Set, Dict
from collections import Counter


def read_file(filepath: str) -> str:
    """Read file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def tokenize(text: str) -> List[str]:
    """Tokenize text into words."""
    # Simple word tokenization
    return re.findall(r'\b\w+\b', text.lower())


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """
    Calculate Jaccard similarity coefficient.
    
    Args:
        set1: First set
        set2: Second set
        
    Returns:
        Jaccard similarity (0.0 to 1.0)
    """
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def cosine_similarity(vec1: Dict, vec2: Dict) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector (word counts)
        vec2: Second vector (word counts)
        
    Returns:
        Cosine similarity (0.0 to 1.0)
    """
    # Get all words
    all_words = set(vec1.keys()) | set(vec2.keys())
    
    # Calculate dot product
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
    
    # Calculate magnitudes
    magnitude1 = sum(count ** 2 for count in vec1.values()) ** 0.5
    magnitude2 = sum(count ** 2 for count in vec2.values()) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein (edit) distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Calculate normalized Levenshtein similarity.
    
    Returns:
        Similarity (0.0 to 1.0)
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)


def ngram_similarity(text1: str, text2: str, n: int = 3) -> float:
    """
    Calculate n-gram similarity.
    
    Args:
        text1: First text
        text2: Second text
        n: N-gram size
        
    Returns:
        N-gram similarity (0.0 to 1.0)
    """
    def get_ngrams(text: str, n: int) -> Set[str]:
        """Generate n-grams from text."""
        text = text.lower()
        return set(text[i:i+n] for i in range(len(text) - n + 1))
    
    ngrams1 = get_ngrams(text1, n)
    ngrams2 = get_ngrams(text2, n)
    
    return jaccard_similarity(ngrams1, ngrams2)


def word_overlap_similarity(text1: str, text2: str) -> float:
    """
    Calculate word overlap similarity.
    
    Returns:
        Word overlap ratio (0.0 to 1.0)
    """
    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))
    
    return jaccard_similarity(words1, words2)


def compare_files(file1: str, file2: str, method: str = 'all') -> Dict[str, float]:
    """
    Compare two files using various similarity metrics.
    
    Args:
        file1: Path to first file
        file2: Path to second file
        method: Similarity method or 'all'
        
    Returns:
        Dictionary of similarity scores
    """
    text1 = read_file(file1)
    text2 = read_file(file2)
    
    results = {}
    
    if method in ('all', 'word'):
        results['word_overlap'] = word_overlap_similarity(text1, text2)
    
    if method in ('all', 'cosine'):
        words1 = tokenize(text1)
        words2 = tokenize(text2)
        vec1 = Counter(words1)
        vec2 = Counter(words2)
        results['cosine'] = cosine_similarity(vec1, vec2)
    
    if method in ('all', 'ngram'):
        results['ngram_3'] = ngram_similarity(text1, text2, 3)
    
    if method in ('all', 'levenshtein'):
        # For large texts, use line-based comparison
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # Sample lines for efficiency
        sample_size = min(100, len(lines1), len(lines2))
        if len(lines1) > sample_size:
            lines1 = lines1[:sample_size]
        if len(lines2) > sample_size:
            lines2 = lines2[:sample_size]
        
        results['levenshtein'] = levenshtein_similarity(
            '\n'.join(lines1), '\n'.join(lines2)
        )
    
    return results


def batch_compare(files: List[str]) -> Dict:
    """
    Compare multiple files and find most similar pairs.
    
    Args:
        files: List of file paths
        
    Returns:
        Dictionary with comparison results
    """
    results = {}
    
    for i, file1 in enumerate(files):
        for file2 in files[i+1:]:
            pair_key = f"{Path(file1).name} <-> {Path(file2).name}"
            similarity = compare_files(file1, file2, method='word')
            results[pair_key] = similarity['word_overlap']
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Calculate text similarity using various metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.txt file2.txt                    # All metrics
  %(prog)s file1.txt file2.txt -m word            # Word overlap
  %(prog)s file1.txt file2.txt -m cosine          # Cosine similarity
  %(prog)s file1.txt file2.txt -m ngram           # N-gram similarity
  %(prog)s file1.txt file2.txt -m levenshtein     # Edit distance
  %(prog)s file1.txt file2.txt file3.txt --batch  # Compare all pairs
  
Similarity Methods:
  word        - Word overlap (Jaccard similarity)
  cosine      - Cosine similarity of word vectors
  ngram       - Character n-gram similarity
  levenshtein - Normalized edit distance
  all         - All methods (default)
        """
    )
    
    parser.add_argument('files', nargs='+', help='Files to compare')
    parser.add_argument('-m', '--method', default='all',
                        choices=['all', 'word', 'cosine', 'ngram', 'levenshtein'],
                        help='Similarity method (default: all)')
    parser.add_argument('--batch', action='store_true',
                        help='Compare all file pairs')
    parser.add_argument('-t', '--threshold', type=float, default=0.0,
                        help='Only show similarities above threshold (0.0-1.0)')
    parser.add_argument('-s', '--sort', action='store_true',
                        help='Sort results by similarity')
    
    args = parser.parse_args()
    
    try:
        # Check files exist
        for filepath in args.files:
            if not Path(filepath).exists():
                print(f"Error: File not found: {filepath}", file=sys.stderr)
                return 1
        
        if args.batch:
            # Batch comparison
            if len(args.files) < 2:
                print("Error: At least 2 files required for batch comparison", file=sys.stderr)
                return 1
            
            print(f"\nComparing {len(args.files)} files...\n")
            results = batch_compare(args.files)
            
            # Filter by threshold
            filtered = {k: v for k, v in results.items() if v >= args.threshold}
            
            # Sort if requested
            if args.sort:
                filtered = dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True))
            
            print(f"{'File Pair':<60} {'Similarity':>10}")
            print("-" * 72)
            
            for pair, similarity in filtered.items():
                print(f"{pair:<60} {similarity:>9.2%}")
            
            if filtered:
                avg_similarity = sum(filtered.values()) / len(filtered)
                print(f"\nAverage similarity: {avg_similarity:.2%}")
        
        else:
            # Pairwise comparison
            if len(args.files) != 2:
                print("Error: Exactly 2 files required for pairwise comparison", file=sys.stderr)
                print("Use --batch for comparing multiple files", file=sys.stderr)
                return 1
            
            file1, file2 = args.files
            results = compare_files(file1, file2, args.method)
            
            print(f"\nSimilarity between:")
            print(f"  {Path(file1).name}")
            print(f"  {Path(file2).name}")
            print()
            
            for metric, score in results.items():
                if score >= args.threshold:
                    metric_name = metric.replace('_', ' ').title()
                    print(f"  {metric_name:<20} {score:>8.2%}")
            
            if not any(score >= args.threshold for score in results.values()):
                print(f"  No similarities above threshold {args.threshold:.2%}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
