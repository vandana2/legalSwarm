"""
Test script for Parser Agent
Run this to test clause extraction from your sample contracts

Usage:
    python test_parser.py
    python test_parser.py --file docs/sample_contracts/NDA.pdf
    python test_parser.py --file docs/sample_contracts/SaaS_Agreement.pdf
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.parser_agent import ParserAgent
from services.pdf_parser import PDFParser


def print_separator(title=""):
    """Print a nice separator"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'-'*80}\n")


def test_parser_with_text(text, title="Test Contract"):
    """Test parser with raw text"""
    print_separator(f"Testing Parser Agent: {title}")
    
    parser = ParserAgent()
    clauses = parser.parse_document(text)
    
    print(f"✓ Total Clauses Found: {len(clauses)}\n")
    
    # Display summary
    summary = parser.get_summary()
    print("Clause Types Distribution:")
    for clause_type, count in summary['clause_types'].items():
        print(f"  - {clause_type}: {count}")
    
    print_separator("Extracted Clauses")
    
    # Display each clause
    for idx, clause in enumerate(clauses, 1):
        print(f"Clause #{idx}")
        print(f"  ID: {clause['clause_id']}")
        print(f"  Type: {clause['clause_type']}")
        print(f"  Title: {clause['title']}")
        print(f"  Section: {clause['section']}")
        print(f"  Text: {clause['text'][:150]}...")
        print()
    
    return clauses


def test_parser_with_pdf(pdf_path):
    """Test parser with actual PDF file"""
    print_separator(f"Testing with PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None
    
    try:
        # Extract text from PDF
        pdf_parser = PDFParser(pdf_path)
        text = pdf_parser.extract_text()
        
        if not text:
            print("❌ Could not extract text from PDF")
            return None
        
        print(f"✓ PDF Text Extracted ({len(text)} characters)\n")
        
        # Parse with Parser Agent
        parser = ParserAgent()
        clauses = parser.parse_document(text)
        
        print(f"✓ Total Clauses Found: {len(clauses)}\n")
        
        # Display summary
        summary = parser.get_summary()
        print("Clause Types Distribution:")
        for clause_type, count in summary['clause_types'].items():
            print(f"  - {clause_type}: {count}")
        
        print_separator("Extracted Clauses (First 5)")
        
        # Display first 5 clauses
        for idx, clause in enumerate(clauses[:5], 1):
            print(f"Clause #{idx}")
            print(f"  ID: {clause['clause_id']}")
            print(f"  Type: {clause['clause_type']}")
            print(f"  Title: {clause['title']}")
            print(f"  Section: {clause['section']}")
            print(f"  Text Preview: {clause['text'][:150]}...")
            print()
        
        if len(clauses) > 5:
            print(f"... and {len(clauses) - 5} more clauses\n")
        
        return clauses
        
    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        return None


def save_results_to_json(clauses, output_file="test_results.json"):
    """Save parsing results to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(clauses, f, indent=2)
    print(f"\n✓ Results saved to: {output_file}")


def list_sample_contracts():
    """List all sample contracts in docs/sample_contracts"""
    sample_dir = "docs/sample_contracts"
    
    if not os.path.exists(sample_dir):
        print(f"Sample contracts directory not found: {sample_dir}")
        return []
    
    pdf_files = list(Path(sample_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {sample_dir}")
        return []
    
    print(f"\nFound {len(pdf_files)} sample contract(s):")
    for idx, pdf_file in enumerate(pdf_files, 1):
        size = os.path.getsize(pdf_file) / 1024  # Size in KB
        print(f"  {idx}. {pdf_file.name} ({size:.1f} KB)")
    
    return pdf_files


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Parser Agent with sample contracts"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to specific PDF file to test"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all sample contracts"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("  LegalSwarm - Parser Agent Test Suite")
    print("="*80)
    
    # Test 1: Simple text example
    sample_text = """
    Section 1: Liability
    The Company shall not be liable for any indirect, incidental, or consequential damages.
    The total liability shall not exceed the fees paid in the last 12 months.
    
    Section 2: Termination
    Either party may terminate this agreement with 30 days written notice.
    Upon termination, all obligations cease except those that survive termination.
    
    Section 3: Confidentiality
    Each party agrees to maintain confidentiality of proprietary information.
    Confidential information shall not be disclosed to third parties without written consent.
    
    Section 4: Payment
    Payment is due within 30 days of invoice date.
    Late payments will incur interest at 1.5% per month.
    """
    
    print("\n[TEST 1] Testing with sample text\n")
    test_parser_with_text(sample_text, "Sample NDA")
    
    # Test 2: List sample contracts
    print("\n[TEST 2] Listing sample contracts\n")
    sample_contracts = list_sample_contracts()
    
    # Test 3: Test with specific file
    if args.file:
        print(f"\n[TEST 3] Testing with specified file\n")
        clauses = test_parser_with_pdf(args.file)
        if clauses:
            save_results_to_json(clauses, f"test_results_{Path(args.file).stem}.json")
    
    # Test 4: Auto-test all sample contracts
    elif sample_contracts:
        print(f"\n[TEST 3] Auto-testing all sample contracts\n")
        for idx, pdf_file in enumerate(sample_contracts, 1):
            print(f"\n--- Testing Contract {idx}/{len(sample_contracts)} ---")
            clauses = test_parser_with_pdf(str(pdf_file))
            if clauses:
                output_name = f"test_results_{pdf_file.stem}.json"
                save_results_to_json(clauses, output_name)
    
    # Test 5: List available tests
    elif args.list:
        print("\nAvailable sample contracts:")
        list_sample_contracts()
    
    print("\n" + "="*80)
    print("  Test Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
