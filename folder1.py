import json
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def analyze_folder(folder: Path) -> dict:
    ext_stats = {}  # ext -> {"count": int, "total_size": int}
    total_files = 0
    total_size = 0
    skipped = 0  # сколько файлов пропущено из-за ошибок доступа

    for root, _, files in os.walk(folder):
        for name in files:
            fp = Path(root) / name
            try:
                size = fp.stat().st_size
            except OSError:
                skipped += 1
                continue

            total_files += 1
            total_size += size

            ext = fp.suffix.lower() or "<no_ext>"
            st = ext_stats.get(ext)
            if st is None:
                st = {"count": 0, "total_size": 0}
                ext_stats[ext] = st

            st["count"] += 1
            st["total_size"] += size

    return {
        "folder": str(folder),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": total_files,
        "total_size_bytes": total_size,
        "extensions": ext_stats,
        "skipped_files": skipped,
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализ папки → JSON отчёт")
        self.geometry("820x520")

        self.folder_var = tk.StringVar()
        self.report = None

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)

        ttk.Label(top, text="Папка:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.folder_var, width=70).grid(
            row=0, column=1, sticky="we", padx=(8, 8)
        )
        ttk.Button(top, text="Выбрать…", command=self.pick_folder).grid(row=0, column=2)

        top.columnconfigure(1, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill="x", **pad)

        ttk.Button(btns, text="Анализировать", command=self.run_analysis).pack(side="left")
        ttk.Button(btns, text="Сохранить JSON…", command=self.save_json).pack(side="left", padx=(10, 0))
        ttk.Button(btns, text="Очистить", command=self.clear).pack(side="left", padx=(10, 0))

        out = ttk.Frame(self)
        out.pack(fill="both", expand=True, **pad)

        ttk.Label(out, text="Отчёт (предпросмотр JSON):").pack(anchor="w")
        self.text = tk.Text(out, wrap="none")
        self.text.pack(fill="both", expand=True, side="left")

        scroll_y = ttk.Scrollbar(out, orient="vertical", command=self.text.yview)
        scroll_y.pack(fill="y", side="right")
        self.text.configure(yscrollcommand=scroll_y.set)

    def pick_folder(self):
        path = filedialog.askdirectory(title="Выберите папку")
        if path:
            self.folder_var.set(path)

    def run_analysis(self):
        folder_str = self.folder_var.get().strip()
        if not folder_str:
            messagebox.showwarning("Нет пути", "Выберите папку.")
            return

        folder = Path(folder_str).expanduser().resolve()
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Ошибка", "Указанный путь не является папкой.")
            return

        self.text.delete("1.0", "end")
        self.text.insert("end", "Сканирование...\n")
        self.update_idletasks()

        try:
            self.report = analyze_folder(folder)
            pretty = json.dumps(self.report, ensure_ascii=False, indent=2)
            self.text.delete("1.0", "end")
            self.text.insert("end", pretty)

            messagebox.showinfo(
                "Готово",
                f"Файлов: {self.report['total_files']}\n"
                f"Размер: {self.report['total_size_bytes']} байт\n"
                f"Расширений: {len(self.report['extensions'])}\n"
                f"Пропущено (нет доступа): {self.report['skipped_files']}"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить анализ:\n{e!r}")

    def save_json(self):
        if not self.report:
            messagebox.showwarning("Нет данных", "Сначала нажмите «Анализировать».")
            return

        default_name = f"folder_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        out_path = filedialog.asksaveasfilename(
            title="Сохранить отчёт JSON",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not out_path:
            return

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(self.report, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", f"Отчёт сохранён:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e!r}")

    def clear(self):
        self.report = None
        self.text.delete("1.0", "end")


if __name__ == "__main__":
    App().mainloop()
