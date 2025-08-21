# PDF Password Remover

A simple tool to remove passwords from PDF files, available in both GUI and command-line versions.

## Features

- **GUI Version**: User-friendly interface with file browser and password input
- **CLI Version**: Command-line tool for batch processing or automation
- **AES Support**: Works with AES-encrypted PDF files
- **Safe Processing**: Overwrites original file with unlocked version
- **Portable**: Single executable file (Windows)

## Requirements

- Python 3.7+ (for source code)
- PyPDF2
- PyCryptodome (for AES encryption support)
- tkinter (for GUI version)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/pdf-password-remover.git
cd pdf-password-remover
```

2. Install dependencies:
```bash
pip install PyPDF2 PyCryptodome
```

## Usage

### GUI Version
Run the GUI application:
```bash
python pdf_password_remover_gui.py
```
1. Click "Browse" to select your PDF file
2. Enter the password
3. Click "Remove Password"
4. The original file will be unlocked

### Command Line Version
```bash
python remove_pdf_password.py input.pdf
```
The tool will prompt for the password and overwrite the original file.

## Building Executable

To create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="PDF_Password_Remover" pdf_password_remover_gui.py
```

## Security Notes

- Passwords are handled securely (masked input, not logged)
- Original files are overwritten - make backups if needed
- Use on trusted systems only

## License

MIT License - feel free to use and modify.