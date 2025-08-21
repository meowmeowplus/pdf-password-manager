# PDF Password Remover v2.0

A comprehensive tool to remove passwords from PDF files, available in both advanced GUI and command-line versions with batch processing, backup functionality, and extensive logging.

## 🚀 Features

### Core Features
- **Enhanced GUI Version**: Modern tabbed interface with batch processing
- **Advanced CLI Version**: Full command-line tool with batch processing and extensive options
- **Original Simple GUI**: Lightweight single-file interface
- **AES Encryption Support**: Works with AES-encrypted PDF files (requires PyCryptodome)
- **Batch Processing**: Process multiple PDF files at once
- **Automatic Backups**: Creates timestamped backups before processing
- **Progress Tracking**: Real-time progress for large files and batches
- **Comprehensive Logging**: Detailed logs with configurable levels

### GUI Features (Enhanced Version)
- **Tabbed Interface**: Main processing, settings, and log tabs
- **File Management**: Add multiple files, remove selected, clear all
- **Drag & Drop Support**: (Framework in place, extensible with tkinterdnd2)
- **Settings Persistence**: Remembers preferences between sessions
- **Real-time Logging**: View processing logs in real-time
- **Progress Visualization**: Progress bars for batch operations

### CLI Features
- **Batch Mode**: Process multiple files with `--batch` flag
- **Flexible Output**: Custom output directories and file names
- **Backup Control**: Enable/disable backups with `--no-backup`
- **Overwrite Control**: Automatic overwrite with `--overwrite`
- **Verbose Logging**: Detailed output with `-v/--verbose`
- **Password Options**: Provide password via command line or prompt

## 📋 Requirements

### Core Dependencies
- Python 3.7+
- PyPDF2 >= 3.0.0
- PyCryptodome >= 3.15.0 (for AES support)

### GUI Dependencies
- tkinter (included with Python)
- tkinterdnd2 >= 0.3.0 (optional, for enhanced drag-drop)

### Development Dependencies
- pytest >= 7.0.0 (for testing)
- pyinstaller >= 5.0.0 (for building executables)

## 🔧 Installation

### From Source
1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/pdf-password-remover.git
cd pdf-password-remover
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Using pip (if published):
```bash
pip install pdf-password-remover
```

## 📖 Usage

### Enhanced GUI Version (Recommended)
```bash
python pdf_password_remover_gui_enhanced.py
```

Features:
- **Main Tab**: Add files, set password, configure options
- **Settings Tab**: Configure output directory, backup settings, logging
- **Log Tab**: View real-time processing logs

### Original Simple GUI
```bash
python pdf_password_remover_gui.py
```

### Command Line Interface

#### Basic Usage
```bash
# Single file
python remove_pdf_password.py document.pdf

# With custom output
python remove_pdf_password.py document.pdf -o unlocked_document.pdf

# With password (avoid for security)
python remove_pdf_password.py document.pdf -p "password123"
```

#### Batch Processing
```bash
# Process multiple files
python remove_pdf_password.py *.pdf --batch --output-dir ./unlocked

# Batch with options
python remove_pdf_password.py file1.pdf file2.pdf file3.pdf --batch --no-backup --overwrite -v
```

#### Advanced Options
```bash
# All options
python remove_pdf_password.py files*.pdf \
  --batch \
  --output-dir ./output \
  --no-backup \
  --overwrite \
  --verbose \
  --password "secret123"
```

### Command Line Arguments
- `input`: PDF file(s) to process
- `-o, --output`: Output file (single mode) or directory (batch mode)
- `--output-dir`: Output directory for batch processing
- `-p, --password`: PDF password (will prompt if not provided)
- `--batch`: Enable batch processing mode
- `--no-backup`: Skip creating backup files
- `--overwrite`: Overwrite existing files without confirmation
- `-v, --verbose`: Enable verbose logging
- `--version`: Show version information

## 🔨 Building Executables

Use the included build script for comprehensive executable creation:

```bash
python build.py
```

This will create:
- `PDF_Password_Remover_CLI.exe`: Command-line version
- `PDF_Password_Remover_GUI.exe`: Enhanced GUI version
- `PDF_Password_Remover_GUI_Simple.exe`: Original simple GUI

### Manual Build (Individual)
```bash
# CLI version
pyinstaller --onefile --console --name="PDF_Password_Remover_CLI" remove_pdf_password.py

# Enhanced GUI version
pyinstaller --onefile --windowed --name="PDF_Password_Remover_GUI" pdf_password_remover_gui_enhanced.py

# Simple GUI version
pyinstaller --onefile --windowed --name="PDF_Password_Remover_GUI_Simple" pdf_password_remover_gui.py
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest test_pdf_password_remover.py -v

# With coverage
python -m pytest test_pdf_password_remover.py --cov=remove_pdf_password --cov-report=html
```

## 📁 File Structure

```
pdf-password-remover/
├── remove_pdf_password.py              # Enhanced CLI version
├── pdf_password_remover_gui.py         # Original simple GUI
├── pdf_password_remover_gui_enhanced.py # Enhanced GUI with tabs
├── test_pdf_password_remover.py        # Test suite
├── build.py                            # Build script
├── requirements.txt                    # Dependencies
├── README.md                           # This file
├── .gitignore                          # Git ignore rules
└── release/                            # Built executables (created by build.py)
```

## 🔒 Security Notes

- **Password Handling**: Passwords are masked in GUI, prompted securely in CLI
- **Backup Safety**: Automatic backups prevent data loss
- **Secure Logging**: Passwords are never logged
- **Input Validation**: Files are validated before processing
- **Error Handling**: Comprehensive error handling prevents crashes

## 🚨 Limitations

- Only works with PDF files encrypted with standard PDF encryption
- Some heavily protected or corrupted PDFs may not be supported
- AES support requires PyCryptodome installation
- Processing speed depends on PDF size and complexity

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Changelog

### v2.0 (Current)
- Enhanced GUI with tabbed interface
- Batch processing support
- Automatic backup functionality
- Comprehensive logging system
- Settings persistence
- Progress tracking
- Extensive test suite
- Improved build system

### v1.0
- Basic GUI and CLI versions
- Single file processing
- Simple password removal

## 📄 License

MIT License - feel free to use and modify.

## ⚠️ Disclaimer

This tool is intended for legitimate use only - removing passwords from PDF files you own or have authorization to modify. Users are responsible for ensuring they have the right to remove passwords from any PDF files they process.