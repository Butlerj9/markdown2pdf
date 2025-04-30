#!/usr/bin/env python3
"""
Script to verify that export settings are correctly reflected in pandoc commands.
This script analyzes the log file from test_all_exports.py to check if settings
are correctly applied to the pandoc commands.
"""

import re
import sys
import os
import argparse
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='Verify export settings in pandoc commands')
    parser.add_argument('--log-file', type=str, help='Path to the log file from test_all_exports.py')
    parser.add_argument('--output', type=str, help='Path to save the verification results')
    return parser.parse_args()

def extract_test_info(line):
    """Extract test information from a test header line"""
    test_info = {}
    
    # Extract format
    format_match = re.search(r'Format: (\w+)', line)
    if format_match:
        test_info['format'] = format_match.group(1).lower()
    
    # Extract engine for PDF
    engine_match = re.search(r'Format: PDF with (\w+) engine', line)
    if engine_match:
        test_info['engine'] = engine_match.group(1).lower()
        test_info['format'] = 'pdf'
    
    # Extract TOC setting
    toc_match = re.search(r'TOC: (Enabled|Disabled)', line)
    if toc_match:
        test_info['toc'] = toc_match.group(1) == 'Enabled'
    
    # Extract TOC depth
    depth_match = re.search(r'Depth: (\d+)', line)
    if depth_match:
        test_info['toc_depth'] = int(depth_match.group(1))
    
    # Extract page settings
    page_match = re.search(r'Page: (\w+) (\w+)', line)
    if page_match:
        test_info['page_size'] = page_match.group(1)
        test_info['orientation'] = page_match.group(2)
    
    # Extract font settings
    font_match = re.search(r'Font: (Master font|Individual fonts)', line)
    if font_match:
        test_info['master_font'] = font_match.group(1) == 'Master font'
    
    # Extract numbering settings
    numbering_match = re.search(r'Numbering: (Technical|Standard)', line)
    if numbering_match:
        test_info['technical_numbering'] = numbering_match.group(1) == 'Technical'
    
    return test_info

def extract_pandoc_command(line):
    """Extract the pandoc command from a log line"""
    command_match = re.search(r'Running pandoc command: (pandoc .+)', line)
    if command_match:
        return command_match.group(1)
    return None

