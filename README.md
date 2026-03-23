# PDF Tools

A collection of Python utilities for working with PDF forms and documents. This repository contains tools that I've developed and continue to extend as I need various PDF manipulation capabilities.

## Tools

### Duplicate Field Unsyncer (`duplicate_unsync.py`)
Fixes PDF forms with duplicate field names that cause syncing issues. When multiple form fields share the same name, they sync their values - this tool renames duplicates to make them independent.

**Features:**
- Scans all pages for form fields (widgets)
- Automatically renames duplicate fields with numeric suffixes
- Preserves original field functionality
- Provides detailed output of changes made

**Usage:**
```bash
python duplicate_unsync.py
```
Place your PDF file as `input.pdf` in the same directory, and the fixed version will be saved as `fixed_unsynced_output.pdf`.

### Interactive Field Locker (`lock.py`)
Interactive tool to lock filled form fields, making them read-only. Perfect for finalizing forms while preserving the content.

**Features:**
- Scans for fields containing text
- Interactive prompts for each filled field
- Sets read-only flags on selected fields
- Preserves unfilled fields as editable

**Usage:**
```bash
python lock.py
```
Place your PDF file as `input.pdf` in the same directory. The tool will prompt you interactively for each filled field and save the result as `locked_fields_output.pdf`.

## Requirements

- Python 3.6+
- PyMuPDF (fitz)

Install dependencies:
```bash
pip install PyMuPDF
```

## How to Use

1. Clone or download this repository
2. Install the required dependencies
3. Place your PDF file as `input.pdf` in the repository directory
4. Run the desired tool
5. Find the processed PDF in the output file specified by each tool

## Contributing

This is a personal collection of tools that I extend as needed. Feel free to submit issues or pull requests if you find bugs or have suggestions for improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Tools

This repository is designed to grow over time. Planned additions include:
- Batch processing capabilities
- More form field manipulation tools
- PDF metadata utilities
- Text extraction and analysis tools

## Disclaimer

These tools work with standard PDF forms. Some PDFs (particularly XFA forms or scanned documents) may not be compatible with form field manipulation.
