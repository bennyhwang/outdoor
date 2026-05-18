import tkinter as tk
from tkinter import ttk
import threading
import pyttsx3

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文字转语音")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="输入要朗读的文字:", font=("Arial", 12)).pack(anchor="w")
        
        self.text_input = tk.Text(main_frame, height=8, font=("Arial", 12))
        self.text_input.pack(fill="both", expand=True, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=10)
        
        ttk.Button(control_frame, text="朗读", command=self.speak).pack(side="left", padx=5)
        ttk.Button(control_frame, text="停止", command=self.stop).pack(side="left", padx=5)
        ttk.Button(control_frame, text="保存音频", command=self.save_audio).pack(side="left", padx=5)
        
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill="x", pady=10)
        
        ttk.Label(settings_frame, text="语速:").pack(side="left", padx=(0, 5))
        self.speed_var = tk.IntVar(value=150)
        self.speed_slider = ttk.Scale(settings_frame, from_=50, to=300, variable=self.speed_var, command=self.update_speed)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(settings_frame, textvariable=self.speed_var, width=4).pack(side="left")
        
        ttk.Label(settings_frame, text="音量:").pack(side="left", padx=(20, 5))
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_slider = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=self.volume_var, command=self.update_volume)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(settings_frame, textvariable=self.volume_var, width=4).pack(side="left")
        
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="gray")
        self.status_label.pack(anchor="w")
        
    def speak(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            self.status_label.config(text="请输入文字", foreground="red")
            return
            
        self.status_label.config(text="正在朗读...", foreground="blue")
        
        def run_tts():
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', self.speed_var.get())
            engine.setProperty('volume', self.volume_var.get())
            engine.say(text)
            engine.runAndWait()
            self.root.after(0, lambda: self.status_label.config(text="朗读完成", foreground="green"))
            
        thread = threading.Thread(target=run_tts)
        thread.daemon = True
        thread.start()
        
    def stop(self):
        self.engine.stop()
        self.status_label.config(text="已停止", foreground="gray")
        
    def update_speed(self, *args):
        self.engine.setProperty('rate', self.speed_var.get())
        
    def update_volume(self, *args):
        self.engine.setProperty('volume', self.volume_var.get())
        
    def save_audio(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            self.status_label.config(text="请输入文字", foreground="red")
            return
            
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 文件", "*.mp3"), ("所有文件", "*.*")]
        )
        
        if filename:
            self.status_label.config(text="正在保存...", foreground="blue")
            
            def run_save():
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[0].id)
                engine.setProperty('rate', self.speed_var.get())
                engine.setProperty('volume', self.volume_var.get())
                engine.save_to_file(text, filename)
                engine.runAndWait()
                self.root.after(0, lambda: self.status_label.config(text=f"已保存到: {filename}", foreground="green"))
                
            thread = threading.Thread(target=run_save)
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
