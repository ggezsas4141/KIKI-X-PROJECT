import ctypes, json, os, platform, subprocess, tempfile, threading, time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pathlib import Path

APP = "KIKI X PROJECT V4"
BG = "#061225"; PANEL = "#08182e"; PANEL2 = "#0b1d37"; BORDER = "#172d4d"
TEXT = "#edf4ff"; MUTED = "#8fa4c4"; GREEN = "#19e985"; RED = "#ff3548"; BLUE = "#2587ff"
ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "KIKI_X_PROJECT_V4"
BACKUP_DIR = ROOT / "backups"; BACKUP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_FILE = BACKUP_DIR / "latest_backup.json"; LOG_FILE = ROOT / "activity.log"
ROOT.mkdir(parents=True, exist_ok=True)

def log(msg):
    line = time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f: f.write(line + "\n")
    except Exception: pass
    return line

def run(args, timeout=20):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, shell=False)

def backup_data():
    try: return json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
    except Exception: return {"version": 1, "items": []}

def reg_query(path, name):
    try:
        p = run(["reg", "query", path, "/v", name], 10)
        if p.returncode: return None
        for line in p.stdout.splitlines():
            bits = line.strip().split(None, 2)
            if len(bits) >= 3 and bits[0].lower() == name.lower():
                return {"type": bits[1], "value": bits[2]}
    except Exception: pass
    return None

def reg_set(path, name, value):
    data = backup_data(); items = data.setdefault("items", [])
    if not any(x["path"].lower() == path.lower() and x["name"].lower() == name.lower() for x in items):
        items.append({"path": path, "name": name, "old": reg_query(path, name)})
        BACKUP_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    p = run(["reg", "add", path, "/v", name, "/t", "REG_DWORD", "/d", str(value), "/f"], 10)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip() or "Registry change failed")
    return f"เปลี่ยน {name} และสำรองค่าเดิมแล้ว"

def restore():
    items = backup_data().get("items", [])
    if not items: return "ไม่มี Registry ที่แอปนี้เคยสำรองไว้"
    out=[]
    for x in reversed(items):
        try:
            if x["old"] is None:
                run(["reg", "delete", x["path"], "/v", x["name"], "/f"], 10)
                out.append(x["name"] + ": ลบค่าที่แอปเพิ่ม")
            else:
                old=x["old"]
                p=run(["reg", "add", x["path"], "/v", x["name"], "/t", old["type"], "/d", old["value"], "/f"], 10)
                out.append(x["name"] + (": คืนค่าแล้ว" if p.returncode == 0 else ": คืนค่าไม่สำเร็จ"))
        except Exception as e: out.append(x["name"] + ": " + str(e))
    return "\n".join(out)

def fps_boost():
    return ("ตรวจแนวทาง FPS Boost แล้ว — ไม่มีการสุ่ม Registry\n"
            "• เปิด Windows Game Mode\n• ปิด Startup/overlay ที่ไม่ใช้\n"
            "• ใน FiveM/GTA V ลด MSAA, Grass, Extended Distance Scaling ก่อน\n"
            "• ปรับกราฟิกทีละค่าและวัด FPS/frametime ก่อน-หลัง")

def cpu_boost():
    path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
    return reg_set(path, "VisualFXSetting", 2) + "\nเป็นการลดเอฟเฟกต์ภาพ Windows ไม่ใช่การโอเวอร์คล็อก CPU"

def gpu_opt():
    return ("ไม่ได้แก้ไดรเวอร์หรือ Registry แบบไม่ทราบผล\n"
            "NVIDIA Control Panel > Manage 3D settings > Program Settings\n"
            "เพิ่ม FiveM/GTA5 แล้วทดลอง Power management mode ตามการใช้งาน\n"
            "อัปเดตไดรเวอร์จาก NVIDIA และปิด overlay ที่ไม่จำเป็น")

def ram_opt():
    return ("RAM Optimization: ไม่มีการบังคับล้าง RAM หรือปิด Pagefile\n"
            "ปิด Chrome/โปรแกรมพื้นหลังที่ไม่ใช้ และตรวจ Task Manager > Processes\n"
            "FiveM + Discord + browser อาจใช้ RAM 16GB ได้มาก ควรเหลือพื้นที่ว่าง")

