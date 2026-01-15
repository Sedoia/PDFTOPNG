import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import pymupdf  # PyMuPDF
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageChops
import os
import threading
import datetime
import platform
import subprocess

# --- COLORS & THEME ---
BG_COLOR = "#181818"       # Darker, sleeker black
PANEL_BG = "#202020"
ACCENT_COLOR = "#00d1b2"   # Sedo Teal
TEXT_COLOR = "#e0e0e0"     
LIST_BG = "#252526"        

class SedoConverterApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sedo Converter - God Mode")
        self.geometry("1000x750") 
        self.configure(bg=BG_COLOR)
        
        try: self.eval('tk::PlaceWindow . center')
        except: pass

        self.attributes("-topmost", True)
        self.after(1000, lambda: self.attributes("-topmost", False))

        self.files_map = {} 
        self.last_output_folder = ""
        
        # --- VARIABLES ---
        self.delete_original_var = tk.BooleanVar(value=False)
        self.stitch_mode_var = tk.BooleanVar(value=False)
        self.extract_text_var = tk.BooleanVar(value=False)
        self.transparent_var = tk.BooleanVar(value=False)
        
        # NEW EFFECTS VARIABLES
        self.night_mode_var = tk.BooleanVar(value=False)
        self.smart_crop_var = tk.BooleanVar(value=False)
        self.watermark_text_var = tk.StringVar(value="")
        
        self.output_format_var = tk.StringVar(value="PNG")
        self.dpi_var = tk.IntVar(value=300)
        
        # --- NEW PAGE RANGE VARIABLE ---
        self.page_range_var = tk.StringVar(value="All")

        self.create_widgets()

    def create_widgets(self):
        # HEADER
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", pady=20)
        tk.Label(header, text="SEDO CONVERTER", font=("Segoe UI", 26, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack()
        tk.Label(header, text="God Mode Edition", font=("Segoe UI", 10, "italic"), bg=BG_COLOR, fg="#666666").pack()

        # MAIN SPLIT
        main_body = tk.Frame(self, bg=BG_COLOR)
        main_body.pack(fill="both", expand=True, padx=30)

        # --- LEFT: FILES ---
        left_frame = tk.Frame(main_body, bg=BG_COLOR)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.drop_frame = tk.LabelFrame(left_frame, text="  SOURCE  ", font=("Segoe UI", 8, "bold"), bg=BG_COLOR, fg="#666666", bd=1, relief="solid")
        self.drop_frame.pack(fill="x", pady=5)
        self.drop_label = tk.Label(self.drop_frame, text="DROP PDFs HERE", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg="#444444", pady=30, cursor="hand2")
        self.drop_label.pack(fill="both", expand=True)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_label.bind("<Button-1>", self.browse_files)

        self.listbox = tk.Listbox(left_frame, bg=LIST_BG, fg=TEXT_COLOR, font=("Consolas", 10), bd=0, highlightthickness=0, selectbackground=ACCENT_COLOR)
        self.listbox.pack(fill="both", expand=True, pady=15)

        # --- RIGHT: CONTROLS ---
        right_frame = tk.Frame(main_body, bg=BG_COLOR)
        right_frame.pack(side="right", fill="y", padx=(0, 0))

        # PANEL 1: CORE SETTINGS
        p1 = tk.LabelFrame(right_frame, text="  CORE  ", font=("Segoe UI", 8, "bold"), bg=PANEL_BG, fg="#aaaaaa", bd=0, padx=15, pady=10)
        p1.pack(fill="x", pady=(0, 10))
        
        # Format
        tk.Label(p1, text="Fmt:", bg=PANEL_BG, fg="#aaaaaa", font=("Segoe UI", 8)).pack(side="left")
        ttk.Combobox(p1, textvariable=self.output_format_var, values=["PNG", "JPG"], state="readonly", width=5).pack(side="left", padx=(5,10))
        
        # DPI
        tk.Label(p1, text="DPI:", bg=PANEL_BG, fg="#aaaaaa", font=("Segoe UI", 8)).pack(side="left")
        tk.Scale(p1, from_=72, to=400, orient="horizontal", variable=self.dpi_var, bg=PANEL_BG, fg="white", highlightthickness=0, length=80).pack(side="left", padx=5)

        # NEW PAGE RANGE INPUT
        tk.Label(p1, text="Pages:", bg=PANEL_BG, fg="#aaaaaa", font=("Segoe UI", 8)).pack(side="left", padx=(10, 5))
        pages_entry = tk.Entry(p1, textvariable=self.page_range_var, width=8, bg="#333333", fg="white", insertbackground="white", bd=0, font=("Segoe UI", 9))
        pages_entry.pack(side="left")
        # Tooltip-ish help
        self.create_tooltip(pages_entry, "Examples: 'All', '1-5', '1,3,5', '1-3, 10'")

        # PANEL 2: EFFECTS STUDIO
        p2 = tk.LabelFrame(right_frame, text="  EFFECTS STUDIO  ", font=("Segoe UI", 8, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR, bd=0, padx=15, pady=10)
        p2.pack(fill="x", pady=(0, 10))

        # Toggles
        self.create_toggle(p2, "Night Mode (Invert Colors)", self.night_mode_var)
        self.create_toggle(p2, "Smart Crop (Trim Borders)", self.smart_crop_var)
        self.create_toggle(p2, "Stitch to Long Image", self.stitch_mode_var)
        
        # Watermark Section
        tk.Label(p2, text="Watermark Text:", bg=PANEL_BG, fg="#aaaaaa", font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 2))
        tk.Entry(p2, textvariable=self.watermark_text_var, bg="#333333", fg="white", insertbackground="white", bd=0).pack(fill="x", pady=(0, 5))
        tk.Label(p2, text="(Leave empty for none)", bg=PANEL_BG, fg="#555555", font=("Segoe UI", 7)).pack(anchor="w")

        # PANEL 3: UTILS
        p3 = tk.LabelFrame(right_frame, text="  UTILS  ", font=("Segoe UI", 8, "bold"), bg=PANEL_BG, fg="#aaaaaa", bd=0, padx=15, pady=10)
        p3.pack(fill="x", pady=(0, 10))
        
        self.create_toggle(p3, "Extract Text (.txt)", self.extract_text_var)
        self.create_toggle(p3, "Transparent BG", self.transparent_var)
        
        tk.Checkbutton(p3, text="Secure Shred Original", variable=self.delete_original_var, 
                       bg=PANEL_BG, fg="#ff5555", selectcolor=PANEL_BG, activebackground=PANEL_BG, activeforeground="#ff5555").pack(anchor="w", pady=(5,0))

        # ACTION AREA
        control_frame = tk.Frame(self, bg=BG_COLOR)
        control_frame.pack(fill="x", padx=30, pady=20)

        self.progress_var = tk.DoubleVar()
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", thickness=10, background=ACCENT_COLOR, troughcolor="#333333", borderwidth=0)
        ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100, style="TProgressbar").pack(fill="x", pady=(0, 10))
        
        self.status_label = tk.Label(control_frame, text="Ready. (Page Range: All)", bg=BG_COLOR, fg="#666666", font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 10))

        btn_grid = tk.Frame(control_frame, bg=BG_COLOR)
        btn_grid.pack(fill="x")
        
        tk.Button(btn_grid, text="CLEAR", command=self.clear_list, bg="#333333", fg="white", bd=0, padx=20, pady=12).pack(side="left")
        self.convert_btn = tk.Button(btn_grid, text="INITIATE PROCESS", command=self.start_conversion_thread, bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 11, "bold"), bd=0, padx=40, pady=12)
        self.convert_btn.pack(side="right")
        self.open_folder_btn = tk.Button(btn_grid, text="FOLDER", command=self.open_output_folder, bg="#333333", fg="white", bd=0, padx=20, pady=12, state="disabled")
        self.open_folder_btn.pack(side="right", padx=10)

    def create_toggle(self, parent, text, var):
        tk.Checkbutton(parent, text=text, variable=var, bg=PANEL_BG, fg="white", selectcolor="#444444", activebackground=PANEL_BG, activeforeground="white").pack(anchor="w", pady=2)

    def create_tooltip(self, widget, text):
        def enter(event):
            self.status_label.config(text=text, fg=ACCENT_COLOR)
        def leave(event):
            self.status_label.config(text="Ready.", fg="#666666")
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # --- IMAGE PROCESSING ENGINE ---
    def process_image_effects(self, img):
        # 1. Smart Crop
        if self.smart_crop_var.get():
            bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
            diff = ImageChops.difference(img, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                img = img.crop(bbox)

        # 2. Night Mode (Invert)
        if self.night_mode_var.get():
            if img.mode == 'RGBA':
                r,g,b,a = img.split()
                rgb_image = Image.merge('RGB', (r,g,b))
                inverted_image = ImageOps.invert(rgb_image)
                r2,g2,b2 = inverted_image.split()
                img = Image.merge('RGBA', (r2,g2,b2,a))
            else:
                img = ImageOps.invert(img.convert('RGB'))

        # 3. Watermark
        wm_text = self.watermark_text_var.get()
        if wm_text:
            draw = ImageDraw.Draw(img)
            # Dynamic font size based on image width
            fontsize = int(img.width / 20)
            try:
                # Try loading a system font, fallback to default
                font = ImageFont.truetype("arial.ttf", fontsize)
            except:
                font = ImageFont.load_default()
            
            # Simple color choice
            wm_color = (255, 0, 0) if not self.night_mode_var.get() else (0, 255, 255)
            # Draw approx center-bottom
            draw.text((img.width * 0.5, img.height * 0.9), wm_text, fill=wm_color, font=font, anchor="mm")

        return img

    # --- HELPER: PAGE RANGE PARSER ---
    def parse_page_indices(self, range_str, total_pages):
        """
        Parses strings like "1-5, 8, 11-13" into a list of 0-based indices.
        Returns all pages if input is 'All' or empty.
        """
        clean_str = range_str.strip().lower()
        if not clean_str or clean_str == "all":
            return list(range(total_pages))
        
        indices = set()
        parts = clean_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle range like 3-5
                try:
                    start, end = map(int, part.split('-'))
                    # Clamp to valid range (1-based input converted to 0-based index)
                    start_idx = max(0, start - 1)
                    end_idx = min(total_pages, end)
                    if start_idx < end_idx:
                        indices.update(range(start_idx, end_idx))
                except ValueError:
                    continue # Skip invalid chunks
            else:
                # Handle single number like 7
                try:
                    p = int(part)
                    if 1 <= p <= total_pages:
                        indices.add(p - 1)
                except ValueError:
                    continue
                    
        sorted_indices = sorted(list(indices))
        return sorted_indices if sorted_indices else list(range(total_pages))

    # --- CORE LOGIC ---
    def handle_drop(self, event):
        self.add_files(self.parse_drop_files(event.data))

    def browse_files(self, event=None):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files: self.add_files(files)

    def parse_drop_files(self, data):
        if "{" in data:
            import re
            return re.findall(r'\{k.*?\}|\S+', data)
        return data.split()

    def add_files(self, paths):
        for path in paths:
            clean_path = path.strip('{}')
            if os.path.isfile(clean_path) and clean_path.lower().endswith(".pdf"):
                if clean_path not in self.files_map.values():
                    idx = self.listbox.size()
                    self.listbox.insert(tk.END, f" 📄 {os.path.basename(clean_path)}")
                    self.files_map[idx] = clean_path
        self.status_label.config(text=f"Queue: {len(self.files_map)} files ready")

    def clear_list(self):
        self.files_map = {}
        self.listbox.delete(0, tk.END)
        self.status_label.config(text="List cleared")
        self.progress_var.set(0)

    def start_conversion_thread(self):
        if not self.files_map: return
        out = filedialog.askdirectory()
        if not out: return
        self.last_output_folder = out
        self.convert_btn.config(state="disabled", text="RUNNING...")
        threading.Thread(target=self.process_files, args=(out,), daemon=True).start()

    def process_files(self, output_folder):
        total_files = len(self.files_map)
        dpi = self.dpi_var.get()
        fmt = self.output_format_var.get()
        stitch = self.stitch_mode_var.get()
        extract_txt = self.extract_text_var.get()
        transparent = self.transparent_var.get()
        
        # Parse range string once or per file? Usually user wants same logic per batch, 
        # but max pages differs per PDF. Logic handles per PDF.
        range_input = self.page_range_var.get()

        for idx in range(total_files):
            pdf_path = self.files_map[idx]
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            try:
                self.listbox.delete(idx)
                self.listbox.insert(idx, f" ⚙️ {pdf_name}")
                self.status_label.config(text=f"Processing: {pdf_name}...")

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                save_dir = os.path.join(output_folder, f"{pdf_name}_{timestamp}")
                os.makedirs(save_dir, exist_ok=True)
                
                doc = pymupdf.open(pdf_path)
                
                # --- DETERMINE PAGES TO PROCESS ---
                pages_to_process = self.parse_page_indices(range_input, doc.page_count)
                
                images_list = []
                full_text = []

                # Loop through specific indices instead of all pages
                for i in pages_to_process:
                    page = doc[i]
                    
                    if extract_txt:
                        full_text.append(f"--- P{i+1} ---\n{page.get_text()}\n")

                    pix = page.get_pixmap(dpi=dpi, alpha=transparent, annots=True)
                    mode = "RGBA" if transparent else "RGB"
                    img = Image.frombytes("RGBA" if pix.alpha else "RGB", [pix.width, pix.height], pix.samples)
                    
                    if not transparent and mode == "RGBA":
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background

                    # --- APPLY EFFECTS ---
                    img = self.process_image_effects(img)

                    if stitch:
                        images_list.append(img)
                    else:
                        ext = "png" if fmt == "PNG" else "jpg"
                        # Filename includes original page number (i+1)
                        img.save(os.path.join(save_dir, f"Page_{i+1}.{ext}"), quality=95)

                if stitch and images_list:
                    total_height = sum(img.height for img in images_list)
                    max_width = max(img.width for img in images_list)
                    stitched_img = Image.new("RGB", (max_width, total_height), (0,0,0) if self.night_mode_var.get() else (255,255,255))
                    y_offset = 0
                    for img in images_list:
                        x_offset = (max_width - img.width) // 2
                        stitched_img.paste(img, (x_offset, y_offset))
                        y_offset += img.height
                    ext = "png" if fmt == "PNG" else "jpg"
                    stitched_img.save(os.path.join(save_dir, f"{pdf_name}_FULL.{ext}"), quality=90)

                if extract_txt and full_text:
                    with open(os.path.join(save_dir, "Text_Data.txt"), "w", encoding="utf-8") as f:
                        f.write("\n".join(full_text))

                doc.close()
                if self.delete_original_var.get(): self.secure_shred(pdf_path)

                self.listbox.delete(idx)
                self.listbox.insert(idx, f" ✅ {pdf_name}")

            except Exception as e:
                print(e)
                self.listbox.delete(idx)
                self.listbox.insert(idx, f" ❌ {pdf_name}")

            self.progress_var.set(((idx + 1) / total_files) * 100)

        self.finish_conversion()

    def secure_shred(self, path):
        try:
            with open(path, "wb") as f: f.write(os.urandom(os.path.getsize(path)))
            os.remove(path)
        except: pass

    def finish_conversion(self):
        self.status_label.config(text="Sequence Complete.")
        self.convert_btn.config(state="normal", text="INITIATE PROCESS")
        self.open_folder_btn.config(state="normal")
        messagebox.showinfo("Sedo Converter", "All tasks completed successfully.")

    def open_output_folder(self):
        if self.last_output_folder:
            path = os.path.realpath(self.last_output_folder)
            if platform.system() == "Windows": os.startfile(path)
            elif platform.system() == "Darwin": subprocess.Popen(["open", path])
            else: subprocess.Popen(["xdg-open", path])

if __name__ == "__main__":
    app = SedoConverterApp()
    app.mainloop()