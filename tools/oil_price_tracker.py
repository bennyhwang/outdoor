import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import requests
import threading
import schedule
import time
import json
import os
import datetime
import tempfile
from dateutil import parser as dateparser

class OilPriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("布伦特原油价格跟踪")
        self.root.geometry("900x700")
        
        self.data_file = os.path.join(tempfile.gettempdir(), "brent_oil_prices.json")
        self.prices = self.load_data()
        self.scheduler_running = False
        self.scheduler_thread = None
        
        self.setup_ui()
        self.plot_chart()
        self.start_scheduler()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.prices, f, indent=2)
    
    def setup_ui(self):
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill="x")
        ttk.Label(title_frame, text="布伦特原油价格跟踪", font=("Arial", 18, "bold")).pack()
        
        self.current_price_label = ttk.Label(title_frame, text="当前价格: --", font=("Arial", 14))
        self.current_price_label.pack(pady=5)
        
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="立即爬取", command=self.fetch_price).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="刷新图表", command=self.plot_chart).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="导出数据", command=self.export_data).pack(side="left", padx=5)
        
        self.scheduler_var = tk.StringVar(value="定时爬取已启动")
        ttk.Label(btn_frame, textvariable=self.scheduler_var, foreground="green").pack(side="left", padx=20)
        
        self.chart_frame = ttk.LabelFrame(self.root, text="价格走势图", padding="10")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=10, state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="x", padx=10, pady=5)
        
        self.log("应用已启动")
        self.log(f"已加载 {len(self.prices)} 条历史数据")
        self.log("定时爬取: 每天 08:00 和 20:00")
        
    def log(self, message):
        self.log_text.config(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def fetch_price(self, auto=False):
        thread = threading.Thread(target=self._fetch_price, args=(auto,))
        thread.daemon = True
        thread.start()
    
    def _fetch_price(self, auto=False):
        try:
            url = 'https://query1.finance.yahoo.com/v8/finance/chart/BZ=F'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            self.root.after(0, lambda: self.log("正在获取油价数据..."))
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
            
            result = data['chart']['result'][0]
            price = result['meta']['regularMarketPrice']
            timestamp = result['meta']['regularMarketTime']
            
            price_time = datetime.datetime.fromtimestamp(timestamp)
            price_str = price_time.strftime("%Y-%m-%d %H:%M")
            
            price_entry = {
                "datetime": price_str,
                "price": price,
                "timestamp": timestamp
            }
            
            self.prices.append(price_entry)
            self.prices = sorted(self.prices, key=lambda x: x['timestamp'])
            self.save_data()
            
            self.root.after(0, lambda: self.current_price_label.config(text=f"当前价格: ${price:.2f}"))
            self.root.after(0, lambda: self.log(f"获取成功: ${price:.2f} ({price_str})"))
            self.root.after(0, self.plot_chart)
            
            if not auto:
                self.root.after(0, lambda: messagebox.showinfo("成功", f"当前布伦特原油价格: ${price:.2f}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"获取失败: {str(e)}"))
            if not auto:
                self.root.after(0, lambda: messagebox.showerror("错误", f"获取油价失败: {str(e)}"))
    
    def plot_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if len(self.prices) < 2:
            ttk.Label(self.chart_frame, text="数据不足，请先爬取数据", foreground="gray", font=("Arial", 14)).pack(pady=50)
            return
        
        dates = [dateparser.parse(p['datetime']) for p in self.prices]
        prices = [p['price'] for p in self.prices]
        
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(dates, prices, 'b-', linewidth=2, marker='o', markersize=4)
        ax.fill_between(dates, prices, alpha=0.3)
        
        ax.set_title('布伦特原油价格走势', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格 (美元/桶)', fontsize=12)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        ax.grid(True, linestyle='--', alpha=0.7)
        
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            ax.axhline(y=min_price, color='green', linestyle='--', alpha=0.5, label=f'最低: ${min_price:.2f}')
            ax.axhline(y=max_price, color='red', linestyle='--', alpha=0.5, label=f'最高: ${max_price:.2f}')
            ax.legend(loc='upper left')
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_data(self):
        if not self.prices:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        filename = f"brent_oil_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("日期,价格\n")
            for p in self.prices:
                f.write(f"{p['datetime']},{p['price']}\n")
        
        self.log(f"数据已导出到: {filename}")
        messagebox.showinfo("成功", f"数据已导出到:\n{filename}")
    
    def start_scheduler(self):
        def run_scheduler():
            schedule.every().day.at("08:00").do(lambda: self.fetch_price(auto=True))
            schedule.every().day.at("20:00").do(lambda: self.fetch_price(auto=True))
            self.root.after(0, lambda: self.log("定时任务已设置: 08:00 和 20:00"))
            
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(30)
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def on_closing(self):
        self.scheduler_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OilPriceTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