def fivem_opt():
    return ("FiveM Optimization\n"
            "• ปิด FiveM ก่อนจัดการไฟล์แคช\n"
            "• อย่าลบโฟลเดอร์เกมหรือ server data แบบสุ่ม\n"
            "• RTX 3050 6GB: ลด Texture/Extended Texture Budget หาก VRAM เต็ม\n"
            "• ทดสอบทีละค่า เพราะ FPS ขึ้นกับเซิร์ฟเวอร์และสคริปต์")

def network_opt():
    return ("Network Boost — ไม่เปลี่ยน DNS/TCP อัตโนมัติ\n"
            "• ใช้สาย Ethernet ถ้าทำได้\n• หยุดดาวน์โหลด/สตรีมเบื้องหลัง\n"
            "• DNS มักไม่ลด ping ในเกมหลังเชื่อมต่อแล้ว\n"
            "• อย่าปิด IPv6 หรือสุ่มเปลี่ยน TCP autotuning")

def clean_temp():
    temp = Path(tempfile.gettempdir()); removed=0; skipped=0
    for p in temp.iterdir():
        try:
            if p.is_file() and p.stat().st_mtime < time.time()-86400:
                p.unlink(); removed+=1
        except Exception: skipped+=1
    return f"ลบไฟล์ TEMP เก่ากว่า 24 ชม. {removed} ไฟล์; ข้าม {skipped} ไฟล์\nการลบไฟล์ไม่สามารถ Restore ได้"

def ping_test():
    try:
        p = run(["ping", "-n", "4", "1.1.1.1"], 12)
        return p.stdout.strip() or p.stderr.strip() or "ไม่มีผลลัพธ์"
    except Exception as e: return str(e)


def system_monitor():
    """Return real readings where available; optional psutil and NVIDIA SMI."""
    lines = []
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        lines.append(f"CPU Usage: {cpu:.1f}%")
        lines.append(f"RAM Usage: {mem.percent:.1f}% ({mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB)")
    except ImportError:
        lines.append("CPU/RAM Usage: ติดตั้ง psutil ก่อน (pip install psutil)")
    except Exception as e:
        lines.append(f"CPU/RAM Usage: อ่านไม่ได้ ({e})")
    try:
        p = run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,driver_version", "--format=csv,noheader,nounits"], 5)
        if p.returncode == 0 and p.stdout.strip():
            parts = [x.strip() for x in p.stdout.strip().splitlines()[0].split(",")]
            if len(parts) >= 6:
                lines += [f"GPU: {parts[0]}", f"GPU Usage: {parts[1]}%", f"VRAM: {parts[2]} / {parts[3]} MB",
                          f"GPU Temperature: {parts[4]} °C", f"NVIDIA Driver: {parts[5]}"]
            else: lines.append("GPU: ได้ข้อมูลไม่ครบจาก nvidia-smi")
        else:
            lines.append("GPU Usage/Temperature: อ่านไม่ได้ (ต้องมี NVIDIA driver ที่รองรับ nvidia-smi)")
    except Exception:
        lines.append("GPU Usage/Temperature: อ่านไม่ได้ (ไม่พบ nvidia-smi)")
    return "\\n".join(lines)

def real_benchmark():
    """Small repeatable CPU workload; score is relative to this app's own timed run, not game FPS."""
    import hashlib
    payload = b"KIKI-X-PERFORMANCE-TEST" * 4096
    start = time.perf_counter()
    loops = 0
    deadline = start + 2.0
    while time.perf_counter() < deadline:
        hashlib.sha256(payload).digest()
        loops += 1
    elapsed = time.perf_counter() - start
    score = int(loops / elapsed)
    return (f"CPU micro-benchmark completed\\n"
            f"Duration: {elapsed:.2f} seconds\\n"
            f"Throughput: {score:,} SHA-256 operations/second\\n"
            "หมายเหตุ: เป็นคะแนนทดสอบ CPU แบบสั้นของแอป ไม่ใช่คะแนน FPS หรือคะแนนเทียบมาตรฐานสากล "
            "ผลขึ้นกับโปรแกรมเบื้องหลังและอุณหภูมิ")

