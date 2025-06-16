
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import easyocr
import datetime
import threading

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Распознаватель рукописного текста")
        self.root.minsize(400, 500)
        self.root.configure(bg="#f0f0f0")

        self.reader = easyocr.Reader(['ru', 'en'], gpu=False)
        self.path = None
        self.img = None

        self.style = ttk.Style()
        self.style.configure('TButton',
                             background="#4CAF50",
                             foreground="#4CAF50",
                             font=('Arial', 12),
                             padding=10)
        self.style.map('TButton',
                       background=[('active', '#388E3C')])

        self.frm_top = tk.Frame(root, bg="#f0f0f0")
        self.frm_top.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frm_top.grid_columnconfigure(0, weight=1)
        self.frm_top.grid_columnconfigure(1, weight=1)
        self.frm_top.grid_rowconfigure(0, weight=1)

        self.frm_pic = tk.Frame(self.frm_top, bg="#ffffff", relief="groove", bd=2)
        self.frm_pic.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.frm_pic.grid_columnconfigure(0, weight=1)
        self.frm_pic.grid_rowconfigure(0, weight=1)
        self.frm_pic.configure(width=200, height=200)
        self.frm_pic.grid_propagate(False)

        self.frm_pic.config(highlightbackground="green", highlightthickness=2)


        self.lbl_pic = tk.Label(self.frm_pic, bg="#ffffff")
        self.lbl_pic.grid(row=0, column=0, sticky="nsew")

        self.frm_result = tk.Frame(self.frm_top, bg="#ffffff", relief="groove", bd=2)
        self.frm_result.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.frm_result.grid_columnconfigure(0, weight=1)
        self.frm_result.grid_rowconfigure(0, weight=1)
        self.frm_result.configure(width=200, height=200)
        self.frm_result.grid_propagate(False)


        self.frm_result.config(highlightbackground="green", highlightthickness=2)


        self.txt = tk.Text(self.frm_result, wrap=tk.WORD, font=('Arial', 12), bg="#ffffff", fg="#333333")
        self.txt.grid(row=0, column=0, sticky="nsew")

        self.frm_btn = tk.Frame(root, bg="#f0f0f0")
        self.frm_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.frm_btn.grid_columnconfigure(0, weight=1)
        self.frm_btn.grid_columnconfigure(1, weight=1)
        self.frm_btn.grid_columnconfigure(2, weight=1)


        try:
            self.load_icon = tk.PhotoImage(file="load.png")
            self.rec_icon = tk.PhotoImage(file="recognize.png")
            self.save_icon = tk.PhotoImage(file="save.png")
        except tk.TclError:
            print("Не удалось загрузить иконки.  Используются текстовые кнопки.")
            self.load_icon = None
            self.rec_icon = None
            self.save_icon = None



        self.btn_load = ttk.Button(self.frm_btn, text="Загрузить", command=self.load)
        self.btn_load.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        if self.load_icon:
            self.btn_load.config(image=self.load_icon, compound=tk.LEFT)

        self.btn_rec = ttk.Button(self.frm_btn, text="Распознать", command=self.recognize, state=tk.DISABLED)
        self.btn_rec.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        if self.rec_icon:
            self.btn_rec.config(image=self.rec_icon, compound=tk.LEFT)


        self.btn_save = ttk.Button(self.frm_btn, text="Сохранить", command=self.save, state=tk.DISABLED)
        self.btn_save.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        if self.save_icon:
            self.btn_save.config(image=self.save_icon, compound=tk.LEFT)


        self.progressbar = ttk.Progressbar(root, orient=tk.HORIZONTAL,
                                             mode='indeterminate')
        self.progressbar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.progressbar.pack_forget()

        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=0)
        root.grid_columnconfigure(0, weight=1)


    def load(self):
        ftypes = [("Фото", "*.png *.jpg *.jpeg *.bmp"), ("Все", "*.*")]
        p = filedialog.askopenfilename(title="Выбрать фото", filetypes=ftypes)
        if p:
            try:
                im = Image.open(p)
                w, h = im.size
                fw, fh = self.frm_pic.winfo_width(), self.frm_pic.winfo_height()
                if fw == 1 and fh == 1:
                    fw, fh = 300, 350
                r = min(fw / w, fh / h)
                new_size = (int(w * r), int(h * r))
                im = im.resize(new_size, Image.LANCZOS)
                self.img = ImageTk.PhotoImage(im)
                self.lbl_pic.config(image=self.img)
                self.path = p
                self.btn_rec.config(state=tk.NORMAL)
                self.txt.delete(1.0, tk.END)
                self.btn_save.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить фото:\n{e}")


    def recognize(self):
        if not self.path:
            messagebox.showwarning("Внимание", "Сначала загрузите фото")
            return

        self.txt.delete(1.0, tk.END)
        self.btn_rec.config(state=tk.DISABLED)
        self.btn_load.config(state=tk.DISABLED)
        self.progressbar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.progressbar.start()

        threading.Thread(target=self.do_recognition).start()

    def do_recognition(self):
        try:
            res = self.reader.readtext(self.path, detail=0, paragraph=True)
            txt = "\n".join(res)

            self.root.after(0, self.update_text, txt)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Ошибка", str(e))

        finally:
            self.root.after(0, self.finish_recognition)

    def update_text(self, text):
        self.txt.insert(tk.END, text)
        self.btn_save.config(state=tk.NORMAL)

    def finish_recognition(self):
        self.progressbar.stop()
        self.progressbar.grid_forget()
        self.btn_rec.config(state=tk.NORMAL)
        self.btn_load.config(state=tk.NORMAL)

    def save(self):
        txt = self.txt.get(1.0, tk.END).strip()
        if not txt:
            messagebox.showwarning("Внимание", "Нет текста для сохранения")
            return

        fname = f"txt_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.txt"
        p = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Текст", "*.txt"), ("Все", "*.*")],
                                         initialfile=fname,
                                         title="Сохранить файл")
        if p:
            try:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(txt)
                messagebox.showinfo("Готово", f"Сохранено:\n{p}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))



if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