def verify_settings(test_info, command):
    """Verify that the settings in test_info are correctly reflected in the pandoc command"""
    results = {
        'format': test_info.get('format', 'unknown'),
        'engine': test_info.get('engine', 'n/a'),
        'settings': {},
        'issues': []
    }
    
    # Check TOC settings
    if test_info.get('toc', False):
        if '--toc' not in command:
            results['issues'].append('TOC is enabled but --toc flag is missing')
        else:
            results['settings']['toc'] = 'Correctly enabled'
            
        # Check TOC depth
        toc_depth_match = re.search(r'--toc-depth=(\d+)', command)
        if toc_depth_match:
            depth = int(toc_depth_match.group(1))
            if depth != test_info.get('toc_depth', 0):
                results['issues'].append(f'TOC depth mismatch: expected {test_info.get("toc_depth")}, got {depth}')
            else:
                results['settings']['toc_depth'] = f'Correctly set to {depth}'
        elif test_info.get('toc', False):
            results['issues'].append('TOC depth not specified in command')
    else:
        if '--toc' in command:
            results['issues'].append('TOC is disabled but --toc flag is present')
        else:
            results['settings']['toc'] = 'Correctly disabled'
    
    # Check technical numbering
    if test_info.get('technical_numbering', False):
        if '--number-sections' not in command:
            results['issues'].append('Technical numbering is enabled but --number-sections flag is missing')
        else:
            results['settings']['technical_numbering'] = 'Correctly enabled'
    else:
        if '--number-sections' in command:
            results['issues'].append('Technical numbering is disabled but --number-sections flag is present')
        elif '--variable secnumdepth=-2' in command or '--variable disable-numbering=true' in command:
            results['settings']['technical_numbering'] = 'Correctly disabled'
    
    # Check page size
    if test_info.get('format') == 'pdf' or test_info.get('format') == 'html':
        page_size = test_info.get('page_size', '').lower()
        if page_size:
            page_size_match = re.search(r'-V papersize=(\w+)', command)
            if page_size_match:
                cmd_page_size = page_size_match.group(1).lower()
                if cmd_page_size != page_size.lower():
                    results['issues'].append(f'Page size mismatch: expected {page_size}, got {cmd_page_size}')
                else:
                    results['settings']['page_size'] = f'Correctly set to {page_size}'
            else:
                results['issues'].append(f'Page size {page_size} not specified in command')
    
    # Check orientation (this is harder to verify as it might be handled differently)
    # For PDF, orientation might be set in LaTeX variables
    
    # Check output format
    output_format = test_info.get('format', '').lower()
    if output_format:
        output_match = re.search(r'-o .+\.(\w+)', command)
        if output_match:
            cmd_format = output_match.group(1).lower()
            if cmd_format != output_format and not (output_format == 'pdf' and cmd_format == 'pdf'):
                results['issues'].append(f'Output format mismatch: expected {output_format}, got {cmd_format}')
            else:
                results['settings']['output_format'] = f'Correctly set to {output_format}'
    
    # For PDF, check engine
    if test_info.get('format') == 'pdf' and test_info.get('engine'):
        engine = test_info.get('engine')
        engine_match = re.search(r'--pdf-engine=(\w+)', command)
        if engine_match:
            cmd_engine = engine_match.group(1).lower()
            if engine != 'wkhtmltopdf' and cmd_engine != engine:  # Special case for wkhtmltopdf which uses full path
                results['issues'].append(f'PDF engine mismatch: expected {engine}, got {cmd_engine}')
            elif engine == 'wkhtmltopdf' and 'wkhtmltopdf' not in cmd_engine:
                results['issues'].append(f'PDF engine mismatch: expected {engine}, but not found in {cmd_engine}')
            else:
                results['settings']['pdf_engine'] = f'Correctly set to {engine}'
        else:
            results['issues'].append(f'PDF engine {engine} not specified in command')
    
    return results

def analyze_log_file(log_file):
    """Analyze the log file to extract test info and pandoc commands"""
    results = []
    current_test = None
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check for test header
            if 'Test ' in line and ':' in line and ('Format:' in line or 'TOC:' in line):
                current_test = extract_test_info(line)
            
            # Check for pandoc command
            if current_test and 'Running pandoc command:' in line:
                command = extract_pandoc_command(line)
                if command:
                    verification = verify_settings(current_test, command)
                    results.append(verification)
                    current_test = None
    
    return results

def summarize_results(results):
    """Summarize the verification results"""
    total_tests = len(results)
    tests_with_issues = sum(1 for r in results if r['issues'])
    
    summary = {
        'total_tests': total_tests,
        'tests_with_issues': tests_with_issues,
        'success_rate': (total_tests - tests_with_issues) / total_tests * 100 if total_tests > 0 else 0,
        'issues_by_format': defaultdict(int),
        'common_issues': defaultdict(int)
    }
    
    for result in results:
        if result['issues']:
            summary['issues_by_format'][result['format']] += 1
            for issue in result['issues']:
                summary['common_issues'][issue] += 1
    
    return summary

def main():
    args = parse_args()
    
    if not args.log_file:
        print("Please provide a log file with --log-file")
        return 1
    
    if not os.path.exists(args.log_file):
        print(f"Log file not found: {args.log_file}")
        return 1
    
    results = analyze_log_file(args.log_file)
    summary = summarize_results(results)
    
    # Print summary
    print("\n===== SETTINGS VERIFICATION SUMMARY =====")
    print(f"Total tests analyzed: {summary['total_tests']}")
    print(f"Tests with issues: {summary['tests_with_issues']}")
    print(f"Success rate: {summary['success_rate']:.2f}%")
    
    if summary['issues_by_format']:
        print("\nIssues by format:")
        for fmt, count in summary['issues_by_format'].items():
            print(f"  {fmt}: {count} tests with issues")
    
    if summary['common_issues']:
        print("\nMost common issues:")
        for issue, count in sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {issue}: {count} occurrences")
    
    # Save detailed results if output file specified
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
