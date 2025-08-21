import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from PyPDF2 import PdfReader, PdfWriter
import os
import threading
import logging
import shutil
from datetime import datetime
import json
from pathlib import Path

# Try to import PyCryptodome for AES support
try:
    from Crypto.Cipher import AES
    AES_AVAILABLE = True
except ImportError:
    AES_AVAILABLE = False

class Settings:
    """Handle application settings."""
    def __init__(self):
        self.settings_file = Path.home() / '.pdf_password_manager_settings.json'
        self.default_settings = {
            'create_backup': True,
            'output_directory': '',
            'remember_last_directory': True,
            'last_directory': str(Path.home()),
            'log_level': 'INFO',
            'overwrite_without_ask': False,
            'default_permissions': {
                'print': True,
                'modify': False,
                'copy': True,
                'annotate': True
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults for new settings
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.settings[key] = value

class PDFPasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Manager v2.0")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Settings
        self.settings = Settings()
        
        # Setup logging
        self.setup_logging()
        
        # Variables
        self.selected_files = []
        self.current_operation = tk.StringVar(value="remove")
        self.user_password = tk.StringVar()
        self.owner_password = tk.StringVar()
        self.status = tk.StringVar(value="Select PDF file(s) and choose operation")
        
        # Options
        self.create_backup = tk.BooleanVar(value=self.settings.get('create_backup'))
        self.overwrite_files = tk.BooleanVar(value=self.settings.get('overwrite_without_ask'))
        
        # Permissions (for add mode)
        default_perms = self.settings.get('default_permissions')
        self.allow_print = tk.BooleanVar(value=default_perms.get('print', True))
        self.allow_modify = tk.BooleanVar(value=default_perms.get('modify', False))
        self.allow_copy = tk.BooleanVar(value=default_perms.get('copy', True))
        self.allow_annotate = tk.BooleanVar(value=default_perms.get('annotate', True))
        
        self.processing = False
        
        self.create_widgets()
        
        # Status
        if not AES_AVAILABLE:
            self.log_message("Warning: PyCryptodome not available. Some AES-encrypted PDFs may not work.")
        
    def setup_logging(self):
        """Setup logging for the application."""
        log_level = getattr(logging, self.settings.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_password_manager_gui.log'),
                logging.StreamHandler()
            ]
        )
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main operation tabs
        self.remove_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.remove_frame, text="Remove Password")
        
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Add Password")
        
        # Settings and log tabs
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Log")
        
        self.create_remove_tab()
        self.create_add_tab()
        self.create_settings_tab()
        self.create_log_tab()
        
    def create_remove_tab(self):
        """Create the remove password tab."""
        # File selection section
        files_section = ttk.LabelFrame(self.remove_frame, text="PDF Files to Unlock", padding=10)
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(files_section, 
            text="Select password-protected PDF files to unlock:")
        instruction_label.pack(anchor=tk.W)
        
        # File list with scrollbar
        list_frame = ttk.Frame(files_section)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.remove_file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.remove_file_listbox.yview)
        self.remove_file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.remove_file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File buttons
        file_buttons = ttk.Frame(files_section)
        file_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_buttons, text="Add Files", 
                  command=lambda: self.add_files(self.remove_file_listbox, 'remove')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons, text="Remove Selected", 
                  command=lambda: self.remove_selected_files(self.remove_file_listbox, 'remove')).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons, text="Clear All", 
                  command=lambda: self.clear_all_files(self.remove_file_listbox, 'remove')).pack(side=tk.LEFT, padx=5)
        
        # Password section
        password_section = ttk.LabelFrame(self.remove_frame, text="Current Password", padding=10)
        password_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(password_section, text="Enter current PDF password:").pack(anchor=tk.W)
        self.remove_password_entry = ttk.Entry(password_section, textvariable=self.user_password, show="*", width=50)
        self.remove_password_entry.pack(fill=tk.X, pady=5)
        
        # Process button
        self.remove_process_btn = ttk.Button(self.remove_frame, text="Remove Passwords", 
                                           command=lambda: self.process_files('remove'))
        self.remove_process_btn.pack(pady=10)
        
    def create_add_tab(self):
        """Create the add password tab."""
        # File selection section
        files_section = ttk.LabelFrame(self.add_frame, text="PDF Files to Protect", padding=10)
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(files_section, 
            text="Select PDF files to add password protection:")
        instruction_label.pack(anchor=tk.W)
        
        # File list with scrollbar
        list_frame = ttk.Frame(files_section)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.add_file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=6)
        scrollbar2 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.add_file_listbox.yview)
        self.add_file_listbox.configure(yscrollcommand=scrollbar2.set)
        
        self.add_file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File buttons
        file_buttons = ttk.Frame(files_section)
        file_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_buttons, text="Add Files", 
                  command=lambda: self.add_files(self.add_file_listbox, 'add')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons, text="Remove Selected", 
                  command=lambda: self.remove_selected_files(self.add_file_listbox, 'add')).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons, text="Clear All", 
                  command=lambda: self.clear_all_files(self.add_file_listbox, 'add')).pack(side=tk.LEFT, padx=5)
        
        # Password section
        password_section = ttk.LabelFrame(self.add_frame, text="Password Settings", padding=10)
        password_section.pack(fill=tk.X, pady=(0, 10))
        
        # User password
        ttk.Label(password_section, text="User Password:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.add_user_password_entry = ttk.Entry(password_section, show="*", width=30)
        self.add_user_password_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Owner password
        ttk.Label(password_section, text="Owner Password:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.add_owner_password_entry = ttk.Entry(password_section, show="*", width=30)
        self.add_owner_password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(password_section, text="(Leave empty to use same as user password)", 
                 font=('TkDefaultFont', 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        password_section.columnconfigure(1, weight=1)
        
        # Permissions section
        permissions_section = ttk.LabelFrame(self.add_frame, text="Permissions", padding=10)
        permissions_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(permissions_section, text="Allow Printing", 
                       variable=self.allow_print).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(permissions_section, text="Allow Content Copying", 
                       variable=self.allow_copy).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(permissions_section, text="Allow Content Modification", 
                       variable=self.allow_modify).grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(permissions_section, text="Allow Annotations", 
                       variable=self.allow_annotate).grid(row=1, column=1, sticky=tk.W)
        
        # Process button
        self.add_process_btn = ttk.Button(self.add_frame, text="Add Password Protection", 
                                        command=lambda: self.process_files('add'))
        self.add_process_btn.pack(pady=10)
        
    def create_settings_tab(self):
        """Create the settings tab."""
        # Output directory
        ttk.Label(self.settings_frame, text="Default Output Directory:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        dir_frame = ttk.Frame(self.settings_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.output_dir_var = tk.StringVar(value=self.settings.get('output_directory'))
        output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_directory).pack(side=tk.RIGHT)
        
        # Other settings
        settings_options = ttk.LabelFrame(self.settings_frame, text="General Options", padding=10)
        settings_options.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(settings_options, text="Create backup files before processing", 
                       variable=self.create_backup).pack(anchor=tk.W)
        ttk.Checkbutton(settings_options, text="Overwrite existing files without asking", 
                       variable=self.overwrite_files).pack(anchor=tk.W)
        
        self.remember_dir_var = tk.BooleanVar(value=self.settings.get('remember_last_directory'))
        ttk.Checkbutton(settings_options, text="Remember last directory", 
                       variable=self.remember_dir_var).pack(anchor=tk.W)
        
        # Log level
        ttk.Label(settings_options, text="Log Level:").pack(anchor=tk.W, pady=(10, 5))
        self.log_level_var = tk.StringVar(value=self.settings.get('log_level'))
        log_level_combo = ttk.Combobox(settings_options, textvariable=self.log_level_var, 
                                      values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state="readonly")
        log_level_combo.pack(anchor=tk.W)
        
        # Save settings button
        ttk.Button(settings_options, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Progress and status section
        progress_section = ttk.LabelFrame(self.settings_frame, text="Processing Status", padding=10)
        progress_section.pack(fill=tk.X, padx=10, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_section, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(progress_section, textvariable=self.status, foreground="blue")
        self.status_label.pack(pady=5)
        
    def create_log_tab(self):
        """Create the log tab."""
        self.log_text = ScrolledText(self.log_frame, height=25, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear log button
        ttk.Button(self.log_frame, text="Clear Log", command=self.clear_log).pack(pady=5)
        
    def add_files(self, listbox, operation):
        """Add PDF files to the specified listbox."""
        initial_dir = self.settings.get('last_directory') if self.settings.get('remember_last_directory') else None
        filenames = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        
        # Get the appropriate file list based on operation
        if operation == 'remove':
            file_list = getattr(self, 'remove_files', [])
            if not hasattr(self, 'remove_files'):
                self.remove_files = []
                file_list = self.remove_files
        else:
            file_list = getattr(self, 'add_files_list', [])
            if not hasattr(self, 'add_files_list'):
                self.add_files_list = []
                file_list = self.add_files_list
        
        for filename in filenames:
            if filename not in file_list:
                file_list.append(filename)
                listbox.insert(tk.END, os.path.basename(filename))
        
        if filenames and self.settings.get('remember_last_directory'):
            self.settings.set('last_directory', os.path.dirname(filenames[0]))
        
        self.update_ui_state()
        
    def remove_selected_files(self, listbox, operation):
        """Remove selected files from the specified listbox."""
        selection = listbox.curselection()
        file_list = self.remove_files if operation == 'remove' else self.add_files_list
        
        for i in reversed(selection):
            del file_list[i]
            listbox.delete(i)
        self.update_ui_state()
        
    def clear_all_files(self, listbox, operation):
        """Clear all files from the specified listbox."""
        if operation == 'remove':
            self.remove_files = []
        else:
            self.add_files_list = []
        listbox.delete(0, tk.END)
        self.update_ui_state()
        
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def update_ui_state(self):
        """Update UI state based on current conditions."""
        # Initialize file lists if they don't exist
        if not hasattr(self, 'remove_files'):
            self.remove_files = []
        if not hasattr(self, 'add_files_list'):
            self.add_files_list = []
            
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        if "Remove" in tab_text:
            has_files = len(self.remove_files) > 0
            has_password = len(self.user_password.get().strip()) > 0
            if has_files and has_password and not self.processing:
                self.status.set(f"{len(self.remove_files)} file(s) ready for password removal")
            elif has_files and not has_password:
                self.status.set("Enter current password to continue")
            elif not has_files:
                self.status.set("Select PDF file(s) to unlock")
        else:
            has_files = len(self.add_files_list) > 0
            has_password = len(self.add_user_password_entry.get().strip()) > 0
            if has_files and has_password and not self.processing:
                self.status.set(f"{len(self.add_files_list)} file(s) ready for password protection")
            elif has_files and not has_password:
                self.status.set("Enter password to protect files")
            elif not has_files:
                self.status.set("Select PDF file(s) to protect")
                
    def process_files(self, operation):
        """Process files based on the operation."""
        if operation == 'remove':
            files = getattr(self, 'remove_files', [])
            password = self.user_password.get()
        else:
            files = getattr(self, 'add_files_list', [])
            password = self.add_user_password_entry.get()
            
        if not files:
            messagebox.showerror("Error", "Please select at least one PDF file.")
            return
            
        if not password:
            messagebox.showerror("Error", "Please enter a password.")
            return
            
        # Start processing
        self.processing = True
        self.progress.config(maximum=len(files), value=0)
        
        thread = threading.Thread(target=self.process_files_thread, args=(operation, files, password), daemon=True)
        thread.start()
        
    def process_files_thread(self, operation, files, password):
        """Process files in background thread."""
        successful = 0
        failed = 0
        
        output_dir = self.output_dir_var.get().strip() or None
        
        for i, input_file in enumerate(files):
            self.root.after(0, lambda i=i: self.progress.config(value=i))
            self.root.after(0, lambda f=input_file: self.status.set(f"Processing: {os.path.basename(f)}"))
            
            try:
                # Determine output file
                if output_dir:
                    prefix = "unlocked_" if operation == 'remove' else "protected_"
                    output_file = os.path.join(output_dir, f"{prefix}{os.path.basename(input_file)}")
                else:
                    prefix = "unlocked_" if operation == 'remove' else "protected_"
                    output_file = f"{prefix}{input_file}"
                
                if operation == 'remove':
                    success = self.process_single_file_remove(input_file, output_file, password)
                else:
                    owner_password = self.add_owner_password_entry.get() or password
                    permissions = {
                        'print': self.allow_print.get(),
                        'modify': self.allow_modify.get(),
                        'copy': self.allow_copy.get(),
                        'annotate': self.allow_annotate.get()
                    }
                    success = self.process_single_file_add(input_file, output_file, password, owner_password, permissions)
                
                if success:
                    successful += 1
                    self.log_message(f"Successfully processed: {input_file}")
                else:
                    failed += 1
                    self.log_message(f"Failed to process: {input_file}")
                    
            except Exception as e:
                failed += 1
                self.log_message(f"Error processing {input_file}: {str(e)}")
        
        # Update UI in main thread
        self.root.after(0, lambda: self.processing_complete(operation, successful, failed))
        
    def process_single_file_remove(self, input_file, output_file, password):
        """Remove password from a single PDF file."""
        try:
            if self.create_backup.get():
                self.create_file_backup(input_file)
                
            reader = PdfReader(input_file)
            
            if not reader.is_encrypted:
                self.log_message(f"Warning: {input_file} is not password protected")
                return True
                
            if not reader.decrypt(password):
                self.log_message(f"Incorrect password for: {input_file}")
                return False
                
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
                
            with open(output_file, "wb") as f:
                writer.write(f)
                
            return True
            
        except Exception as e:
            self.log_message(f"Error removing password from {input_file}: {str(e)}")
            return False
            
    def process_single_file_add(self, input_file, output_file, user_password, owner_password, permissions):
        """Add password to a single PDF file."""
        try:
            if self.create_backup.get():
                self.create_file_backup(input_file)
                
            reader = PdfReader(input_file)
            
            if reader.is_encrypted:
                self.log_message(f"Warning: {input_file} is already password protected")
                
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            # Convert permissions to PyPDF2 format
            permissions_flag = 0
            if permissions.get('print', False):
                permissions_flag |= 4
            if permissions.get('modify', False):
                permissions_flag |= 8
            if permissions.get('copy', False):
                permissions_flag |= 16
            if permissions.get('annotate', False):
                permissions_flag |= 32
                
            writer.encrypt(
                user_password=user_password,
                owner_password=owner_password,
                use_128bit=True,
                permissions_flag=permissions_flag
            )
                
            with open(output_file, "wb") as f:
                writer.write(f)
                
            return True
            
        except Exception as e:
            self.log_message(f"Error adding password to {input_file}: {str(e)}")
            return False
            
    def create_file_backup(self, file_path):
        """Create a backup of the file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            backup_name = f"{base_name}_backup_{timestamp}.pdf"
            backup_path = os.path.join(os.path.dirname(file_path), backup_name)
            shutil.copy2(file_path, backup_path)
            self.log_message(f"Backup created: {backup_path}")
        except Exception as e:
            self.log_message(f"Could not create backup: {e}")
            
    def processing_complete(self, operation, successful, failed):
        """Called when processing is complete."""
        self.processing = False
        self.progress.config(value=self.progress['maximum'])
        
        total = successful + failed
        op_text = "removed" if operation == 'remove' else "added"
        self.status.set(f"Complete: {successful}/{total} passwords {op_text}")
        
        if failed == 0:
            messagebox.showinfo("Success", f"Successfully {op_text} passwords for all {successful} files!")
        else:
            messagebox.showwarning("Partial Success", 
                                 f"Processed {successful}/{total} files successfully.\n"
                                 f"{failed} files failed. Check the log for details.")
        
        # Clear passwords for security
        self.user_password.set("")
        self.add_user_password_entry.delete(0, tk.END)
        self.add_owner_password_entry.delete(0, tk.END)
        
    def log_message(self, message):
        """Add message to log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Update log tab
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_entry))
        self.root.after(0, lambda: self.log_text.see(tk.END))
        
        # Also log to file
        logging.info(message)
        
    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
        
    def save_settings(self):
        """Save current settings."""
        self.settings.set('output_directory', self.output_dir_var.get())
        self.settings.set('remember_last_directory', self.remember_dir_var.get())
        self.settings.set('log_level', self.log_level_var.get())
        self.settings.set('create_backup', self.create_backup.get())
        self.settings.set('overwrite_without_ask', self.overwrite_files.get())
        
        # Save default permissions
        self.settings.set('default_permissions', {
            'print': self.allow_print.get(),
            'modify': self.allow_modify.get(),
            'copy': self.allow_copy.get(),
            'annotate': self.allow_annotate.get()
        })
        
        self.settings.save_settings()
        messagebox.showinfo("Settings", "Settings saved successfully!")
        
        # Update logging level
        new_level = getattr(logging, self.log_level_var.get())
        logging.getLogger().setLevel(new_level)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFPasswordManagerGUI(root)
    
    # Set up change callbacks
    app.user_password.trace('w', lambda *args: app.update_ui_state())
    
    root.mainloop()