import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- CONFIGURATION ---
DEFAULT_INPUT = "input.pdf"
OUTPUT_FILE = "fillable_output.pdf"
TEXT_SIZE = 11
# ---------------------

class DragSelectTableUI:
    def __init__(self, table_text):
        self.root = tk.Tk()
        self.root.title("PDF Table Field Selector")
        self.root.attributes("-topmost", True)
        
        self.table_text = table_text
        self.rows = len(table_text)
        self.cols = len(table_text[0])
        
        # Selection state: 2D grid of Booleans
        self.selected = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_widgets = []
        
        # Dragging logic state
        self.start_cell = None 
        
        # UI Header
        tk.Label(self.root, text="Click or Drag to select cells (Green = Input Field)", 
                 pady=10, font=("Arial", 10, "bold")).pack()

        # Build the Grid
        self.grid_frame = tk.Frame(self.root, bg="#ccc", borderwidth=1)
        self.grid_frame.pack(padx=20, pady=10)

        for r in range(self.rows):
            row_widgets = []
            for c in range(self.cols):
                text = self.table_text[r][c].strip() or " "
                display_text = (text[:15] + '..') if len(text) > 15 else text
                
                lbl = tk.Label(self.grid_frame, text=display_text, width=14, height=2, 
                               relief="flat", borderwidth=1, bg="white", font=("Segoe UI", 9))
                lbl.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
                
                # Mouse Bindings for Dragging
                lbl.bind("<Button-1>", lambda e, r=r, c=c: self.on_press(r, c))
                lbl.bind("<B1-Motion>", self.on_drag)
                lbl.bind("<ButtonRelease-1>", lambda e: self.on_release())
                
                row_widgets.append(lbl)
            self.cell_widgets.append(row_widgets)

        # Footer Buttons
        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack()
        tk.Button(btn_frame, text="Generate PDF", bg="#28a745", fg="white", 
                  font=("Arial", 10, "bold"), padx=20, command=self.confirm).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.root.destroy).pack(side=tk.LEFT)

        self.confirmed = False

    def get_cell_at_pos(self, event):
        # Find which label is under the mouse during a drag
        x, y = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x, y)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cell_widgets[r][c] == widget:
                    return r, c
        return None

    def on_press(self, r, c):
        self.start_cell = (r, c)
        self.update_highlight(r, c, r, c)

    def on_drag(self, event):
        curr = self.get_cell_at_pos(event)
        if curr and self.start_cell:
            self.update_highlight(self.start_cell[0], self.start_cell[1], curr[0], curr[1])

    def on_release(self):
        # When mouse is released, finalize the "yellow" temporary highlight into "green" selection
        if not self.start_cell: return
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cell_widgets[r][c].cget("bg") == "yellow":
                    self.selected[r][c] = not self.selected[r][c]
        self.start_cell = None
        self.refresh_ui()

    def update_highlight(self, r1, c1, r2, c2):
        # Temporary yellow highlight while dragging
        self.refresh_ui()
        min_r, max_r = sorted([r1, r2])
        min_c, max_c = sorted([c1, c2])
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                self.cell_widgets[r][c].config(bg="yellow")

    def refresh_ui(self):
        for r in range(self.rows):
            for c in range(self.cols):
                color = "#90ee90" if self.selected[r][c] else "white"
                self.cell_widgets[r][c].config(bg=color)

    def confirm(self):
        self.confirmed = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        if self.confirmed:
            return [(r, c) for r in range(self.rows) for c in range(self.cols) if self.selected[r][c]]
        return None

def get_input_file(path):
    if os.path.exists(path): return path
    root = tk.Tk(); root.withdraw()
    selected = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
    root.destroy()
    return selected

def main():
    input_path = get_input_file(DEFAULT_INPUT)
    if not input_path: return

    doc = fitz.open(input_path)
    page = doc[0]
    tabs = page.find_tables()

    if not tabs.tables:
        messagebox.showerror("Error", "No tables detected on page 1.")
        return

    table = tabs.tables[0]
    # table.rows is a list of Row objects, each has a .cells attribute (list of bboxes)
    # table.extract() gives us the text
    text_grid = table.extract()
    
    ui = DragSelectTableUI(text_grid)
    selected_indices = ui.run()

    if not selected_indices:
        print("No cells selected.")
        return

    fields_added = 0
    # Use the table row/cell structure directly for 1:1 coordinate mapping
    for (r, c) in selected_indices:
        try:
            # bbox is (x0, y0, x1, y1)
            cell_bbox = table.rows[r].cells[c]
            if not cell_bbox: continue

            # Apply small padding so text doesn't hit borders
            rect = fitz.Rect(cell_bbox)
            rect.x0 += 2; rect.y0 += 2; rect.x1 -= 2; rect.y1 -= 2
            
            widget = fitz.Widget()
            widget.rect = rect
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_name = f"Field_R{r}_C{c}"
            widget.text_font = "Helv"
            widget.text_fontsize = TEXT_SIZE
            
            page.add_widget(widget)
            fields_added += 1
        except Exception as e:
            print(f"Skipping cell ({r},{c}) due to error: {e}")

    if fields_added > 0:
        doc.save(OUTPUT_FILE, garbage=3, deflate=True)
        messagebox.showinfo("Success", f"Created {fields_added} fields in '{OUTPUT_FILE}'")
    
    doc.close()

if __name__ == "__main__":
    main()