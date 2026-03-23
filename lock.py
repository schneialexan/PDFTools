import fitz  # PyMuPDF

# --- CONFIGURATION ---
INPUT_FILE = "input.pdf"
OUTPUT_FILE = "locked_fields_output.pdf"
# ---------------------

def interactive_lock():
    try:
        doc = fitz.open(INPUT_FILE)
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    fields_modified = 0
    
    print(f"Scanning {doc.page_count} pages for filled input fields...")
    print("-" * 30)

    for page_num, page in enumerate(doc, start=1):
        for widget in page.widgets():
            # Get the current value and name
            value = (widget.field_value or "").strip()
            name = widget.field_name or "Unnamed Field"

            # Only prompt if the field contains text
            if value:
                print(f"\n[Page {page_num}] Field Name: '{name}'")
                print(f"Contains text: \"{value}\"")
                
                user_choice = input("Do you want to make this field UNCHANGEABLE? (y/n): ").lower().strip()

                if user_choice == 'y':
                    # bit 1 (value 1) is the Read-Only flag in PDF spec
                    # We use bitwise OR to set it without changing other flags
                    widget.field_flags |= 1 
                    widget.update()
                    fields_modified += 1
                    print("Status: LOCKED")
                else:
                    print("Status: Kept editable")

    if fields_modified > 0:
        # Save the changes
        doc.save(OUTPUT_FILE)
        doc.close()
        print("\n" + "="*30)
        print(f"Done! {fields_modified} fields were locked.")
        print(f"Result saved as: {OUTPUT_FILE}")
    else:
        doc.close()
        print("\nNo fields were locked. No file saved.")

if __name__ == "__main__":
    interactive_lock()