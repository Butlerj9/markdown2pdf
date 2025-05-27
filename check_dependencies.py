#!/usr/bin/env python3
"""
Check dependencies for Markdown to PDF Converter
"""

import os
import sys
import subprocess
import platform

def check_command(command, args=["--version"], name=None):
    """Check if a command is available"""
    if name is None:
        name = command

    try:
        result = subprocess.run([command] + args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5)
        if result.returncode == 0:
            print(f"✅ {name} is installed")
            print(f"   Version: {result.stdout.decode('utf-8').splitlines()[0]}")
            return True
        else:
            print(f"❌ {name} is installed but returned an error")
            print(f"   Error: {result.stderr.decode('utf-8')}")
            return False
    except FileNotFoundError:
        print(f"❌ {name} is not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ {name} command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking {name}: {str(e)}")
        return False

def check_pandoc():
    """Check if Pandoc is installed"""
    # First try the standard command
    if check_command("pandoc", name="Pandoc"):
        return True

    # Try common installation paths
    if platform.system() == "Windows":
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), "Pandoc", "pandoc.exe"),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), "Pandoc", "pandoc.exe")
        ]

        for path in paths:
            if os.path.exists(path):
                print(f"✅ Pandoc is installed at {path}")
                try:
                    result = subprocess.run([path, "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                    print(f"   Version: {result.stdout.decode('utf-8').splitlines()[0]}")
                    return True
                except Exception as e:
                    print(f"   Error running Pandoc: {str(e)}")
                    return False

    print("❌ Pandoc is not installed or not found")
    print("   Please install Pandoc from https://pandoc.org/installing.html")
    return False

def check_pdf_engines():
    """Check if PDF engines are installed"""
    engines = ['xelatex', 'pdflatex', 'lualatex', 'wkhtmltopdf', 'weasyprint']
    found_engines = []

    for engine in engines:
        if check_command(engine, name=f"PDF engine ({engine})"):
            found_engines.append(engine)

    if not found_engines:
        print("❌ No PDF engines found")
        print("   Please install at least one PDF engine (XeLaTeX recommended)")
        return False

    return True

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        ("PyQt6", "PyQt6"),
        ("PyPDF2", "PyPDF2"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("ebooklib", "ebooklib"),
        ("python-docx", "docx")
    ]

    all_installed = True

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ Python package {package_name} is installed")
        except ImportError:
            print(f"❌ Python package {package_name} is not installed")
            all_installed = False

    return all_installed

def main():
    """Main function"""
    print("Checking dependencies for Markdown to PDF Converter...")
    print("=" * 60)

    # Check Python version
    python_version = sys.version.split()[0]
    python_version_tuple = tuple(map(int, python_version.split('.')))
    if python_version_tuple >= (3, 6):
        print(f"✅ Python {python_version} is installed (required: 3.6+)")
    else:
        print(f"❌ Python {python_version} is installed (required: 3.6+)")
        print("   Please upgrade Python to version 3.6 or higher")

    # Check Pandoc
    pandoc_installed = check_pandoc()

    # Check PDF engines
    pdf_engines_installed = check_pdf_engines()

    # Check Python dependencies
    python_deps_installed = check_python_dependencies()

    # Summary
    print("=" * 60)
    print("Summary:")
    if pandoc_installed and pdf_engines_installed and python_deps_installed:
        print("✅ All dependencies are installed")
    else:
        print("❌ Some dependencies are missing")
        if not pandoc_installed:
            print("   - Pandoc is required for document conversion")
        if not pdf_engines_installed:
            print("   - At least one PDF engine is required for PDF export")
        if not python_deps_installed:
            print("   - Some Python packages are missing")

    return 0 if pandoc_installed and pdf_engines_installed and python_deps_installed else 1

if __name__ == "__main__":
    sys.exit(main())
