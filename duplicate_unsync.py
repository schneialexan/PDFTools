import fitz  # This is PyMuPDF

# --- CONFIGURATION ---
INPUT_FILE = "input.pdf"
OUTPUT_FILE = "fixed_unsynced_output.pdf"
# ---------------------

def aggressive_unsync():
    doc = fitz.open(INPUT_FILE)
    
    # Dictionary to track names we've encountered
    name_tracker = {}
    total_renamed = 0

    print(f"Scanning {doc.page_count} pages for 'hidden' fields...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # widgets() finds every form field on the page directly
        for widget in page.widgets():
            current_name = widget.field_name
            
            if not current_name:
                continue

            if current_name not in name_tracker:
                name_tracker[current_name] = 1
            else:
                # It's a duplicate!
                name_tracker[current_name] += 1
                new_name = f"{current_name}_{name_tracker[current_name]}"
                
                # Apply the new name to the widget
                widget.field_name = new_name
                widget.update() # This commits the change to the PDF
                
                print(f"Page {page_num+1}: Renamed duplicate '{current_name}' -> '{new_name}'")
                total_renamed += 1

    if total_renamed > 0:
        doc.save(OUTPUT_FILE)
        print(f"\nSuccess! Found and fixed {total_renamed} syncing fields.")
        print(f"Saved as: {OUTPUT_FILE}")
    else:
        print("\nNo duplicates found in the widget scan.")
        if name_tracker:
            print("Fields found:")
            for name in list(name_tracker.keys())[:10]:
                print(f" - {name}")
        else:
            print("Truly no fields found. The PDF might be an XFA form or a scan.")

if __name__ == "__main__":
    try:
        aggressive_unsync()
    except Exception as e:
        print(f"Error: {e}")