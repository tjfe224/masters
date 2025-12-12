"""
OCR Text Corrector - Applies automated corrections to OCR output
Based on error pattern analysis from University of Kentucky newspaper collection
"""

import re
from pathlib import Path

class OCRCorrector:
    def __init__(self):
        # Dictionary of known OCR errors → corrections
        self.word_corrections = {
            # th- errors
            'tlie': 'the', 'ilie': 'the', 'tbe': 'the', 'tho': 'the',
            'tliat': 'that', 'tbat': 'that', 'tlien': 'then',
            'tliis': 'this', 'tliese': 'these', 'tliose': 'those',
            'tliey': 'they', 'tliere': 'there', 'tliem': 'them',
            'tlieir': 'their', 'tlius': 'thus', 'tliree': 'three',
            'tlian': 'than', 'tlirough': 'through',
            
            # wh- errors  
            'wliich': 'which', 'wlien': 'when', 'wliere': 'where',
            'wliile': 'while', 'wliite': 'white', 'wlio': 'who',
            'wliole': 'whole', 'wliat': 'what', 'wliy': 'why',
            
            # h- errors
            'liave': 'have', 'liad': 'had', 'liis': 'his',
            'lier': 'her', 'liim': 'him', 'liow': 'how',
            'liere': 'here', 'liand': 'hand', 'liouse': 'house',
            'lieart': 'heart', 'liead': 'head', 'liigh': 'high',
            
            # with- errors
            'witli': 'with', 'wltli': 'with', 'witb': 'with',
            
            # and- errors
            'aud': 'and', 'aad': 'and', 'ani': 'and', 'anc': 'and',
            
            # from- errors
            'fiom': 'from', 'frorn': 'from', 'fro': 'from',
            
            # friend- errors
            'fiieids': 'friends', 'firiend': 'friend', 'fiiend': 'friend',
            
            # other common errors
            'tbserved': 'observed', 'loubted': 'doubted', 'probf': 'proof',
            'woifet': 'worst', 'ruong': 'wrong', 'wag': 'was',
            'io': 'to', 'od': 'of', 'ai': 'at', 'iu': 'in',
            'oue': 'one', 'cau': 'can', 'rnay': 'may',
            'rny': 'my', 'owu': 'own', 'uow': 'now',
            'ouly': 'only', 'iustead': 'instead', 'upou': 'upon',
            'rnan': 'man', 'raen': 'men', 'rnore': 'more',
            'rnust': 'must', 'rnake': 'make', 'rnany': 'many',
            'tirne': 'time', 'sorne': 'some', 'corne': 'come',
            'becorne': 'become', 'horne': 'home', 'narne': 'name',
            'sarne': 'same', 'deterrnine': 'determine',
            'deterrnined': 'determined', 'govenrment': 'government',
            'govemment': 'government', 'govermnent': 'government',
            'cornmittee': 'committee', 'cornmon': 'common',
            'raade': 'made', 'raight': 'might', 'electea': 'elected',
            'acccle': 'accede', 'fiieids': 'friends', 'wfficb': 'which',
            'den.ee': 'defence', 'boldy': 'boldly'
        }
        
        # Character-level corrections (regex patterns)
        self.char_patterns = [
            # Fix "AI" at start of word (often "Mr")
            (r'\bAI([a-z])', r'M\1'),
            # Fix number-letter confusion in words
            (r'\b([A-Z])1([a-z])', r'\1I\2'),  # Replace 1 with I in names
            # Remove excessive spaces
            (r'  +', ' '),
            # Fix line breaks within words
            (r'(\w)-\s*\n\s*(\w)', r'\1\2'),
        ]
        
        self.corrections_applied = 0
        self.corrections_log = []
    
    def correct_text(self, text, case_sensitive=False):
        """Apply corrections to text"""
        corrected = text
        self.corrections_applied = 0
        self.corrections_log = []
        
        # Word-level corrections
        for wrong, correct in self.word_corrections.items():
            if case_sensitive:
                pattern = r'\b' + re.escape(wrong) + r'\b'
            else:
                pattern = r'\b' + re.escape(wrong) + r'\b'
                
            count = len(re.findall(pattern, corrected, re.IGNORECASE))
            if count > 0:
                corrected = re.sub(pattern, correct, corrected, flags=re.IGNORECASE)
                self.corrections_applied += count
                self.corrections_log.append(f"{wrong} → {correct}: {count} times")
        
        # Character-level pattern corrections
        for pattern, replacement in self.char_patterns:
            matches = len(re.findall(pattern, corrected))
            if matches > 0:
                corrected = re.sub(pattern, replacement, corrected)
                self.corrections_applied += matches
        
        return corrected
    
    def correct_file(self, input_path, output_path=None):
        """Correct an entire file"""
        input_path = Path(input_path)
        
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_corrected{input_path.suffix}"
        
        try:
            # Read original
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_text = f.read()
            
            # Apply corrections
            corrected_text = self.correct_text(original_text)
            
            # Write corrected version
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(corrected_text)
            
            return {
                'success': True,
                'input_file': str(input_path),
                'output_file': str(output_path),
                'corrections_applied': self.corrections_applied,
                'original_length': len(original_text),
                'corrected_length': len(corrected_text)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_file': str(input_path)
            }
    
    def generate_comparison_report(self, original_text, corrected_text, output_file='comparison_report.txt'):
        #Generate before/after comparison report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("OCR Correction Comparison Report=\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("Summary\n")
            f.write("-" * 80 + "\n")
            f.write(f"Corrections applied: {self.corrections_applied}\n")
            f.write(f"Original text length: {len(original_text):,} characters\n")
            f.write(f"Corrected text length: {len(corrected_text):,} characters\n\n")
            
            if self.corrections_log:
                f.write("Corrections Made\n")
                f.write("-" * 80 + "\n")
                for log_entry in self.corrections_log:
                    f.write(f"  {log_entry}\n")
                f.write("\n")
            
            f.write("SAMPLE EXCERPTS (First 1000 characters)\n")
            f.write("-" * 80 + "\n")
            f.write("Original:\n")
            f.write(original_text[:1000] + "\n\n")
            f.write("Corrected:\n")
            f.write(corrected_text[:1000] + "\n")
            f.write("=" * 80 + "\n")
        
        print(f"Comparison report saved to: {output_file}")


