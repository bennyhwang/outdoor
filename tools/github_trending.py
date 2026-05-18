import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import threading
import schedule
import time
import json
import os
import datetime

class GitHubTrendingCrawler:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub 高星项目爬虫")
        self.root.geometry("900x700")
        
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_projects.json")
        self.projects = self.load_data()
        self.is_running = False
        
        self.setup_ui()
        self.start_scheduler()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
    
    def setup_ui(self):
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill="x")
        ttk.Label(title_frame, text="GitHub 高星项目爬虫", font=("Arial", 18, "bold")).pack()
        
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill="x")
        
        ttk.Label(info_frame, text="类别: 开发工具(Developer Tools) + AI", font=("Arial", 12)).pack(side="left")
        ttk.Label(info_frame, text="定时: 每天 18:00", font=("Arial", 12), foreground="blue").pack(side="right")
        
        status_frame = ttk.Frame(self.root, padding="5")
        status_frame.pack(fill="x")
        
        self.status_label = ttk.Label(status_frame, text="等待运行...", foreground="gray")
        self.status_label.pack(side="left")
        
        self.next_run_label = ttk.Label(status_frame, text="", foreground="green")
        self.next_run_label.pack(side="right")
        
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="立即爬取", command=self.fetch_now).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="导出数据", command=self.export_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="清空数据", command=self.clear_data).pack(side="left", padx=5)
        
        list_frame = ttk.LabelFrame(self.root, text="项目列表", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("排名", "项目名称", "描述", "Stars", "语言", "类别")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("排名", text="排名")
        self.tree.heading("项目名称", text="项目名称")
        self.tree.heading("描述", text="描述")
        self.tree.heading("Stars", text="Stars")
        self.tree.heading("语言", text="语言")
        self.tree.heading("类别", text="类别")
        
        self.tree.column("排名", width=50, anchor="center")
        self.tree.column("项目名称", width=200)
        self.tree.column("描述", width=300)
        self.tree.column("Stars", width=80, anchor="center")
        self.tree.column("语言", width=100, anchor="center")
        self.tree.column("类别", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=8, state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="x", padx=10, pady=5)
        
        self.refresh_list()
        
    def log(self, message):
        self.log_text.config(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def fetch_now(self):
        thread = threading.Thread(target=self.fetch_projects)
        thread.daemon = True
        thread.start()
    
    def fetch_projects(self):
        self.is_running = True
        self.root.after(0, lambda: self.status_label.config(text="正在爬取...", foreground="blue"))
        self.root.after(0, lambda: self.log("开始爬取 GitHub 高星项目..."))
        
        categories = {
            "developer-tools": "开发工具",
            "ai": "AI"
        }
        
        new_projects = []
        
        for category, category_name in categories.items():
            self.root.after(0, lambda c=category_name: self.log(f"正在爬取类别: {c}"))
            
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": f"topic:{category} stars:>1000",
                "sort": "stars",
                "order": "desc",
                "per_page": 30
            }
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GitHub-Trending-Crawler"
            }
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    for item in items:
                        project = {
                            "name": item.get("full_name", ""),
                            "description": item.get("description", "")[:200] if item.get("description") else "无描述",
                            "stars": item.get("stargazers_count", 0),
                            "language": item.get("language", "Unknown"),
                            "category": category_name,
                            "url": item.get("html_url", ""),
                            "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        new_projects.append(project)
                    
                    self.root.after(0, lambda n=len(items), c=category_name: self.log(f"  {c}: 获取 {n} 个项目"))
                    
                elif response.status_code == 403:
                    self.root.after(0, lambda: self.log("API 频率限制，等待后再试..."))
                    time.sleep(60)
                else:
                    self.root.after(0, lambda s=response.status_code: self.log(f"请求失败: {s}"))
                    
            except Exception as e:
                self.root.after(0, lambda e=str(e): self.log(f"错误: {e}"))
            
            time.sleep(2)
        
        new_projects.sort(key=lambda x: x["stars"], reverse=True)
        
        existing_names = {p["name"] for p in self.projects}
        for p in new_projects:
            if p["name"] not in existing_names:
                self.projects.append(p)
        
        self.projects = sorted(self.projects, key=lambda x: x["stars"], reverse=True)[:100]
        self.save_data()
        
        self.root.after(0, self.refresh_list)
        self.root.after(0, lambda: self.status_label.config(text=f"已完成 (共 {len(self.projects)} 个项目)", foreground="green"))
        self.root.after(0, lambda: self.log(f"爬取完成! 共获取 {len(new_projects)} 个新项目"))
        
        self.is_running = False
    
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, project in enumerate(self.projects[:50], 1):
            self.tree.insert("", "end", values=(
                i,
                project["name"],
                project["description"][:50] + "..." if len(project["description"]) > 50 else project["description"],
                project["stars"],
                project["language"],
                project["category"]
            ))
    
    def start_scheduler(self):
        def run_scheduler():
            schedule.every().day.at("18:00").do(self.fetch_projects)
            self.root.after(0, lambda: self.log("定时任务已设置: 每天 18:00"))
            self.root.after(0, self.update_next_run)
            
            while True:
                schedule.run_pending()
                self.root.after(0, self.update_next_run)
                time.sleep(60)
        
        thread = threading.Thread(target=run_scheduler)
        thread.daemon = True
        thread.start()
    
    def update_next_run(self):
        next_run = schedule.next_run()
        if next_run:
            self.next_run_label.config(text=f"下次运行: {next_run.strftime('%H:%M')}")
    
    def export_data(self):
        if not self.projects:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        filename = f"github_projects_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', encoding='utf-8-sig') as f:
            f.write("排名,项目名称,描述,Stars,语言,类别,URL,抓取时间\n")
            for i, p in enumerate(self.projects, 1):
                f.write(f'{i},"{p["name"]}","{p["description"]}",{p["stars"]},"{p["language"]}","{p["category"]}","{p["url"]}","{p["fetched_at"]}"\n')
        
        self.log(f"数据已导出到: {filename}")
        messagebox.showinfo("成功", f"数据已导出到:\n{filename}")
    
    def clear_data(self):
        if messagebox.askyesno("确认", "确定要清空所有数据吗?"):
            self.projects = []
            self.save_data()
            self.refresh_list()
            self.log("数据已清空")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubTrendingCrawler(root)
    root.mainloop()