import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import threading
import pyttsx3
import time
import json

class NewsScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("新浪财经新闻爬虫")
        self.root.geometry("700x600")
        
        self.news_list = []
        self.speaking = False
        self.stop_flag = False
        
        title_frame = ttk.Frame(root, padding="10")
        title_frame.pack(fill="x")
        ttk.Label(title_frame, text="新浪财经头条新闻", font=("Arial", 18, "bold")).pack()
        
        btn_frame = ttk.Frame(root, padding="10")
        btn_frame.pack(fill="x")
        
        self.btn_fetch = ttk.Button(btn_frame, text="爬取新闻", command=self.fetch_news)
        self.btn_fetch.pack(side="left", padx=5)
        
        self.btn_speak = ttk.Button(btn_frame, text="朗读新闻", command=self.speak_news, state="disabled")
        self.btn_speak.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="停止朗读", command=self.stop_speak, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.news_frame = ttk.LabelFrame(root, text="新闻列表", padding="10")
        self.news_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.news_text = scrolledtext.ScrolledText(self.news_frame, height=20, font=("Arial", 11))
        self.news_text.pack(fill="both", expand=True)
        
        self.status_label = ttk.Label(root, text="就绪", foreground="gray", padding="5")
        self.status_label.pack(fill="x")
        
    def fetch_news(self):
        self.btn_fetch.config(state="disabled", text="爬取中...")
        self.status_label.config(text="正在爬取新浪财经头条新闻...", foreground="blue")
        self.news_text.delete("1.0", "end")
        
        thread = threading.Thread(target=self._fetch_news)
        thread.daemon = True
        thread.start()
        
    def _fetch_news(self):
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {
                "pageid": "153",
                "lid": "2516",
                "k": "",
                "num": "5",
                "page": "1"
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn/'
            }
            
            self.root.after(0, lambda: self.status_label.config(text="正在连接新浪财经...", foreground="blue"))
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            self.root.after(0, lambda: self.status_label.config(text="正在解析新闻...", foreground="blue"))
            data = response.json()
            
            self.news_list = []
            items = data.get('result', {}).get('data', [])
            
            for item in items[:5]:
                title = item.get('title', '')
                url = item.get('url', '')
                if title:
                    self.news_list.append((title, url))
            
            def update_ui():
                self.news_text.delete("1.0", "end")
                if self.news_list:
                    for i, (title, url) in enumerate(self.news_list, 1):
                        self.news_text.insert("end", f"{i}. {title}\n\n")
                    self.btn_speak.config(state="normal")
                    self.status_label.config(text=f"成功爬取 {len(self.news_list)} 条新闻", foreground="green")
                else:
                    self.news_text.insert("end", "未找到新闻，请检查网络连接")
                    self.status_label.config(text="未找到新闻", foreground="red")
                self.btn_fetch.config(state="normal", text="爬取新闻")
                
            self.root.after(0, update_ui)
            
        except Exception as e:
            def update_ui():
                self.news_text.delete("1.0", "end")
                self.news_text.insert("end", f"爬取失败: {str(e)}")
                self.status_label.config(text="爬取失败", foreground="red")
                self.btn_fetch.config(state="normal", text="爬取新闻")
            self.root.after(0, update_ui)
            
    def speak_news(self):
        if not self.news_list:
            return
            
        self.speaking = True
        self.stop_flag = False
        self.btn_speak.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="正在朗读...", foreground="blue")
        
        thread = threading.Thread(target=self._speak_news)
        thread.daemon = True
        thread.start()
        
    def _speak_news(self):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        for i, (title, _) in enumerate(self.news_list):
            if self.stop_flag:
                break
                
            news_text = f"第{i+1}条新闻。{title}"
            
            def update_status():
                self.status_label.config(text=f"正在朗读第 {i+1} 条...", foreground="blue")
            self.root.after(0, update_status)
            
            engine.say(news_text)
            engine.runAndWait()
            
            time.sleep(0.5)
            
        def finish():
            self.speaking = False
            self.btn_speak.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.status_label.config(text="朗读完成", foreground="green")
            
        self.root.after(0, finish)
        
    def stop_speak(self):
        self.stop_flag = True
        self.status_label.config(text="正在停止...", foreground="orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsScraper(root)
    root.mainloop()
