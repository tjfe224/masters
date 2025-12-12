"""
QUICK OCR Error Analyzer - Get Results in seconds
Run this first to get immediate statistics from a select number of sample of files

"""

import os
import re
from collections import Counter
from pathlib import Path

def quick_analyze():
    #Quick analysis of OCR files - returns results immediately
    files_to_analyze = 20
    base_dir = Path(r"G:\2_KDNP_inprocess")
    
    # Find OCR files
    print("Searching for OCR files...")
    ocr_files = list(base_dir.glob('**/*_ocr.txt'))[:files_to_analyze]  # Analyze first 20 files
    
    if not ocr_files:
        print("No OCR files found! Check the directory path.")
        return
    
    print(f"Found {len(ocr_files)} files. Analyzing...\n")
    
    # Track errors
    word_errors = Counter()
    char_errors = Counter()
    total_words = 0
    
    # Common OCR word errors to look for
    error_dict = {
        'tlie': 'the', 'ilie': 'the', 'tbe': 'the', 'tliis': 'this',
        'aud': 'and', 'aad': 'and', 'witli': 'with', 'wliich': 'which',
        'fiom': 'from', 'fiieids': 'friends', 'tbat': 'that',
        'wlien': 'when', 'tliey': 'they', 'liave': 'have',
        'probf': 'proof', 'woifet': 'worst', 'wag': 'was',
        'io': 'to', 'od': 'of', 'liis': 'his', 'lier': 'her'
    }
    
    for filepath in ocr_files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            words = re.findall(r'\b\w+\b', text.lower())
            total_words += len(words)
            
            # Count specific word errors
            for word in words:
                if word in error_dict:
                    word_errors[f"{word} → {error_dict[word]}"] += 1
            
            # Count character patterns
            char_errors['l/1 confusion'] += len(re.findall(r'\bl\d|\d1\b', text))
            char_errors['O/0 confusion'] += len(re.findall(r'\bO\d|\d0[a-z]', text))
            char_errors['rn/m confusion'] += text.count('rn')
            char_errors['Mixed nums/letters'] += len(re.findall(r'\b\w*\d\w*[a-z]\w*|\b\w*[a-z]\w*\d\w*\b', text))
            
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")
    
    # Print results
    print("=" * 70)
    print("Quick OCR Error Analysis Results")
    print("=" * 70)
    print(f"\nFiles analyzed: {len(ocr_files)}")
    print(f"Total words scanned: {total_words:,}")
    print()
    
    print("Top 20 Common Word Errors:")
    print("-" * 70)
    for error, count in word_errors.most_common(20):
        print(f"  {error:<35} {count:>6} occurrences")
    
    print("\n")
    print("Character-Level Error Patterns:")
    print("-" * 70)
    for pattern, count in char_errors.most_common():
        if count > 0:
            print(f"  {pattern:<35} {count:>6} instances")
    
    print("\n" + "=" * 70)
    print("Error Rate Estimate:")
    total_errors = sum(word_errors.values())
    if total_words > 0:
        error_rate = (total_errors / total_words) * 100
        print(f"  Known word-level errors: {total_errors:,}")
        print(f"  Error rate (minimum): {error_rate:.2f}%")
        print(f"  (Actual rate likely 3-5x higher including unknown errors)")
    
    print("\nQuick analysis complete!")
    print("  Run the full analyzer script for comprehensive results.")
    print("=" * 70)


if __name__ == "__main__":
    quick_analyze()
