"""
OCR Error Pattern Analyzer for Historical Newspaper Digitization
University of Kentucky Master's Project
Analyzes OCR output files to identify common error patterns and generate statistics
"""

import os
import re
from collections import Counter, defaultdict
import json
from pathlib import Path
from datetime import datetime

class OCRErrorAnalyzer:
    def __init__(self, base_directory):
        self.base_directory = Path(base_directory)
        self.results = {
            'files_analyzed': 0,
            'total_words': 0,
            'total_characters': 0,
            'character_substitutions': Counter(),
            'common_word_errors': Counter(),
            'suspicious_patterns': defaultdict(int),
            'files_by_era': {},
            'statistics': {}
        }
        
        # Common OCR character confusions
        self.char_confusion_pairs = [
            ('l', '1'), ('I', '1'), ('O', '0'), ('S', '5'),
            ('rn', 'm'), ('cl', 'd'), ('nn', 'm'), ('vv', 'w'),
            ('li', 'h'), ('tl', 'd'), ('ii', 'u')
        ]
        
        # Load English dictionary for validation
        self.load_common_words()
    
    def load_common_words(self):
        """Load common English words for validation"""
        # Top 10,000 most common English words
        common_words_text = """the of and to a in is it you that he was for on are with as I his they be at one have this from or had by hot word but what some we can out other were all there when up use your how said an each she which do their time if will way about many then them write would like so these her long make thing see him two has look more day could go come did number sound no most people my over know water than call who oil its now find he may down side been now any new work part take get place made live where after back little only round man year came show every good me give our under name very through just form sentence great think say help low line differ turn cause much mean before move right boy old too same tell does set three want air well also play small end put home read hand port large spell add even land here must big high such follow act why ask men change went light kind off need house picture try us again animal point mother world near build self earth father any new work part take"""
        
        self.common_words = set(common_words_text.lower().split())
    
    def extract_year_from_filename(self, filename):
        """Extract year from filename like 'kea1828012501_ocr.txt'"""
        match = re.search(r'(\d{4})', filename)
        if match:
            return int(match.group(1))
        return None
    
    def categorize_by_era(self, year):
        """Categorize files by historical era"""
        if year < 1850:
            return "Early 19th Century (1800-1849)"
        elif year < 1900:
            return "Late 19th Century (1850-1899)"
        elif year < 1950:
            return "Early 20th Century (1900-1949)"
        else:
            return "Mid-Late 20th Century (1950-1989)"
    
    def detect_common_errors(self, text):
        """Detect common OCR error patterns"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            # Check for likely OCR errors
            if len(word) > 2:
                # Words with mixed numbers and letters (likely errors)
                if re.search(r'\d+[a-z]+|\[a-z]+\d+', word):
                    self.results['suspicious_patterns']['mixed_nums_letters'] += 1
                
                # Common specific errors
                common_errors = {
                    'tlie': 'the',
                    'ilie': 'the',
                    'tbe': 'the',
                    'tbat': 'that',
                    'aud': 'and',
                    'aad': 'and',
                    'fiom': 'from',
                    'witli': 'with',
                    'wliich': 'which',
                    'wlien': 'when',
                    'tliis': 'this',
                    'wliite': 'white',
                    'tliey': 'they',
                    'tliese': 'these',
                    'tliose': 'those',
                    'tlie': 'the',
                    'liis': 'his',
                    'lier': 'her',
                    'liave': 'have',
                    'liad': 'had',
                    'fiieids': 'friends',
                    'firiend': 'friend',
                    'tbserved': 'observed',
                    'loubted': 'doubted',
                    'probf': 'proof',
                    'woifet': 'worst',
                    'ruong': 'wrong',
                    'wag': 'was',
                    'io': 'to',
                    'al': 'at',
                    'od': 'of'
                }
                
                if word in common_errors:
                    self.results['common_word_errors'][f"{word} → {common_errors[word]}"] += 1
                
                # Check for double letters that should be single
                if re.search(r'(.)\1{2,}', word):
                    self.results['suspicious_patterns']['repeated_chars'] += 1
                
                # Non-dictionary words (potential errors)
                if word not in self.common_words and len(word) > 3:
                    if not re.search(r'\d', word):  # Exclude numbers
                        self.results['suspicious_patterns']['non_dict_words'] += 1
        
        return words
    
    def analyze_character_patterns(self, text):
        """Analyze character-level patterns for substitutions"""
        # Look for common confusion patterns
        for wrong, correct in self.char_confusion_pairs:
            pattern = re.compile(re.escape(wrong))
            matches = pattern.findall(text)
            if matches:
                self.results['character_substitutions'][f"{wrong} → {correct}"] += len(matches)
        
        # Specific patterns
        if re.search(r'\bAI[a-z]', text):  # "AI" instead of "M" (e.g., "AIr.")
            self.results['character_substitutions']['AI* → Mr.'] += len(re.findall(r'\bAI[a-z]', text))
        
        if re.search(r'\b[A-Z]1[a-z]', text):  # Number 1 instead of letter I
            self.results['character_substitutions']['1 → I (uppercase)'] += len(re.findall(r'\b[A-Z]1[a-z]', text))
    
    def analyze_file(self, filepath):
        """Analyze a single OCR file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract year and categorize
            filename = os.path.basename(filepath)
            year = self.extract_year_from_filename(filename)
            
            if year:
                era = self.categorize_by_era(year)
                if era not in self.results['files_by_era']:
                    self.results['files_by_era'][era] = []
                self.results['files_by_era'][era].append({
                    'filename': filename,
                    'year': year,
                    'path': str(filepath)
                })
            
            # Basic statistics
            words = self.detect_common_errors(content)
            self.results['total_words'] += len(words)
            self.results['total_characters'] += len(content)
            self.results['files_analyzed'] += 1
            
            # Character-level analysis
            self.analyze_character_patterns(content)
            
            return True
        
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
            return False
    
    def scan_directory(self, max_files=None):
        """Scan directory for OCR files"""
        print(f"Scanning directory: {self.base_directory}")
        ocr_files = list(self.base_directory.glob('**/*_ocr.txt'))
        
        if max_files:
            ocr_files = ocr_files[:max_files]
        
        print(f"Found {len(ocr_files)} OCR files")
        
        for idx, filepath in enumerate(ocr_files, 1):
            if idx % 10 == 0:
                print(f"Processed {idx}/{len(ocr_files)} files...")
            self.analyze_file(filepath)
        
        print(f"Analysis complete! Processed {self.results['files_analyzed']} files")
    
    def calculate_statistics(self):
        """Calculate summary statistics"""
        self.results['statistics'] = {
            'avg_words_per_file': self.results['total_words'] / max(self.results['files_analyzed'], 1),
            'avg_chars_per_file': self.results['total_characters'] / max(self.results['files_analyzed'], 1),
            'total_error_patterns': sum(self.results['common_word_errors'].values()),
            'total_char_substitutions': sum(self.results['character_substitutions'].values()),
            'total_suspicious_patterns': sum(self.results['suspicious_patterns'].values())
        }
    
    def generate_report(self, output_file='ocr_analysis_report.txt'):
        """Generate a comprehensive text report"""
        self.calculate_statistics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("OCR ERROR ANALYSIS REPORT\n")
            f.write("University of Kentucky Historical Newspaper Digitization Project\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary Statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total files analyzed: {self.results['files_analyzed']}\n")
            f.write(f"Total words processed: {self.results['total_words']:,}\n")
            f.write(f"Total characters: {self.results['total_characters']:,}\n")
            f.write(f"Average words per file: {self.results['statistics']['avg_words_per_file']:.1f}\n")
            f.write(f"Total error patterns found: {self.results['statistics']['total_error_patterns']:,}\n")
            f.write(f"Total character substitutions: {self.results['statistics']['total_char_substitutions']:,}\n\n")
            
            # Files by Era
            f.write("FILES BY HISTORICAL ERA\n")
            f.write("-" * 80 + "\n")
            for era in sorted(self.results['files_by_era'].keys()):
                files = self.results['files_by_era'][era]
                f.write(f"{era}: {len(files)} files\n")
            f.write("\n")
            
            # Common Word Errors (Top 50)
            f.write("TOP 50 COMMON WORD-LEVEL OCR ERRORS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Error Pattern':<30} {'Frequency':>15}\n")
            f.write("-" * 80 + "\n")
            for error, count in self.results['common_word_errors'].most_common(50):
                f.write(f"{error:<30} {count:>15,}\n")
            f.write("\n")
            
            # Character Substitution Patterns
            f.write("CHARACTER SUBSTITUTION PATTERNS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Pattern':<30} {'Frequency':>15}\n")
            f.write("-" * 80 + "\n")
            for pattern, count in self.results['character_substitutions'].most_common(30):
                f.write(f"{pattern:<30} {count:>15,}\n")
            f.write("\n")
            
            # Suspicious Patterns
            f.write("SUSPICIOUS PATTERN COUNTS\n")
            f.write("-" * 80 + "\n")
            for pattern, count in sorted(self.results['suspicious_patterns'].items()):
                f.write(f"{pattern:<30} {count:>15,}\n")
            f.write("\n")
        
        print(f"\nReport saved to: {output_file}")
    
    def export_json(self, output_file='ocr_analysis_data.json'):
        """Export raw data as JSON for further processing"""
        # Convert Counter objects to regular dicts
        export_data = {
            'files_analyzed': self.results['files_analyzed'],
            'total_words': self.results['total_words'],
            'total_characters': self.results['total_characters'],
            'character_substitutions': dict(self.results['character_substitutions'].most_common(100)),
            'common_word_errors': dict(self.results['common_word_errors'].most_common(100)),
            'suspicious_patterns': dict(self.results['suspicious_patterns']),
            'files_by_era': self.results['files_by_era'],
            'statistics': self.results['statistics']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"JSON data exported to: {output_file}")


def main():
    """Main execution function"""
    # Configuration
    BASE_DIR = r"G:\2_KDNP_inprocess"  # Modify this path as needed
    MAX_FILES = None  # Set to a number to limit files, or None for all files
    
    print("=" * 80)
    print("OCR ERROR PATTERN ANALYZER")
    print("University of Kentucky Historical Newspaper Digitization Project")
    print("=" * 80)
    print()
    
    # Create analyzer instance
    analyzer = OCRErrorAnalyzer(BASE_DIR)
    
    # Scan and analyze files
    analyzer.scan_directory(max_files=MAX_FILES)
    
    # Generate outputs
    print("\nGenerating reports...")
    analyzer.generate_report('ocr_analysis_report.txt')
    analyzer.export_json('ocr_analysis_data.json')
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nOutputs generated:")
    print("  1. ocr_analysis_report.txt - Human-readable detailed report")
    print("  2. ocr_analysis_data.json - Machine-readable data for further processing")
    print("\nNext steps:")
    print("  - Review the report to identify top error patterns")
    print("  - Use the JSON data for building correction algorithms")
    print("  - Create visualizations of error frequencies by era")
    print()


if __name__ == "__main__":
    main()