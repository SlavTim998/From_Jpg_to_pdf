<div align="center">

<img src="assets/banner.png" alt="Photo PDF Studio" width="100%" />

# Photo PDF Studio

**Современное desktop-приложение на Python для объединения фотографий в один PDF.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-EXE-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

</div>

## 📥 Скачать для Windows

Готовый файл находится в репозитории:

**`dist/PhotoPDFStudio.exe`**

Также GitHub Actions автоматически собирает свежий `.exe` из исходников. Откройте **Actions → Build Windows EXE → последний успешный запуск → Artifacts → PhotoPDFStudio-Windows**.

## ✨ Возможности

- JPG, JPEG, PNG, WebP, BMP и TIFF;
- все изображения отображаются сразу карточками с миниатюрами;
- имя, разрешение, формат и размер каждого файла;
- **Drag & Drop** для изменения порядка страниц;
- кнопки перемещения вверх и вниз;
- крупный предпросмотр выбранной фотографии;
- удаление отдельных изображений и очистка списка;
- автоматический учёт EXIF-поворота;
- корректная обработка прозрачных PNG/WebP;
- экспорт всех фотографий в один PDF;
- удобные горячие клавиши.

## 🚀 Запуск из исходников

```bash
git clone https://github.com/SlavTim998/From_Jpg_to_pdf.git
cd From_Jpg_to_pdf
python -m pip install -r requirements.txt
python app.py
```

## ⌨️ Горячие клавиши

| Комбинация | Действие |
|---|---|
| `Ctrl + O` | Добавить фотографии |
| `Ctrl + S` | Создать PDF |
| `Delete` | Удалить выбранную фотографию |
| `Alt + ↑` | Переместить выше |
| `Alt + ↓` | Переместить ниже |

## 🛠️ Сборка `.exe`

```bash
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --name PhotoPDFStudio app.py
```

После сборки файл будет находиться в `dist/PhotoPDFStudio.exe`.

## 📁 Структура проекта

```text
From_Jpg_to_pdf/
├── app.py
├── requirements.txt
├── assets/
│   ├── banner.png
│   └── icon.png
├── dist/
│   └── PhotoPDFStudio.exe
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── .gitignore
├── LICENSE
└── README.md
```

## 📄 Лицензия

MIT — см. [LICENSE](LICENSE).