def demo_correction():
    """Demonstrate the corrector on sample text"""
    sample_text = """
    Tlie fiieids of Mr. Clay stated, that if tlie friemsef Mr. Adams 
    would unite witli them, tliey would make AI*. Adams President in 
    one hour. But tbat is not all. It was loubted whether tliis was 
    tbe beginning of this matter. Iu the ruong hands, such a probf 
    might be used to show woifet corruption. Tlie government wag 
    strong aud tbe people wliich had elected him were satisfied.
    """
    
    corrector = OCRCorrector()
    corrected = corrector.correct_text(sample_text)
    
    print("=" * 80)
    print("Demonstration: OCR Correction")
    print("=" * 80)
    print("\nOriginal Text:")
    print(sample_text)
    print("\nCorrected Text:")
    print(corrected)
    print(f"\nTotal corrections applied: {corrector.corrections_applied}")
    print("=" * 80)


def main():
    # Main execution - correct a specific file or run demo    
    # Demo mode - shows how it works
    print("Running demonstration mode...")
    demo_correction()
    
    print("\n" + "=" * 80)
    print("To Correct Actual Files:")
    print("=" * 80)
    corrector = OCRCorrector()
    result = corrector.correct_file('G:/2_KDNP_inprocess/hen_19090108-19091231/1_finished/1909051401/1909051401_150dpi/hen1909051401_ocr.txt')
    print(f"Corrections: {result['corrections_applied']}")
    print("""
      # Example usage:
      corrector = OCRCorrector()
      
      # Correct a single file
      result = corrector.correct_file('path/to/file_ocr.txt')
      print(f"Corrections: {result['corrections_applied']}")
      
      # Or correct multiple files
      from pathlib import Path
      for ocr_file in Path('G:/2_KDNP_inprocess').glob('**/kea*_ocr.txt'):
          result = corrector.correct_file(ocr_file)
          print(f"{ocr_file.name}: {result['corrections_applied']} corrections")
    """)


if __name__ == "__main__":
    main()
