import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import threading
import glob
import tkinter.scrolledtext as scrolledtext

class EbookConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB 转 PDF 批量转换器")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.selected_files = []
        self.ebook_convert_path = r"C:\Program Files\Calibre2\ebook-convert.exe"
        
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self.root, text="EPUB 转 PDF 批量转换器", font=("Arial", 16, "bold")).pack(pady=10)
        
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(dir_frame, text="源目录:").grid(row=0, column=0, sticky="w")
        tk.Entry(dir_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=5)
        tk.Button(dir_frame, text="选择", command=self.select_input_dir, width=10).grid(row=0, column=2)
        
        tk.Label(dir_frame, text="输出目录:").grid(row=1, column=0, sticky="w", pady=(10,0))
        tk.Entry(dir_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=(10,0))
        tk.Button(dir_frame, text="选择", command=self.select_output_dir, width=10).grid(row=1, column=2, pady=(10,0))
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="全选", command=self.select_all, width=10).pack(side="left", padx=5)
        tk.Button(control_frame, text="取消全选", command=self.deselect_all, width=10).pack(side="left", padx=5)
        tk.Button(control_frame, text="刷新列表", command=self.refresh_list, width=10).pack(side="left", padx=5)
        
        list_frame = tk.Frame(self.root, height=200)
        list_frame.pack(fill="both", expand=True, padx=20)
        list_frame.pack_propagate(False)
        
        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.btn_convert = tk.Button(self.root, text="开始转换", command=self.start_convert, 
                                     bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), height=2)
        self.btn_convert.pack(fill="x", padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=8, state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=False, padx=20, pady=(0, 10))
        
    def select_input_dir(self):
        dirname = filedialog.askdirectory(title="选择包含 EPUB 文件的目录")
        if dirname:
            self.input_dir.set(dirname)
            if not self.output_dir.get():
                self.output_dir.set(dirname)
            self.load_files()
            
    def select_output_dir(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir.set(dirname)
            
    def load_files(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.input_dir.get():
            return
            
        pattern = os.path.join(self.input_dir.get(), "*.epub")
        epub_files = glob.glob(pattern)
        
        if not epub_files:
            tk.Label(self.scrollable_frame, text="该目录下没有找到 EPUB 文件", fg="gray").pack()
            return
            
        self.selected_files = []
        
        for filepath in sorted(epub_files):
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.scrollable_frame, variable=var, anchor="w", width=80)
            cb.pack(fill="x", padx=10, pady=2)
            
            filename = os.path.basename(filepath)
            tk.Label(self.scrollable_frame, text=f"  {filename}", anchor="w").pack(fill="x", padx=30)
            
            self.selected_files.append((filepath, var))
            
    def refresh_list(self):
        if self.input_dir.get():
            self.load_files()
            
    def select_all(self):
        for _, var in self.selected_files:
            var.set(True)
            
    def deselect_all(self):
        for _, var in self.selected_files:
            var.set(False)
            
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        
    def start_convert(self):
        if not self.input_dir.get():
            messagebox.showwarning("警告", "请先选择源目录")
            return
            
        selected = [(path, var) for path, var in self.selected_files if var.get()]
        
        if not selected:
            messagebox.showwarning("警告", "请至少选择一个文件")
            return
            
        output_dir = self.output_dir.get() if self.output_dir.get() else self.input_dir.get()
        
        self.btn_convert.config(state="disabled", text="转换中...")
        self.log("=" * 40)
        self.log("开始转换...")
        
        thread = threading.Thread(target=self.convert_files, args=(selected, output_dir))
        thread.daemon = True
        thread.start()
        
    def convert_files(self, files, output_dir):
        success = 0
        failed = 0
        
        for filepath, _ in files:
            filename = os.path.basename(filepath)
            output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".pdf")
            
            self.root.after(0, self.log, f"转换: {filename}")
            
            try:
                process = subprocess.Popen(
                    [self.ebook_convert_path, filepath, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=300)
                    
                    if process.returncode == 0:
                        self.root.after(0, self.log, f"  [OK] {os.path.basename(output_file)}")
                        success += 1
                    else:
                        err_msg = stderr.decode('utf-8', errors='ignore') if stderr else ''
                        self.root.after(0, self.log, f"  [FAIL] {err_msg[:100]}")
                        failed += 1
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.root.after(0, self.log, f"  [FAIL] 超时: {filename}")
                    failed += 1
                    
            except Exception as e:
                self.root.after(0, self.log, f"  [FAIL] {str(e)}")
                failed += 1
                
        self.root.after(0, self.log, "=" * 40)
        self.root.after(0, self.log, f"完成! 成功: {success}, 失败: {failed}")
        self.root.after(0, self.on_complete, success, failed)
        
    def on_complete(self, success, failed):
        self.btn_convert.config(state="normal", text="开始转换")
        
        if failed == 0:
            messagebox.showinfo("完成", f"全部转换成功！\n成功: {success} 个文件")
        else:
            messagebox.showwarning("完成", f"转换完成\n成功: {success}, 失败: {failed}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = EbookConverter(root)
    root.mainloop()