class Dashboard:
    def __init__(self, root):
        self.root=root; root.title(APP); root.geometry("1280x790"); root.minsize(1000,680); root.configure(bg=BG)
        self.busy=False; self.current="Dashboard"; self.build(); self.log("พร้อมใช้งาน • Local-only tools • Safe profile")
    def label(self, parent, text, size=11, color=TEXT, bold=False, **kw):
        return tk.Label(parent,text=text,font=("Segoe UI",size,"bold" if bold else "normal"),fg=color,bg=kw.pop("bg",PANEL),**kw)
    def card(self,parent,title):
        f=tk.Frame(parent,bg=PANEL,highlightbackground=BORDER,highlightthickness=1)
        self.label(f,title.upper(),9,MUTED,True,bg=PANEL).pack(anchor="w",padx=15,pady=(14,8))
        return f
    def button(self,parent,text,cmd,primary=False):
        return tk.Button(parent,text=text,command=cmd,bg=GREEN if primary else "#142b4d",fg="#032116" if primary else TEXT,
          activebackground="#0fc773" if primary else "#20436f",activeforeground=TEXT,relief="flat",bd=0,
          font=("Segoe UI",9,"bold"),cursor="hand2",padx=14,pady=10)
    def build(self):
        side=tk.Frame(self.root,bg="#041023",width=205); side.pack(side="left",fill="y"); side.pack_propagate(False)
        self.label(side,"◉",34,GREEN,True,bg="#041023").pack(pady=(26,0))
        self.label(side,"KIKI X",19,TEXT,True,bg="#041023").pack()
        self.label(side,"PROJECT V4",9,GREEN,True,bg="#041023").pack(pady=(0,32))
        for name,ico in [("Dashboard","▦"),("FPS Boost","✦"),("CPU Boost","◆"),("GPU Optimization","◈"),("RAM Optimization","▤"),("FiveM Optimization","◉"),("Network Boost","⌁"),("Clean & Smooth","✧"),("Restore","↶")]:
            b=tk.Button(side,text=f"  {ico}   {name}",anchor="w",command=lambda n=name:self.select(n),
                bg="#0a2c38" if name=="Dashboard" else "#041023",fg=GREEN if name=="Dashboard" else TEXT,
                activebackground="#10344c",activeforeground=GREEN,relief="flat",bd=0,
                font=("Segoe UI",10,"bold"),padx=12,pady=12,cursor="hand2")
            b.pack(fill="x",padx=9,pady=3)
        self.label(side,"● Local-only tools\nRuns on your PC. No cloud scan.",9,MUTED,bg="#0b1a2e",justify="left",padx=10,pady=10).pack(side="bottom",fill="x",padx=10,pady=14)
        body=tk.Frame(self.root,bg=BG); body.pack(side="left",fill="both",expand=True,padx=16,pady=14)
        hero=tk.Frame(body,bg=PANEL,highlightbackground=BORDER,highlightthickness=1); hero.pack(fill="x")
        left=tk.Frame(hero,bg=PANEL); left.pack(side="left",fill="both",expand=True,padx=22,pady=18)
        self.label(left,"KIKI X DASHBOARD",9,GREEN,True).pack(anchor="w")
        self.label(left,"Your PC. Your Performance.",25,TEXT,True).pack(anchor="w",pady=(4,0))
        self.label(left,"Ryzen 5 5600  •  RTX 3050 6GB  •  RAM 16GB",10,MUTED).pack(anchor="w",pady=(5,0))
        right=tk.Frame(hero,bg=PANEL); right.pack(side="right",padx=18,pady=22)
        self.button(right,"⚡  QUICK BOOST",self.quick,True).pack(side="left",padx=5)
        self.button(right,"↻  REFRESH",self.refresh).pack(side="left",padx=5)
        cards=tk.Frame(body,bg=BG); cards.pack(fill="x",pady=12)
        self.score=self.card(cards,"Performance profile"); self.score.pack(side="left",fill="both",expand=True,padx=(0,8))
        self.label(self.score,"SAFE",25,GREEN,True).pack(anchor="w",padx=16,pady=(12,0))
        self.label(self.score,"Profile ready",10,MUTED).pack(anchor="w",padx=16,pady=(0,16))
        self.cpu=self.card(cards,"CPU / System"); self.cpu.pack(side="left",fill="both",expand=True,padx=8)
        self.label(self.cpu,"AMD Ryzen 5 5600",15,TEXT,True).pack(anchor="w",padx=15,pady=(10,2))
        self.label(self.cpu,"6 cores / 12 threads",10,MUTED).pack(anchor="w",padx=15,pady=(0,16))
        self.ram=self.card(cards,"Memory"); self.ram.pack(side="left",fill="both",expand=True,padx=8)
        self.label(self.ram,"16 GB DDR4",15,TEXT,True).pack(anchor="w",padx=15,pady=(10,2))
        self.label(self.ram,"Usage readout requires optional system monitor",9,MUTED,wraplength=190,justify="left").pack(anchor="w",padx=15,pady=(0,16))
        self.gpu=self.card(cards,"GPU Status"); self.gpu.pack(side="left",fill="both",expand=True,padx=(8,0))
        self.label(self.gpu,"RTX 3050 6GB",15,TEXT,True).pack(anchor="w",padx=15,pady=(10,2))
        self.label(self.gpu,"Driver status not queried",10,MUTED).pack(anchor="w",padx=15,pady=(0,16))
        lower=tk.Frame(body,bg=BG); lower.pack(fill="both",expand=True)
        overview=self.card(lower,"System overview"); overview.pack(side="left",fill="both",expand=True,padx=(0,8))
        self.label(overview,"◆  CPU   AMD Ryzen 5 5600",11,TEXT,True).pack(anchor="w",padx=16,pady=(10,6))
        self.label(overview,"◆  GPU   NVIDIA RTX 3050 6GB",11,TEXT,True).pack(anchor="w",padx=16,pady=6)
        self.label(overview,"◆  RAM   16 GB DDR4",11,TEXT,True).pack(anchor="w",padx=16,pady=6)
        self.label(overview,"◆  Motherboard   ASUS Prime A520M-K/CSM",10,TEXT,True).pack(anchor="w",padx=16,pady=5)
        self.label(overview,"◆  Storage   Lexar NM620 512GB SSD",10,TEXT,True).pack(anchor="w",padx=16,pady=5)
        self.label(overview,"◆  PSU   Gigabyte 550W",10,TEXT,True).pack(anchor="w",padx=16,pady=5)
        self.button(overview,"REAL-TIME MONITOR",self.show_monitor,True).pack(anchor="w",padx=16,pady=(12,4))
        self.button(overview,"RUN PERFORMANCE TEST",lambda:self.action("Performance Test",real_benchmark)).pack(anchor="w",padx=16,pady=4)
        recent=self.card(lower,"Activity / Recent optimization"); recent.pack(side="left",fill="both",expand=True,padx=8)
        self.logbox=scrolledtext.ScrolledText(recent,bg="#040d1b",fg="#d9e7ff",insertbackground="white",font=("Consolas",9),relief="flat",wrap="word",height=12)
        self.logbox.pack(fill="both",expand=True,padx=12,pady=(0,12))
        tools=self.card(lower,"Ping tools"); tools.pack(side="left",fill="both",expand=True,padx=(8,0))
        self.ping_value=self.label(tools,"— ms",26,GREEN,True); self.ping_value.pack(anchor="w",padx=16,pady=(12,3))
        self.label(tools,"Host: 1.1.1.1",10,MUTED).pack(anchor="w",padx=16)
        self.button(tools,"REFRESH PING",self.do_ping).pack(fill="x",padx=14,pady=(14,6))
        self.button(tools,"LOW PING RESET",self.network_action,True).pack(fill="x",padx=14,pady=6)
        self.label(tools,"Ping test measures reachability only; not game-server latency.",9,MUTED,wraplength=220,justify="left").pack(anchor="w",padx=14,pady=8)
        self.status=tk.Label(body,text="● READY  |  No Defender / Firewall / Anti-cheat changes",bg=BG,fg=GREEN,font=("Segoe UI",9,"bold"),anchor="w")
        self.status.pack(fill="x",pady=(10,0))
    def log(self,msg):
        line=log(msg)
        if hasattr(self,"logbox"):
            self.logbox.configure(state="normal"); self.logbox.insert("end",line+"\n"); self.logbox.see("end"); self.logbox.configure(state="disabled")
    def finish(self,title,result,err=False):
        self.log(title+"\n"+result); self.status.config(text="● ERROR" if err else "● READY  |  Completed",fg=RED if err else GREEN); self.busy=False
        messagebox.showerror(APP,result[:2200]) if err else messagebox.showinfo(title,result[:2200])
    def action(self,title,fn,confirm=False):
        if self.busy:return
        if confirm and not messagebox.askyesno(title,"ดำเนินการต่อหรือไม่?\nการลบไฟล์ TEMP ไม่สามารถคืนค่าได้"):return
        self.busy=True; self.status.config(text="● WORKING...",fg="#ffd166")
        def worker():
            try: result=fn(); self.root.after(0,lambda t=title,r=result:self.finish(t,r))
            except Exception as e: self.root.after(0,lambda t=title,err=str(e):self.finish(t,err,True))
        threading.Thread(target=worker,daemon=True).start()
    def select(self,name):
        funcs={"FPS Boost":fps_boost,"CPU Boost":cpu_boost,"GPU Optimization":gpu_opt,"RAM Optimization":ram_opt,
               "FiveM Optimization":fivem_opt,"Network Boost":network_opt,"Clean & Smooth":clean_temp,"Restore":restore}
        if name=="Dashboard":return
        if name in funcs:
            if name == "CPU Boost":
                if not messagebox.askyesno("Apply CPU/Windows setting",
                    "จะเปลี่ยนเฉพาะ VisualFXSetting ของ Windows และสำรองค่าเดิมก่อน\nนี่ไม่ใช่การโอเวอร์คล็อก CPU ต้องการดำเนินการหรือไม่?"):
                    return
            self.action(name,funcs[name],name=="Clean & Smooth" or name=="Restore")
    def quick(self):
        self.action("Quick Boost",lambda: "\n\n".join([fps_boost(),gpu_opt(),ram_opt(),fivem_opt(),
            "CPU/Windows Visual Effects: ไม่ได้เปลี่ยนอัตโนมัติ เพื่อให้กดยืนยัน Apply แยกต่างหาก"]))
    def refresh(self):
        self.log("Refresh: ตรวจข้อมูลโปรไฟล์แล้ว (ไม่แก้ค่าระบบ)")
        messagebox.showinfo(APP,"รีเฟรชข้อมูลโปรไฟล์แล้ว\nค่าการใช้งาน CPU/GPU แบบสดยังไม่ได้เปิดใช้ในรุ่นนี้")
    def show_monitor(self):
        win = tk.Toplevel(self.root)
        win.title("KIKI X — Real-time Monitor")
        win.geometry("620x430")
        win.configure(bg=BG)
        self.label(win,"REAL-TIME SYSTEM MONITOR",14,GREEN,True,bg=BG).pack(anchor="w",padx=18,pady=(18,8))
        out = scrolledtext.ScrolledText(win,bg="#040d1b",fg=TEXT,insertbackground="white",
                                       font=("Consolas",11),relief="flat",wrap="word")
        out.pack(fill="both",expand=True,padx=18,pady=8)
        def refresh_readings():
            out.configure(state="normal")
            out.delete("1.0","end")
            out.insert("end",system_monitor() + "\\n\\nUpdated: " + time.strftime("%H:%M:%S"))
            out.configure(state="disabled")
        def loop():
            if not win.winfo_exists():
                return
            def worker():
                data = system_monitor()
                self.root.after(0, lambda: update_data(data) if win.winfo_exists() else None)
            threading.Thread(target=worker, daemon=True).start()
        def update_data(data):
            out.configure(state="normal")
            out.delete("1.0","end")
            out.insert("end",data + "\\n\\nUpdated: " + time.strftime("%H:%M:%S"))
            out.configure(state="disabled")
            if win.winfo_exists():
                win.after(3000, loop)
        self.button(win,"REFRESH NOW",loop,True).pack(anchor="e",padx=18,pady=(0,14))
        loop()

    def do_ping(self):
        def work():
            result=ping_test()
            self.root.after(0,lambda:self.ping_done(result))
        threading.Thread(target=work,daemon=True).start()
    def ping_done(self,result):
        import re
        m=re.search(r"Average\s*=\s*(\d+)\s*ms",result,re.I)
        self.ping_value.config(text=(m.group(1)+" ms") if m else "N/A")
        self.log("Ping test:\n"+result); messagebox.showinfo("Ping Test",result[:1800])
    def network_action(self):
        if messagebox.askyesno("Low Ping Reset","คำสั่งนี้จะแค่ตรวจ ping และแสดงคำแนะนำ ไม่ reset Winsock/TCP อัตโนมัติ\nต้องการทดสอบ ping 1.1.1.1 หรือไม่?"):
            self.do_ping()

def main():
    if platform.system()!="Windows": print("Designed for Windows.")
    root=tk.Tk(); Dashboard(root); root.mainloop()
if __name__=="__main__":main()
