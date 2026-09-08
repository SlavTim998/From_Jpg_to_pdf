import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from PIL import Image, ImageTk, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


class PhotoCard(ttk.Frame):
    """Карточка изображения в списке с поддержкой drag-and-drop."""

    def __init__(self, master, app, index, path, thumb):
        super().__init__(master, style="Card.TFrame", padding=(8, 8))
        self.app = app
        self.index = index
        self.path = path
        self.thumb = thumb

        self.columnconfigure(2, weight=1)

        self.grip = ttk.Label(self, text="⋮⋮", style="Grip.TLabel", cursor="hand2")
        self.grip.grid(row=0, column=0, rowspan=2, padx=(0, 8), sticky="ns")

        self.image_label = ttk.Label(self, image=self.thumb, style="Thumb.TLabel", cursor="hand2")
        self.image_label.grid(row=0, column=1, rowspan=2, padx=(0, 10), sticky="w")

        filename = os.path.basename(path)
        self.name_label = ttk.Label(
            self,
            text=f"{index + 1}.  {filename}",
            style="CardTitle.TLabel",
            cursor="hand2"
        )
        self.name_label.grid(row=0, column=2, sticky="sw")

        meta = self.app.get_image_meta(path)
        self.meta_label = ttk.Label(
            self,
            text=meta,
            style="CardMeta.TLabel",
            cursor="hand2"
        )
        self.meta_label.grid(row=1, column=2, sticky="nw", pady=(3, 0))

        self.delete_btn = ttk.Button(
            self,
            text="✕",
            width=3,
            style="Ghost.TButton",
            command=lambda: self.app.remove_at(self.index)
        )
        self.delete_btn.grid(row=0, column=3, rowspan=2, padx=(8, 0), sticky="e")

        for widget in (self, self.grip, self.image_label, self.name_label, self.meta_label):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_motion)
            widget.bind("<ButtonRelease-1>", self._drag_end)
            widget.bind("<Button-1>", self._select, add="+")

    def _select(self, event=None):
        self.app.select_index(self.index)

    def _drag_start(self, event):
        self.app.begin_drag(self.index, event)

    def _drag_motion(self, event):
        self.app.drag_motion(event)

    def _drag_end(self, event):
        self.app.end_drag(event)


class PhotoToPDFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo PDF Studio")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.files = []
        self.thumbnails = {}
        self.selected_index = None
        self.preview_photo = None
        self.drag_from = None
        self.drag_target = None

        self._configure_window()
        self._configure_styles()
        self._build_ui()
        self._bind_shortcuts()

    def _configure_window(self):
        self.configure(bg="#eceff3")
        try:
            self.iconname("Photo PDF Studio")
        except Exception:
            pass

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#eceff3"
        panel = "#ffffff"
        border = "#d6dbe1"
        text = "#20242a"
        muted = "#6c7480"
        accent = "#2f6fed"
        accent_hover = "#245dcc"
        selection = "#eaf1ff"

        style.configure(".", font=("Segoe UI", 10), background=bg, foreground=text)
        style.configure("App.TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel)
        style.configure("Toolbar.TFrame", background="#f7f8fa")
        style.configure("Status.TFrame", background="#f7f8fa")
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"), background=panel, foreground=text)
        style.configure("Muted.TLabel", font=("Segoe UI", 9), background=panel, foreground=muted)
        style.configure("Status.TLabel", font=("Segoe UI", 9), background="#f7f8fa", foreground=muted)
        style.configure("Toolbar.TButton", font=("Segoe UI", 9), padding=(12, 7))
        style.map("Toolbar.TButton", background=[("active", "#e9edf2")])
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 9), background=accent, foreground="#ffffff", borderwidth=0)
        style.map("Primary.TButton", background=[("active", accent_hover), ("pressed", accent_hover)], foreground=[("disabled", "#d7dbe2")])
        style.configure("Ghost.TButton", padding=(4, 2), relief="flat")
        style.map("Ghost.TButton", background=[("active", "#f1f3f6")])
        style.configure("Card.TFrame", background=panel, bordercolor=border, relief="solid", borderwidth=1)
        style.configure("CardSelected.TFrame", background=selection, bordercolor=accent, relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background=panel, foreground=text, font=("Segoe UI", 10, "bold"))
        style.configure("CardMeta.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))
        style.configure("CardSelectedTitle.TLabel", background=selection, foreground=text, font=("Segoe UI", 10, "bold"))
        style.configure("CardSelectedMeta.TLabel", background=selection, foreground=muted, font=("Segoe UI", 9))
        style.configure("Grip.TLabel", background=panel, foreground="#9aa2ad", font=("Segoe UI", 15, "bold"))
        style.configure("GripSelected.TLabel", background=selection, foreground=accent, font=("Segoe UI", 15, "bold"))
        style.configure("Thumb.TLabel", background=panel)
        style.configure("ThumbSelected.TLabel", background=selection)

        self.colors = {"bg": bg, "panel": panel, "border": border, "text": text, "muted": muted, "accent": accent, "selection": selection}

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True)

        toolbar = ttk.Frame(root, style="Toolbar.TFrame", padding=(12, 8))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="＋ Добавить фотографии", command=self.add_images, style="Toolbar.TButton").pack(side="left")
        ttk.Button(toolbar, text="Удалить", command=self.remove_selected, style="Toolbar.TButton").pack(side="left", padx=(6, 0))
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(toolbar, text="↑ Выше", command=self.move_up, style="Toolbar.TButton").pack(side="left")
        ttk.Button(toolbar, text="↓ Ниже", command=self.move_down, style="Toolbar.TButton").pack(side="left", padx=(6, 0))
        ttk.Button(toolbar, text="Очистить", command=self.clear_all, style="Toolbar.TButton").pack(side="left", padx=(6, 0))
        ttk.Button(toolbar, text="Создать PDF", command=self.export_pdf, style="Primary.TButton").pack(side="right")

        content = ttk.Frame(root, style="App.TFrame", padding=(14, 14, 14, 8))
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=5)
        content.columnconfigure(1, weight=4)
        content.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(content, style="Panel.TFrame", padding=14)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        ttk.Label(left_panel, text="Страницы PDF", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.count_label = ttk.Label(left_panel, text="Добавьте фотографии. Перетаскивайте карточки мышью, чтобы менять порядок.", style="Muted.TLabel")
        self.count_label.grid(row=1, column=0, sticky="w", pady=(3, 12))

        list_container = ttk.Frame(left_panel, style="Panel.TFrame")
        list_container.grid(row=2, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(list_container, background=self.colors["panel"], highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.cards_frame = ttk.Frame(self.canvas, style="Panel.TFrame")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.cards_frame.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_inner_frame)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        right_panel = ttk.Frame(content, style="Panel.TFrame", padding=14)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(2, weight=1)
        ttk.Label(right_panel, text="Предпросмотр", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.preview_name = ttk.Label(right_panel, text="Файл не выбран", style="Muted.TLabel")
        self.preview_name.grid(row=1, column=0, sticky="w", pady=(3, 12))

        preview_frame = tk.Frame(right_panel, background="#f3f5f8", highlightbackground=self.colors["border"], highlightthickness=1)
        preview_frame.grid(row=2, column=0, sticky="nsew")
        preview_frame.grid_propagate(False)
        self.preview_label = tk.Label(preview_frame, text="Выберите фотографию слева", bg="#f3f5f8", fg=self.colors["muted"], font=("Segoe UI", 10), compound="center")
        self.preview_label.pack(fill="both", expand=True, padx=18, pady=18)
        self.preview_label.bind("<Configure>", lambda e: self.refresh_preview())

        info = ttk.Frame(right_panel, style="Panel.TFrame")
        info.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        info.columnconfigure(0, weight=1)
        self.order_info = ttk.Label(info, text="Порядок страниц задаётся списком слева.", style="Muted.TLabel")
        self.order_info.grid(row=0, column=0, sticky="w")
        ttk.Button(info, text="Сохранить как PDF", command=self.export_pdf, style="Primary.TButton").grid(row=1, column=0, sticky="ew", pady=(10, 0))

        status = ttk.Frame(root, style="Status.TFrame", padding=(12, 5))
        status.pack(fill="x")
        self.status_var = tk.StringVar(value="Готово")
        ttk.Label(status, textvariable=self.status_var, style="Status.TLabel").pack(side="left")
        ttk.Label(status, text="Ctrl+O: добавить   Ctrl+S: PDF   Delete: удалить   Alt+↑/↓: порядок", style="Status.TLabel").pack(side="right")
        self.refresh_cards()

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: self.add_images())
        self.bind("<Control-s>", lambda e: self.export_pdf())
        self.bind("<Delete>", lambda e: self.remove_selected())
        self.bind("<Alt-Up>", lambda e: self.move_up())
        self.bind("<Alt-Down>", lambda e: self.move_down())

    def refresh_cards(self):
        for child in self.cards_frame.winfo_children():
            child.destroy()
        if not self.files:
            ttk.Label(self.cards_frame, text="Нет фотографий\n\nНажмите «Добавить фотографии»", style="Muted.TLabel", anchor="center", justify="center").pack(fill="both", expand=True, pady=120)
            self.count_label.configure(text="0 фотографий")
            self.selected_index = None
            self.clear_preview()
            return
        for i, path in enumerate(self.files):
            card = PhotoCard(self.cards_frame, self, i, path, self.get_thumbnail(path))
            card.pack(fill="x", pady=(0, 8))
            if i == self.selected_index:
                self._apply_card_selected_style(card, True)
        count = len(self.files)
        suffix = "фотография" if count == 1 else "фотографии" if 2 <= count <= 4 else "фотографий"
        self.count_label.configure(text=f"{count} {suffix} · Перетаскивайте карточки мышью для изменения порядка.")
        self.after_idle(self._update_scrollregion)

    def _apply_card_selected_style(self, card, selected):
        card.configure(style="CardSelected.TFrame" if selected else "Card.TFrame")
        card.name_label.configure(style="CardSelectedTitle.TLabel" if selected else "CardTitle.TLabel")
        card.meta_label.configure(style="CardSelectedMeta.TLabel" if selected else "CardMeta.TLabel")
        card.grip.configure(style="GripSelected.TLabel" if selected else "Grip.TLabel")
        card.image_label.configure(style="ThumbSelected.TLabel" if selected else "Thumb.TLabel")

    def select_index(self, index):
        if 0 <= index < len(self.files):
            self.selected_index = index
            self.refresh_cards()
            self.refresh_preview()

    def get_thumbnail(self, path):
        key = (path, 112, 76)
        if key in self.thumbnails:
            return self.thumbnails[key]
        try:
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im)
                im.thumbnail((112, 76), Image.LANCZOS)
                canvas = Image.new("RGB", (112, 76), "#eef1f5")
                rgb = im.convert("RGB")
                canvas.paste(rgb, ((112 - rgb.width) // 2, (76 - rgb.height) // 2))
                photo = ImageTk.PhotoImage(canvas)
        except Exception:
            photo = ImageTk.PhotoImage(Image.new("RGB", (112, 76), "#e1e5ea"))
        self.thumbnails[key] = photo
        return photo

    def get_image_meta(self, path):
        try:
            size_kb = os.path.getsize(path) / 1024
            with Image.open(path) as im:
                w, h = im.size
                fmt = (im.format or Path(path).suffix.lstrip(".")).upper()
            size_text = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.0f} KB"
            return f"{w} × {h} px   ·   {fmt}   ·   {size_text}"
        except Exception:
            return "Не удалось прочитать параметры изображения"

    def begin_drag(self, index, event):
        self.drag_from = index
        self.drag_target = index
        self.select_index(index)
        self.config(cursor="fleur")

    def drag_motion(self, event):
        if self.drag_from is None:
            return
        y_root = event.y_root
        children = self.cards_frame.winfo_children()
        if not children:
            return
        target = self.drag_from
        for i, child in enumerate(children):
            if not isinstance(child, PhotoCard):
                continue
            if y_root < child.winfo_rooty() + child.winfo_height() / 2:
                target = i
                break
            target = i
        if target != self.drag_target:
            self.drag_target = target
            self._preview_reorder(self.drag_from, target)
            self.drag_from = target
        canvas_top = self.canvas.winfo_rooty()
        canvas_bottom = canvas_top + self.canvas.winfo_height()
        if y_root < canvas_top + 35:
            self.canvas.yview_scroll(-1, "units")
        elif y_root > canvas_bottom - 35:
            self.canvas.yview_scroll(1, "units")

    def _preview_reorder(self, old_index, new_index):
        if old_index == new_index or not (0 <= old_index < len(self.files) and 0 <= new_index < len(self.files)):
            return
        item = self.files.pop(old_index)
        self.files.insert(new_index, item)
        self.selected_index = new_index
        self.refresh_cards()

    def end_drag(self, event=None):
        if self.drag_from is not None:
            self.status_var.set("Порядок страниц изменён")
        self.drag_from = None
        self.drag_target = None
        self.config(cursor="")

    def add_images(self):
        paths = filedialog.askopenfilenames(title="Добавить фотографии", filetypes=[("Изображения", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff"), ("JPEG", "*.jpg *.jpeg"), ("PNG", "*.png"), ("Все файлы", "*.*")])
        if not paths:
            return
        added = 0
        first_added = len(self.files)
        for path in paths:
            p = Path(path)
            if p.suffix.lower() in SUPPORTED_EXTENSIONS and str(p) not in self.files:
                self.files.append(str(p))
                added += 1
        if added:
            self.selected_index = first_added
            self.refresh_cards()
            self.refresh_preview()
            self.status_var.set(f"Добавлено: {added}")

    def remove_at(self, index):
        if not (0 <= index < len(self.files)):
            return
        removed = self.files.pop(index)
        self.thumbnails = {k: v for k, v in self.thumbnails.items() if k[0] != removed}
        if not self.files:
            self.selected_index = None
        elif self.selected_index is None:
            self.selected_index = 0
        else:
            self.selected_index = min(index, len(self.files) - 1)
        self.refresh_cards()
        self.refresh_preview()
        self.status_var.set("Фотография удалена")

    def remove_selected(self):
        if self.selected_index is not None:
            self.remove_at(self.selected_index)

    def clear_all(self):
        if self.files and messagebox.askyesno("Очистить список", "Удалить все фотографии из проекта?"):
            self.files.clear()
            self.thumbnails.clear()
            self.selected_index = None
            self.refresh_cards()
            self.status_var.set("Список очищен")

    def move_up(self):
        i = self.selected_index
        if i is None or i <= 0:
            return
        self.files[i - 1], self.files[i] = self.files[i], self.files[i - 1]
        self.selected_index = i - 1
        self.refresh_cards(); self.refresh_preview(); self.status_var.set("Страница перемещена выше")

    def move_down(self):
        i = self.selected_index
        if i is None or i >= len(self.files) - 1:
            return
        self.files[i + 1], self.files[i] = self.files[i], self.files[i + 1]
        self.selected_index = i + 1
        self.refresh_cards(); self.refresh_preview(); self.status_var.set("Страница перемещена ниже")

    def clear_preview(self):
        self.preview_photo = None
        self.preview_label.configure(image="", text="Выберите фотографию слева")
        self.preview_name.configure(text="Файл не выбран")
        self.order_info.configure(text="Порядок страниц задаётся списком слева.")

    def refresh_preview(self):
        i = self.selected_index
        if i is None or not (0 <= i < len(self.files)):
            self.clear_preview(); return
        path = self.files[i]
        self.preview_name.configure(text=os.path.basename(path))
        self.order_info.configure(text=f"Страница {i + 1} из {len(self.files)}")
        try:
            max_w = max(260, self.preview_label.winfo_width() - 30)
            max_h = max(260, self.preview_label.winfo_height() - 30)
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im)
                im.thumbnail((max_w, max_h), Image.LANCZOS)
                self.preview_photo = ImageTk.PhotoImage(im.convert("RGB"))
            self.preview_label.configure(image=self.preview_photo, text="")
        except Exception as exc:
            self.preview_photo = None
            self.preview_label.configure(image="", text=f"Не удалось открыть изображение:\n{exc}")

    def export_pdf(self):
        if not self.files:
            messagebox.showwarning("Нет фотографий", "Сначала добавьте хотя бы одну фотографию.")
            return
        output_path = filedialog.asksaveasfilename(title="Сохранить PDF", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="photos.pdf")
        if not output_path:
            return
        pages = []
        try:
            self.status_var.set("Создание PDF...")
            self.update_idletasks()
            for n, path in enumerate(self.files, start=1):
                self.status_var.set(f"Подготовка страницы {n} из {len(self.files)}...")
                self.update_idletasks()
                with Image.open(path) as im:
                    im = ImageOps.exif_transpose(im)
                    if im.mode in ("RGBA", "LA"):
                        rgba = im.convert("RGBA")
                        background = Image.new("RGB", rgba.size, "white")
                        background.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
                        page = background
                    elif im.mode == "P":
                        rgba = im.convert("RGBA")
                        background = Image.new("RGB", rgba.size, "white")
                        background.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
                        page = background
                    else:
                        page = im.convert("RGB")
                    pages.append(page.copy())
            pages[0].save(output_path, "PDF", save_all=True, append_images=pages[1:], resolution=100.0)
            self.status_var.set(f"PDF создан: {output_path}")
            messagebox.showinfo("Готово", f"PDF успешно создан:\n{output_path}")
        except Exception as exc:
            self.status_var.set("Ошибка при создании PDF")
            messagebox.showerror("Ошибка", f"Не удалось создать PDF:\n{exc}")
        finally:
            for page in pages:
                try: page.close()
                except Exception: pass

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner_frame(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_containing(event.x_root, event.y_root):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == "__main__":
    app = PhotoToPDFApp()
    app.mainloop()
