# PDF Password Manager v2.0

A comprehensive tool to **add and remove passwords** from PDF files, available in both advanced GUI and command-line versions with batch processing, backup functionality, and extensive logging.

## 🚀 Features

### Core Features
- **🔓 Password Removal**: Remove passwords from encrypted PDFs
- **🔒 Password Addition**: Add password protection to PDFs with custom permissions
- **📱 Modern GUI**: Tabbed interface with separate Add/Remove sections
- **⚙️ Advanced CLI**: Full command-line tool with batch processing
- **🔐 AES Encryption Support**: Works with AES-encrypted PDF files (requires PyCryptodome)
- **📦 Batch Processing**: Process multiple PDF files at once
- **💾 Automatic Backups**: Creates timestamped backups before processing
- **📊 Progress Tracking**: Real-time progress for large files and batches
- **📋 Comprehensive Logging**: Detailed logs with configurable levels

### GUI Features
- **📑 Separate Tabs**: Dedicated "Remove Password" and "Add Password" tabs
- **📁 File Management**: Add multiple files, remove selected, clear all
- **🎛️ Settings Persistence**: Remembers preferences between sessions
- **📊 Real-time Logging**: View processing logs in real-time
- **🔧 Permission Control**: Fine-grained PDF permissions for password addition
- **📈 Progress Visualization**: Progress bars for batch operations

### CLI Features
- **🎯 Dual Mode**: `--add` or `--remove` operations
- **📦 Batch Mode**: Process multiple files with `--batch` flag
- **📂 Flexible Output**: Custom output directories and file names
- **💾 Backup Control**: Enable/disable backups with `--no-backup`
- **🔄 Overwrite Control**: Automatic overwrite with `--overwrite`
- **📝 Verbose Logging**: Detailed output with `-v/--verbose`
- **🔑 Advanced Options**: Owner passwords, permission flags

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

### New Complete GUI (Recommended)
```bash
python pdf_password_manager_gui.py
```

Features:
- **Remove Password Tab**: Select encrypted PDFs and remove protection
- **Add Password Tab**: Select PDFs and add password protection with permissions
- **Settings Tab**: Configure output directory, backup settings, logging
- **Log Tab**: View real-time processing logs

### Enhanced GUI (Legacy)
```bash
python pdf_password_remover_gui_enhanced.py  # Remove-only functionality
```

### Original Simple GUI (Legacy)
```bash
python pdf_password_remover_gui.py  # Remove-only functionality
```

### Command Line Interface

#### Remove Passwords
```bash
# Single file
python remove_pdf_password.py document.pdf --remove

# With custom output
python remove_pdf_password.py document.pdf --remove -o unlocked_document.pdf

# Batch processing
python remove_pdf_password.py *.pdf --remove --batch --output-dir ./unlocked
```

#### Add Passwords
```bash
# Single file with password
python remove_pdf_password.py document.pdf --add --password "secret123"

# With custom permissions
python remove_pdf_password.py document.pdf --add --password "secret123" --no-modify --no-copy

# Batch with owner password
python remove_pdf_password.py *.pdf --add --batch --password "user123" --owner-password "admin456" --output-dir ./protected
```

#### Advanced Examples
```bash
# Remove passwords with all options
python remove_pdf_password.py files*.pdf --remove --batch --output-dir ./unlocked --no-backup --overwrite --verbose

# Add passwords with restricted permissions
python remove_pdf_password.py document.pdf --add --password "user123" --owner-password "admin456" --no-print --no-modify --no-copy
```

### Command Line Arguments

**Operations:**
- `--add`: Add password protection to PDF(s)
- `--remove`: Remove password protection from PDF(s)

**Files & Output:**
- `input`: PDF file(s) to process
- `-o, --output`: Output file (single mode) or directory (batch mode)
- `--output-dir`: Output directory for batch processing

**Password Options:**
- `-p, --password`: PDF password (will prompt if not provided)
- `--owner-password`: Owner password (for add mode, defaults to user password)

**Permissions (Add Mode Only):**
- `--no-print`: Disable printing
- `--no-modify`: Disable content modification
- `--no-copy`: Disable copying/extracting
- `--no-annotate`: Disable annotations

**Processing Options:**
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
- `PDF_Password_Manager_CLI.exe`: Full command-line version (add/remove)
- `PDF_Password_Manager_GUI.exe`: Complete GUI with add/remove tabs
- `PDF_Password_Remover_GUI.exe`: Legacy enhanced GUI (remove-only)
- `PDF_Password_Remover_GUI_Simple.exe`: Legacy simple GUI (remove-only)

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
pdf-password-manager/
├── remove_pdf_password.py              # Full CLI (add/remove passwords)
├── pdf_password_manager_gui.py         # Complete GUI (add/remove tabs)
├── pdf_password_remover_gui_enhanced.py # Legacy GUI (remove-only)
├── pdf_password_remover_gui.py         # Legacy simple GUI (remove-only)
├── test_pdf_password_remover.py        # Comprehensive test suite
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