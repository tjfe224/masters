"""
Comprehensive OCR Error Analysis System - FULL DRIVE SCAN
University of Kentucky Master's Project - Complete Dataset Analysis

Analyzes ALL OCR files across the ENTIRE G:\ drive
Includes: 2_KDNP_inprocess, 3_KDNP_Ready, 4_Archival-Packages_Ready, and all subdirectories
"""

import os
import re
from collections import Counter, defaultdict
from pathlib import Path
import json
from datetime import datetime
import statistics

class ComprehensiveOCRAnalyzer:
    def __init__(self, base_directory="G:\\"):
        """
        Initialize analyzer to scan entire drive
        
        Args:
            base_directory: Root directory to scan (default: G:\)
        """
        self.base_dir = Path(base_directory)
        
        # Directories to exclude (system/temp folders)
        self.exclude_dirs = {
            '$RECYCLE.BIN', 'System Volume Information', 
            '.Spotlight-V100', 'Thumbs.db', '.DS_Store'
        }
        
        self.results = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'base_directory': str(self.base_dir),
                'directories_scanned': [],
                'total_files': 0,
                'total_words': 0,
                'total_characters': 0
            },
            'error_patterns': {
                'character_substitutions': Counter(),
                'word_level_errors': Counter(),
                'suspicious_patterns': defaultdict(int)
            },
            'by_era': {},
            'by_resolution': defaultdict(lambda: {'files': 0, 'errors': 0, 'words': 0}),
            'by_directory': defaultdict(lambda: {'files': 0, 'words': 0, 'errors': 0}),
            'by_newspaper': defaultdict(lambda: {'files': 0, 'years': set(), 'errors': Counter()}),
            'statistics': {}
        }
        
        # Expanded error patterns
        self.char_confusion_pairs = [
            ('l', '1'), ('I', '1'), ('O', '0'), ('S', '5'), ('Z', '2'),
            ('rn', 'm'), ('cl', 'd'), ('nn', 'm'), ('li', 'h'), ('tl', 'd'),
            ('ii', 'u'), ('vv', 'w'), ('ﬁ', 'fi'), ('ﬂ', 'fl')
        ]
        
        self.word_error_dict = {
            # th- errors
            'tbe': 'the', 'tlie': 'the', 'ilie': 'the', 'tho': 'the',
            'tliat': 'that', 'tbat': 'that', 'tliis': 'this', 'tliese': 'these',
            'tliey': 'they', 'tlien': 'then', 'tliere': 'there', 'tliem': 'them',
            'tliose': 'those', 'tliree': 'three', 'tlian': 'than', 'tlius': 'thus',
            'tlirough': 'through',
            
            # wh- errors
            'wliich': 'which', 'wlien': 'when', 'wliere': 'where', 'wlio': 'who',
            'wliite': 'white', 'wliile': 'while', 'wliole': 'whole', 'wliat': 'what',
            'wliy': 'why',
            
            # and/or errors
            'aud': 'and', 'aad': 'and', 'aiid': 'and', 'arid': 'and',
            'witli': 'with', 'witb': 'with', 'wltli': 'with',
            'fiom': 'from', 'frorn': 'from', 'fro': 'from',
            
            # h- errors
            'liave': 'have', 'liad': 'had', 'liis': 'his', 'lier': 'her',
            'liim': 'him', 'liow': 'how', 'liere': 'here', 'liand': 'hand',
            'liouse': 'house', 'lieart': 'heart', 'liead': 'head', 'liigh': 'high',
            
            # common words
            'wag': 'was', 'io': 'to', 'od': 'of', 'iu': 'in', 'oue': 'one',
            'cau': 'can', 'owu': 'own', 'uow': 'now', 'ouly': 'only',
            'iustead': 'instead', 'upou': 'upon', 'rnan': 'man', 'raen': 'men',
            'rnore': 'more', 'rnust': 'must', 'rnake': 'make', 'rnany': 'many',
            'tirne': 'time', 'sorne': 'some', 'corne': 'come', 'becorne': 'become',
            'horne': 'home', 'narne': 'name', 'sarne': 'same'
        }
    
    def should_skip_directory(self, dir_path):
        """Check if directory should be skipped"""
        dir_name = dir_path.name
        return dir_name in self.exclude_dirs or dir_name.startswith('.')
    
    def extract_metadata(self, filepath):
        """Extract metadata from filename and path"""
        filename = filepath.name
        path_str = str(filepath)
        
        # Extract year
        year_match = re.search(r'(\d{4})', filename)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract newspaper code (first 3 letters typically)
        paper_match = re.search(r'([a-z]{3})', filename.lower())
        newspaper_code = paper_match.group(1) if paper_match else 'unknown'
        
        # Detect resolution from path
        resolution = None
        if '150dpi' in path_str.lower():
            resolution = 150
        elif '300dpi' in path_str.lower():
            resolution = 300
        elif '400dpi' in path_str.lower():
            resolution = 400
        elif '600dpi' in path_str.lower():
            resolution = 600
        
        # Determine processing stage from directory
        stage = 'unknown'
        if 'inprocess' in path_str.lower():
            stage = 'in_process'
        elif 'ready' in path_str.lower():
            stage = 'ready'
        elif 'archival' in path_str.lower():
            stage = 'archived'
        elif 'batch' in path_str.lower():
            stage = 'batch'
        
        # Extract parent directory for grouping
        parent_dir = None
        if '2_KDNP_inprocess' in path_str:
            parent_dir = '2_KDNP_inprocess'
        elif '3_KDNP_Ready' in path_str:
            parent_dir = '3_KDNP_Ready'
        elif '4_Archival-Packages_Ready' in path_str:
            parent_dir = '4_Archival-Packages_Ready'
        elif '7_NDNP_Batch' in path_str:
            parent_dir = '7_NDNP_Batch'
        else:
            parent_dir = 'Other'
        
        return {
            'year': year,
            'newspaper_code': newspaper_code,
            'resolution': resolution,
            'stage': stage,
            'parent_directory': parent_dir,
            'filename': filename,
            'path': str(filepath)
        }
    
    def categorize_era(self, year):
        """Categorize by historical era with finer granularity"""
        if not year:
            return 'Unknown'
        if year < 1850:
            return '1800-1849 (Early 19th C)'
        elif year < 1875:
            return '1850-1874 (Mid 19th C)'
        elif year < 1900:
            return '1875-1899 (Late 19th C)'
        elif year < 1920:
            return '1900-1919 (WWI Era)'
        elif year < 1940:
            return '1920-1939 (Interwar)'
        elif year < 1960:
            return '1940-1959 (WWII-Postwar)'
        elif year < 1980:
            return '1960-1979 (Modern)'
        else:
            return '1980-2001 (Digital Era)'
    
    def analyze_text(self, text, metadata):
        """Comprehensive text analysis"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        analysis = {
            'word_count': len(words),
            'char_count': len(text),
            'errors_found': {
                'character_level': 0,
                'word_level': 0,
                'suspicious': 0
            }
        }
        
        # Character-level analysis
        for wrong, correct in self.char_confusion_pairs:
            pattern = re.compile(re.escape(wrong))
            matches = len(pattern.findall(text))
            if matches > 0:
                self.results['error_patterns']['character_substitutions'][f"{wrong}→{correct}"] += matches
                analysis['errors_found']['character_level'] += matches
        
        # Word-level analysis
        for word in words:
            if word in self.word_error_dict:
                correct = self.word_error_dict[word]
                self.results['error_patterns']['word_level_errors'][f"{word}→{correct}"] += 1
                analysis['errors_found']['word_level'] += 1
        
        # Suspicious pattern detection
        suspicious_count = 0
        
        # Mixed numbers and letters
        mixed = len(re.findall(r'\b\w*\d\w*[a-z]\w*|\b\w*[a-z]\w*\d\w*\b', text))
        suspicious_count += mixed
        self.results['error_patterns']['suspicious_patterns']['mixed_nums_letters'] += mixed
        
        # Repeated characters (3+)
        repeated = len(re.findall(r'(.)\1{2,}', text))
        suspicious_count += repeated
        self.results['error_patterns']['suspicious_patterns']['repeated_chars'] += repeated
        
        analysis['errors_found']['suspicious'] = suspicious_count
        
        return analysis
    
    def find_all_ocr_files(self):
        """Recursively find all OCR files in entire drive"""
        print(f"Scanning entire drive: {self.base_dir}")
        print("This may take a few minutes...")
        print()
        
        ocr_files = []
        dir_counts = defaultdict(int)
        
        try:
            for root, dirs, files in os.walk(self.base_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                root_path = Path(root)
                
                # Find OCR files
                for file in files:
                    if file.endswith('_ocr.txt') or file.endswith('ocr.txt'):
                        filepath = root_path / file
                        ocr_files.append(filepath)
                        
                        # Track by parent directory
                        if '2_KDNP_inprocess' in str(filepath):
                            dir_counts['2_KDNP_inprocess'] += 1
                        elif '3_KDNP_Ready' in str(filepath):
                            dir_counts['3_KDNP_Ready'] += 1
                        elif '4_Archival-Packages_Ready' in str(filepath):
                            dir_counts['4_Archival-Packages_Ready'] += 1
                        elif '7_NDNP_Batch' in str(filepath):
                            dir_counts['7_NDNP_Batch'] += 1
                        else:
                            dir_counts['Other'] += 1
        
        except Exception as e:
            print(f"Error scanning drive: {e}")
        
        print("=" * 80)
        print("FILES FOUND BY DIRECTORY:")
        print("-" * 80)
        for dir_name, count in sorted(dir_counts.items()):
            print(f"  {dir_name:<40} {count:>6} files")
        print("-" * 80)
        print(f"  {'TOTAL':<40} {len(ocr_files):>6} files")
        print("=" * 80)
        print()
        
        self.results['metadata']['directories_scanned'] = list(dir_counts.keys())
        
        return ocr_files
    
    def scan_all_files(self, max_files=None):
        """Scan all OCR files found on drive"""
        print("=" * 80)
        print("COMPREHENSIVE OCR ANALYSIS - FULL DRIVE SCAN")
        print("University of Kentucky Master's Project")
        print("=" * 80)
        print()
        
        # Find all files
        all_ocr_files = self.find_all_ocr_files()
        
        if not all_ocr_files:
            print("ERROR: No OCR files found!")
            return
        
        if max_files:
            print(f"Limiting analysis to first {max_files} files\n")
            all_ocr_files = all_ocr_files[:max_files]
        
        print(f"Processing {len(all_ocr_files)} files...")
        print("This will take several minutes. Please wait...\n")
        
        for idx, filepath in enumerate(all_ocr_files, 1):
            if idx % 10 == 0:
                print(f"  Progress: {idx}/{len(all_ocr_files)} files ({idx/len(all_ocr_files)*100:.1f}%)...")
            
            try:
                # Extract metadata
                metadata = self.extract_metadata(filepath)
                
                # Read and analyze text
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                analysis = self.analyze_text(text, metadata)
                
                # Update global statistics
                self.results['metadata']['total_files'] += 1
                self.results['metadata']['total_words'] += analysis['word_count']
                self.results['metadata']['total_characters'] += analysis['char_count']
                
                # Update directory statistics
                parent_dir = metadata['parent_directory']
                self.results['by_directory'][parent_dir]['files'] += 1
                self.results['by_directory'][parent_dir]['words'] += analysis['word_count']
                self.results['by_directory'][parent_dir]['errors'] += sum(analysis['errors_found'].values())
                
                # Update era statistics
                era = self.categorize_era(metadata['year'])
                if era not in self.results['by_era']:
                    self.results['by_era'][era] = {
                        'files': [],
                        'total_words': 0,
                        'total_errors': 0
                    }
                
                self.results['by_era'][era]['files'].append({
                    'filename': metadata['filename'],
                    'year': metadata['year'],
                    'newspaper': metadata['newspaper_code'],
                    'directory': parent_dir,
                    'word_count': analysis['word_count'],
                    'errors': sum(analysis['errors_found'].values())
                })
                self.results['by_era'][era]['total_words'] += analysis['word_count']
                self.results['by_era'][era]['total_errors'] += sum(analysis['errors_found'].values())
                
                # Update resolution statistics
                if metadata['resolution']:
                    res_key = f"{metadata['resolution']}dpi"
                    self.results['by_resolution'][res_key]['files'] += 1
                    self.results['by_resolution'][res_key]['words'] += analysis['word_count']
                    self.results['by_resolution'][res_key]['errors'] += sum(analysis['errors_found'].values())
                
                # Update newspaper statistics
                paper = metadata['newspaper_code']
                self.results['by_newspaper'][paper]['files'] += 1
                if metadata['year']:
                    self.results['by_newspaper'][paper]['years'].add(metadata['year'])
                for error_type, count in analysis['errors_found'].items():
                    self.results['by_newspaper'][paper]['errors'][error_type] += count
                
            except Exception as e:
                print(f"  Error processing {filepath.name}: {e}")
        
        print(f"\n✓ Analysis complete! Processed {self.results['metadata']['total_files']} files")
        print()
        self.calculate_statistics()
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        total_files = self.results['metadata']['total_files']
        total_words = self.results['metadata']['total_words']
        total_chars = self.results['metadata']['total_characters']
        
        self.results['statistics'] = {
            'avg_words_per_file': total_words / max(total_files, 1),
            'avg_chars_per_file': total_chars / max(total_files, 1),
            'total_error_patterns': {
                'character_level': sum(self.results['error_patterns']['character_substitutions'].values()),
                'word_level': sum(self.results['error_patterns']['word_level_errors'].values()),
                'suspicious': sum(self.results['error_patterns']['suspicious_patterns'].values())
            },
            'error_rates': {
                'char_error_rate': sum(self.results['error_patterns']['character_substitutions'].values()) / max(total_chars, 1) * 100,
                'word_error_rate': sum(self.results['error_patterns']['word_level_errors'].values()) / max(total_words, 1) * 100
            }
        }
        
        # Calculate era statistics
        for era, data in self.results['by_era'].items():
            if data['total_words'] > 0:
                data['error_rate'] = (data['total_errors'] / data['total_words']) * 100
                data['avg_errors_per_file'] = data['total_errors'] / len(data['files'])
    
    def generate_comprehensive_report(self, output_file='comprehensive_analysis_FULL.txt'):
        """Generate detailed analysis report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPREHENSIVE OCR ERROR ANALYSIS - FULL DRIVE SCAN\n")
            f.write("University of Kentucky Historical Newspaper Digitization Project\n")
            f.write(f"Analysis Date: {self.results['metadata']['analysis_date']}\n")
            f.write("=" * 80 + "\n\n")
            
            # Overview
            f.write("DATASET OVERVIEW\n")
            f.write("-" * 80 + "\n")
            f.write(f"Base directory: {self.results['metadata']['base_directory']}\n")
            f.write(f"Total files analyzed: {self.results['metadata']['total_files']}\n")
            f.write(f"Total words processed: {self.results['metadata']['total_words']:,}\n")
            f.write(f"Total characters: {self.results['metadata']['total_characters']:,}\n")
            f.write(f"Average words per file: {self.results['statistics']['avg_words_per_file']:.1f}\n")
            f.write(f"Average characters per file: {self.results['statistics']['avg_chars_per_file']:.1f}\n\n")
            
            # By directory
            f.write("FILES BY DIRECTORY\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Directory':<40} {'Files':>8} {'Words':>12} {'Errors':>12}\n")
            f.write("-" * 80 + "\n")
            for dir_name, data in sorted(self.results['by_directory'].items()):
                f.write(f"{dir_name:<40} {data['files']:>8} {data['words']:>12,} {data['errors']:>12,}\n")
            f.write("\n")
            
            # Error summary
            f.write("ERROR SUMMARY\n")
            f.write("-" * 80 + "\n")
            stats = self.results['statistics']['total_error_patterns']
            f.write(f"Character-level errors: {stats['character_level']:,}\n")
            f.write(f"Word-level errors: {stats['word_level']:,}\n")
            f.write(f"Suspicious patterns: {stats['suspicious']:,}\n")
            f.write(f"Total errors identified: {sum(stats.values()):,}\n\n")
            
            rates = self.results['statistics']['error_rates']
            f.write(f"Character error rate: {rates['char_error_rate']:.3f}%\n")
            f.write(f"Word error rate: {rates['word_error_rate']:.5f}%\n\n")
            
            # By era
            f.write("ANALYSIS BY HISTORICAL ERA\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Era':<30} {'Files':>8} {'Words':>12} {'Errors':>12} {'Rate':>8}\n")
            f.write("-" * 80 + "\n")
            
            for era in sorted(self.results['by_era'].keys()):
                data = self.results['by_era'][era]
                f.write(f"{era:<30} {len(data['files']):>8} {data['total_words']:>12,} "
                       f"{data['total_errors']:>12,} {data.get('error_rate', 0):>7.2f}%\n")
            f.write("\n")
            
            # By resolution
            if self.results['by_resolution']:
                f.write("ANALYSIS BY SCAN RESOLUTION\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Resolution':<20} {'Files':>10} {'Words':>12} {'Errors':>12}\n")
                f.write("-" * 80 + "\n")
                for res, data in sorted(self.results['by_resolution'].items()):
                    f.write(f"{res:<20} {data['files']:>10} {data['words']:>12,} {data['errors']:>12,}\n")
                f.write("\n")
            
            # Top errors
            f.write("TOP 30 CHARACTER SUBSTITUTION ERRORS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Rank':<6} {'Pattern':<30} {'Frequency':>15} {'% of Total':>12}\n")
            f.write("-" * 80 + "\n")
            total_char_errors = sum(self.results['error_patterns']['character_substitutions'].values())
            for idx, (error, count) in enumerate(
                self.results['error_patterns']['character_substitutions'].most_common(30), 1):
                pct = (count / total_char_errors * 100) if total_char_errors > 0 else 0
                f.write(f"{idx:<6} {error:<30} {count:>15,} {pct:>11.1f}%\n")
            f.write("\n")
            
            f.write("TOP 30 WORD-LEVEL ERRORS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Rank':<6} {'Pattern':<30} {'Frequency':>15}\n")
            f.write("-" * 80 + "\n")
            for idx, (error, count) in enumerate(
                self.results['error_patterns']['word_level_errors'].most_common(30), 1):
                f.write(f"{idx:<6} {error:<30} {count:>15,}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"✓ Comprehensive report saved: {output_file}")
    
    def export_json(self, output_file='comprehensive_analysis_FULL.json'):
        """Export full results as JSON"""
        # Convert sets to lists for JSON serialization
        export_data = self.results.copy()
        for paper, data in export_data['by_newspaper'].items():
            data['years'] = sorted(list(data['years']))
            data['errors'] = dict(data['errors'])
        
        # Convert Counters to dicts
        export_data['error_patterns']['character_substitutions'] = dict(
            export_data['error_patterns']['character_substitutions'].most_common(100))
        export_data['error_patterns']['word_level_errors'] = dict(
            export_data['error_patterns']['word_level_errors'].most_common(100))
        export_data['error_patterns']['suspicious_patterns'] = dict(
            export_data['error_patterns']['suspicious_patterns'])
        export_data['by_resolution'] = dict(export_data['by_resolution'])
        export_data['by_newspaper'] = dict(export_data['by_newspaper'])
        export_data['by_directory'] = dict(export_data['by_directory'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ JSON data exported: {output_file}")


def main():
    """Main execution"""
    print("=" * 80)
    print("COMPREHENSIVE OCR ANALYSIS SYSTEM - FULL DRIVE")
    print("University of Kentucky Master's Project")
    print("=" * 80)
    print()
    
    # Initialize analyzer for entire G:\ drive
    analyzer = ComprehensiveOCRAnalyzer(base_directory="G:\\")
    
    # Scan all files (no limit for comprehensive analysis)
    analyzer.scan_all_files(max_files=None)
    
    # Generate outputs
    print("Generating reports...")
    analyzer.generate_comprehensive_report('comprehensive_analysis_FULL.txt')
    analyzer.export_json('comprehensive_analysis_FULL.json')
    
    print("\n" + "=" * 80)
    print("FULL DRIVE ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nOutputs generated:")
    print("  1. comprehensive_analysis_FULL.txt - Detailed report")
    print("  2. comprehensive_analysis_FULL.json - Complete data export")
    print(f"\nDataset statistics:")
    print(f"  Total files: {analyzer.results['metadata']['total_files']}")
    print(f"  Total words: {analyzer.results['metadata']['total_words']:,}")
    print(f"  Total characters: {analyzer.results['metadata']['total_characters']:,}")
    print()


if __name__ == "__main__":
    main()