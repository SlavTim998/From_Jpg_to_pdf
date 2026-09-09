<div align="center">

# Photo PDF Studio

**Современное desktop-приложение на Python для объединения фотографий в один PDF.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-EXE-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2ea44f.svg)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-6e40c9)

**[⬇ Скачать PhotoPDFStudio.exe](dist/PhotoPDFStudio.exe)**

</div>

## 🚀 О проекте

**Photo PDF Studio** — локальное приложение для Windows, которое позволяет загрузить набор фотографий, визуально выставить их порядок и объединить в один PDF-файл. Фотографии никуда не отправляются: конвертация происходит на вашем компьютере.

## ✨ Возможности

- поддержка **JPG, JPEG, PNG, WebP, BMP и TIFF**;
- все фотографии сразу отображаются в виде удобных карточек;
- миниатюра и **название каждого файла**;
- отображение разрешения, формата и размера изображения;
- **Drag & Drop** — зажмите карточку и перетащите её выше или ниже;
- кнопки перемещения страниц вверх/вниз;
- большой предпросмотр выбранного изображения;
- удаление отдельных фотографий и полная очистка списка;
- автоматический учёт **EXIF-поворота**;
- прозрачный фон PNG/WebP корректно заменяется белым при экспорте;
- объединение всех страниц в **один PDF**;
- удобные горячие клавиши;
- готовая Windows-версия `.exe`.

## 📥 Windows EXE

Самый простой вариант — скачать готовый файл:

### **[PhotoPDFStudio.exe](dist/PhotoPDFStudio.exe)**

GitHub Actions также автоматически пересобирает Windows-версию из актуального `app.py`. Свежую сборку можно получить во вкладке **Actions → Build Windows EXE → Artifacts → PhotoPDFStudio-Windows**.

## 🐍 Запуск из исходников

Требуется Python 3.10 или новее.

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
| `Alt + ↑` | Переместить фотографию выше |
| `Alt + ↓` | Переместить фотографию ниже |

## 🔨 Сборка `.exe` вручную

```bash
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconsole --onefile --clean --name PhotoPDFStudio app.py
```

Результат:

```text
dist/PhotoPDFStudio.exe
```

## 📁 Структура проекта

```text
From_Jpg_to_pdf/
├── app.py
├── requirements.txt
├── assets/
│   ├── banner.svg
│   └── icon.svg
├── dist/
│   └── PhotoPDFStudio.exe
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── .gitignore
├── LICENSE
└── README.md
```

## 🔒 Конфиденциальность

Приложение работает локально. Выбранные изображения не загружаются на внешние серверы и используются только для создания PDF на вашем компьютере.

## 🤝 Open Source

Проект открыт для улучшений. Можно создавать Issues, предлагать изменения интерфейса, новые настройки PDF и поддержку дополнительных форматов.

## 📄 Лицензия

Распространяется по лицензии **MIT** — см. [`LICENSE`](LICENSE).

---

<div align="center">

Made with Python • Photo PDF Studio

</div>
