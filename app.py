import os
import json
import threading
import queue
from tkinter import Tk, StringVar, BooleanVar, filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# Lazy import so the UI opens fast
def lazy_imports():
    global pytesseract, convert_from_path
    import pytesseract
    from pdf2image import convert_from_path

# Background worker so the UI stays responsive
class OCRWorker(threading.Thread):
    def __init__(self, pdf_path, out_path, tesseract_path, poppler_bin, lang, dpi, logq, progress_cb):
        super().__init__(daemon=True)
        self.pdf_path = pdf_path
        self.out_path = out_path
        self.tesseract_path = tesseract_path
        self.poppler_bin = poppler_bin
        self.lang = lang
        self.dpi = dpi
        self.logq = logq
        self.progress_cb = progress_cb

    def log(self, msg):
        self.logq.put(msg)

    def run(self):
        try:
            self.log("🔁 Starting OCR...")
            if not os.path.isfile(self.pdf_path):
                raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

            # Import heavy deps here
            lazy_imports()

            # Configure Tesseract path if provided
            if self.tesseract_path:
                if not os.path.isfile(self.tesseract_path):
                    raise FileNotFoundError("Invalid tesseract.exe path.")
                import pytesseract as _pt
                _pt.pytesseract.tesseract_cmd = self.tesseract_path
                self.log(f"✔ Using Tesseract: {self.tesseract_path}")
            else:
                self.log("ℹ Using Tesseract from system PATH (if available)")

            # Configure Poppler for pdf2image
            poppler_arg = None
            if self.poppler_bin:
                if not os.path.isdir(self.poppler_bin):
                    raise FileNotFoundError("Invalid Poppler \\bin folder.")
                poppler_arg = self.poppler_bin
                self.log(f"✔ Using Poppler bin: {self.poppler_bin}")
            else:
                self.log("ℹ Trying Poppler from system PATH")

            # PDF -> images
            self.log("📄 Converting PDF pages to images...")
            pages = convert_from_path(self.pdf_path, dpi=self.dpi, poppler_path=poppler_arg)
            total = len(pages)
            if total == 0:
                raise RuntimeError("No pages detected in PDF.")
            self.log(f"✔ Page count: {total}")

            # OCR each page
            results = []
            for i, page in enumerate(pages, start=1):
                self.log(f"🔎 OCR page {i}/{total} (lang={self.lang})...")
                text = pytesseract.image_to_string(page, lang=self.lang)
                results.append({"page": i, "text": text.strip()})
                self.progress_cb(i, total)

            # Save JSON
            os.makedirs(os.path.dirname(self.out_path) or ".", exist_ok=True)
            with open(self.out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            self.log(f"✅ Done! Saved JSON: {self.out_path}")
            self.progress_cb(total, total)

        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.progress_cb(0, 1)

class App:
    def __init__(self, root: Tk):
        self.root = root
        root.title("PDF → JSON OCR (pytesseract + pdf2image)")
        root.geometry("820x600")

        # State
        self.pdf_path = StringVar()
        self.json_path = StringVar()
        self.tesseract_path = StringVar()
        self.poppler_bin = StringVar()
        self.lang = StringVar(value="eng")  # "eng", "vie", or "eng+vie"
        self.dpi = StringVar(value="300")
        self.auto_open = BooleanVar(value=True)

        self.logq = queue.Queue()

        pad = {"padx": 8, "pady": 6}
        frm = ttk.Frame(root)
        frm.pack(fill="both", expand=True)

        # Row 1: PDF input
        ttk.Label(frm, text="PDF input:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.pdf_path, width=80).grid(row=0, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, **pad)

        # Row 2: JSON output
        ttk.Label(frm, text="JSON output:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.json_path, width=80).grid(row=1, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Save As...", command=self.browse_json).grid(row=1, column=2, **pad)

        # Row 3: Tesseract
        ttk.Label(frm, text="tesseract.exe (optional):").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.tesseract_path, width=80).grid(row=2, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse...", command=self.browse_tesseract).grid(row=2, column=2, **pad)

        # Row 4: Poppler bin
        ttk.Label(frm, text="Poppler\\bin (optional):").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.poppler_bin, width=80).grid(row=3, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse...", command=self.browse_poppler).grid(row=3, column=2, **pad)

        # Row 5: Options
        opts = ttk.Frame(frm)
        opts.grid(row=4, column=0, columnspan=3, sticky="we", **pad)
        ttk.Label(opts, text="Language:").pack(side="left")
        ttk.Combobox(opts, values=("eng", "vie", "jpn", "eng+vie", "eng+jpn"), textvariable=self.lang, width=10, state="readonly").pack(side="left", padx=6)
        ttk.Label(opts, text="DPI:").pack(side="left")
        ttk.Entry(opts, textvariable=self.dpi, width=6).pack(side="left", padx=6)
        ttk.Checkbutton(opts, text="Open output folder when finished", variable=self.auto_open).pack(side="left", padx=12)
        ttk.Button(opts, text="❓ Help", command=self.show_help).pack(side="left", padx=6)

        # Row 6: Run button
        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=3, sticky="we", **pad)
        self.run_btn = ttk.Button(btns, text="▶ Run OCR", command=self.start_ocr)
        self.run_btn.pack(side="left")

        # Row 7: Progress
        self.prog = ttk.Progressbar(frm, mode="determinate")
        self.prog.grid(row=6, column=0, columnspan=3, sticky="we", **pad)

        # Row 8: Log
        self.logbox = ScrolledText(frm, height=16, wrap="word")
        self.logbox.grid(row=7, column=0, columnspan=3, sticky="nsew", **pad)

        # Resizing
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(7, weight=1)

        # Periodic log flush
        self.root.after(120, self.flush_log)

    def browse_pdf(self):
        path = filedialog.askopenfilename(title="Select PDF", filetypes=(("PDF", "*.pdf"),))
        if path:
            self.pdf_path.set(path)
            base, _ = os.path.splitext(path)
            self.json_path.set(base + ".json")

    def browse_json(self):
        path = filedialog.asksaveasfilename(title="Save JSON As...", defaultextension=".json", filetypes=(("JSON", "*.json"),))
        if path:
            self.json_path.set(path)

    def browse_tesseract(self):
        path = filedialog.askopenfilename(title="Select tesseract.exe", filetypes=(("Executable", "*.exe"),))
        if path:
            self.tesseract_path.set(path)

    def browse_poppler(self):
        path = filedialog.askdirectory(title="Select Poppler\\bin folder")
        if path:
            self.poppler_bin.set(path)

    def progress_cb(self, done, total):
        self.prog["maximum"] = total
        self.prog["value"] = done
        self.root.update_idletasks()

    def flush_log(self):
        try:
            while True:
                msg = self.logq.get_nowait()
                self.logbox.insert("end", msg + "\n")
                self.logbox.see("end")
        except queue.Empty:
            pass
        self.root.after(150, self.flush_log)

    def start_ocr(self):
        pdf = self.pdf_path.get().strip()
        outp = self.json_path.get().strip()
        tpath = self.tesseract_path.get().strip()
        pbin = self.poppler_bin.get().strip()
        lang = self.lang.get().strip()

        try:
            dpi = int(self.dpi.get().strip())
        except ValueError:
            messagebox.showerror("Error", "DPI must be an integer, e.g., 300.")
            return

        if not pdf:
            messagebox.showerror("Missing data", "Please select an input PDF.")
            return
        if not outp:
            messagebox.showerror("Missing data", "Please choose an output JSON path.")
            return

        self.run_btn.config(state="disabled")

        def on_done(done, total):
            self.progress_cb(done, total)
            if done == total:
                self.run_btn.config(state="normal")
                if self.auto_open.get():
                    try:
                        folder = os.path.dirname(outp) or "."
                        os.startfile(folder)
                    except Exception:
                        pass

        worker = OCRWorker(pdf, outp, tpath or None, pbin or None, lang or "eng", dpi, self.logq, on_done)
        worker.start()

    def show_help(self):
        messagebox.showinfo(
            "Help",
            "1) Install/extract Poppler (bin folder) and Tesseract OCR\n"
            "2) Point to tesseract.exe and Poppler\\bin if they are not in PATH\n"
            "3) Choose input PDF and output JSON path\n"
            "4) Click 'Run OCR'\n\n"
            "Languages: 'eng', 'vie', or 'eng+vie'. Recommended DPI: 300."
        )

def main():
    root = Tk()
    # Optional: nicer theme / HiDPI
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    try:
        style = ttk.Style()
        style.theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
