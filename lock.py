import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- CONFIGURATION ---
DEFAULT_INPUT = "input.pdf"
OUTPUT_FILE = "locked_fields_output.pdf"
TEXT_SIZE = 11
# ---------------------

def get_input_file(path):
    """Checks if file exists; if not, opens a Windows File Dialog."""
    if os.path.exists(path):
        return path
    
    print(f"File '{path}' not found. Opening file picker...")
    
    # Initialize hidden tkinter root
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes("-topmost", True) # Bring picker to front
    
    selected_file = filedialog.askopenfilename(
        title="Select a PDF file to process",
        filetypes=[("PDF files", "*.pdf")],
        initialdir=os.getcwd()
    )
    
    root.destroy()
    
    if not selected_file:
        print("No file selected. Exiting.")
        return None
    return selected_file

def interactive_lock():
    input_path = get_input_file(DEFAULT_INPUT)
    if not input_path:
        return

    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    fields_modified = 0
    print(f"\nProcessing: {input_path}")
    print(f"Scanning {doc.page_count} pages for filled input fields...")
    print("-" * 30)

    for page_num in range(len(doc)):
        page = doc[page_num]
        for widget in page.widgets():
            value = (widget.field_value or "").strip()
            name = widget.field_name or "Unnamed Field"

            if value:
                print(f"\n[Page {page_num + 1}] Field: '{name}' | Content: \"{value}\"")
                
                user_choice = input("Lock this field? (y/n): ").lower().strip()

                if user_choice == 'y':
                    # Set Read-Only flags (Method: High-level + Low-level)
                    widget.field_flags |= 1 
                    
                    # Set fixed text size from configuration
                    widget.field_font_size = TEXT_SIZE
                    
                    widget.update()
                    
                    # Force update the raw PDF dictionary keys
                    xref = widget.xref
                    doc.xref_set_key(xref, "Ff", "1") # Field Flag: ReadOnly
                    doc.xref_set_key(xref, "F", "4")  # Annotation Flag: Print/Static
                    doc.xref_set_key(xref, "FS", str(TEXT_SIZE)) # Font Size from config
                    
                    fields_modified += 1
                    print(f"Status: LOCKED ({TEXT_SIZE}pt font size set)")

    if fields_modified > 0:
        # Save with 'expand=True' to finalize the dictionary changes
        doc.save(OUTPUT_FILE, garbage=3, deflate=True, expand=True)
        doc.close()
        print(f"\nSuccess! {fields_modified} fields locked in '{OUTPUT_FILE}'.")
    else:
        doc.close()
        print("\nNo fields were locked.")

if __name__ == "__main__":
    interactive_lock()