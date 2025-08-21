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

class DropTarget:
    """Handles drag and drop functionality."""
    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback
        self.widget.drop_target_register('DND_Files')
        self.widget.dnd_bind('<<DropEnter>>', self.drop_enter)
        self.widget.dnd_bind('<<DropPosition>>', self.drop_position)
        self.widget.dnd_bind('<<DropLeave>>', self.drop_leave)
        self.widget.dnd_bind('<<Drop>>', self.drop)
    
    def drop_enter(self, event):
        event.widget.focus_force()
        return 'copy'
    
    def drop_position(self, event):
        return 'copy'
    
    def drop_leave(self, event):
        pass
    
    def drop(self, event):
        files = event.data.split()
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.callback(pdf_files)
        return 'copy'

class Settings:
    """Handle application settings."""
    def __init__(self):
        self.settings_file = Path.home() / '.pdf_password_remover_settings.json'
        self.default_settings = {
            'create_backup': True,
            'output_directory': '',
            'remember_last_directory': True,
            'last_directory': str(Path.home()),
            'log_level': 'INFO',
            'overwrite_without_ask': False
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

class PDFPasswordRemoverGUIEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Remover v2.0")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Settings
        self.settings = Settings()
        
        # Setup logging
        self.setup_logging()
        
        # Variables
        self.selected_files = []
        self.password = tk.StringVar()
        self.status = tk.StringVar(value="Select PDF file(s) to begin")
        self.create_backup = tk.BooleanVar(value=self.settings.get('create_backup'))
        self.overwrite_files = tk.BooleanVar(value=self.settings.get('overwrite_without_ask'))
        self.processing = False
        
        self.create_widgets()
        self.setup_drag_drop()
        
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
                logging.FileHandler('pdf_password_remover_gui.log'),
                logging.StreamHandler()
            ]
        )
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main processing tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Process PDFs")
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Log tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Log")
        
        self.create_main_tab()
        self.create_settings_tab()
        self.create_log_tab()
        
    def create_main_tab(self):
        """Create the main processing tab."""
        # File selection section
        files_section = ttk.LabelFrame(self.main_frame, text="PDF Files", padding=10)
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        instruction_label = ttk.Label(files_section, 
            text="Select PDF files or drag and drop them here:")
        instruction_label.pack(anchor=tk.W)
        
        # File list with scrollbar
        list_frame = ttk.Frame(files_section)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File buttons
        file_buttons = ttk.Frame(files_section)
        file_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_buttons, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons, text="Remove Selected", command=self.remove_selected_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons, text="Clear All", command=self.clear_all_files).pack(side=tk.LEFT, padx=5)
        
        # Password section
        password_section = ttk.LabelFrame(self.main_frame, text="Password", padding=10)
        password_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(password_section, text="Enter PDF Password:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(password_section, textvariable=self.password, show="*", width=50)
        self.password_entry.pack(fill=tk.X, pady=5)
        self.password_entry.bind('<Return>', lambda e: self.process_files())
        
        # Options section
        options_section = ttk.LabelFrame(self.main_frame, text="Options", padding=10)
        options_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(options_section, text="Create backup files", 
                       variable=self.create_backup).pack(anchor=tk.W)
        ttk.Checkbutton(options_section, text="Overwrite existing files without asking", 
                       variable=self.overwrite_files).pack(anchor=tk.W)
        
        # Processing section
        process_section = ttk.LabelFrame(self.main_frame, text="Processing", padding=10)
        process_section.pack(fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(process_section, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Process button
        self.process_btn = ttk.Button(process_section, text="Remove Passwords", 
                                    command=self.process_files, state="disabled")
        self.process_btn.pack(pady=5)
        
        # Status label
        self.status_label = ttk.Label(process_section, textvariable=self.status, foreground="blue")
        self.status_label.pack(pady=5)
        
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
        settings_options = ttk.LabelFrame(self.settings_frame, text="Preferences", padding=10)
        settings_options.pack(fill=tk.X, padx=10, pady=10)
        
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
        
    def create_log_tab(self):
        """Create the log tab."""
        self.log_text = ScrolledText(self.log_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear log button
        ttk.Button(self.log_frame, text="Clear Log", command=self.clear_log).pack(pady=5)
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        try:
            # This is a simplified drag-drop implementation
            # For full functionality, you'd need tkinterdnd2 package
            self.file_listbox.bind('<Button-1>', self.on_listbox_click)
        except Exception as e:
            self.log_message(f"Drag-drop setup failed: {e}")
    
    def on_listbox_click(self, event):
        """Handle listbox clicks (placeholder for drag-drop)."""
        pass
        
    def add_files(self):
        """Add PDF files to the list."""
        initial_dir = self.settings.get('last_directory') if self.settings.get('remember_last_directory') else None
        filenames = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        
        for filename in filenames:
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.file_listbox.insert(tk.END, os.path.basename(filename))
        
        if filenames and self.settings.get('remember_last_directory'):
            self.settings.set('last_directory', os.path.dirname(filenames[0]))
        
        self.update_ui_state()
        
    def remove_selected_files(self):
        """Remove selected files from the list."""
        selection = self.file_listbox.curselection()
        for i in reversed(selection):  # Remove in reverse order to maintain indices
            del self.selected_files[i]
            self.file_listbox.delete(i)
        self.update_ui_state()
        
    def clear_all_files(self):
        """Clear all files from the list."""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_ui_state()
        
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def update_ui_state(self):
        """Update UI state based on current conditions."""
        has_files = len(self.selected_files) > 0
        has_password = len(self.password.get().strip()) > 0
        
        if has_files and has_password and not self.processing:
            self.process_btn.config(state="normal")
            self.status.set(f"{len(self.selected_files)} file(s) ready for processing")
        elif has_files and not has_password:
            self.process_btn.config(state="disabled")
            self.status.set("Enter password to continue")
        elif not has_files:
            self.process_btn.config(state="disabled")
            self.status.set("Select PDF file(s) to begin")
        else:
            self.process_btn.config(state="disabled")
            
    def process_files(self):
        """Process all selected files."""
        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one PDF file.")
            return
            
        if not self.password.get():
            messagebox.showerror("Error", "Please enter the PDF password.")
            return
            
        # Start processing in separate thread
        self.processing = True
        self.process_btn.config(state="disabled")
        self.password_entry.config(state="disabled")
        
        self.progress.config(maximum=len(self.selected_files), value=0)
        
        thread = threading.Thread(target=self.process_files_thread, daemon=True)
        thread.start()
        
    def process_files_thread(self):
        """Process files in background thread."""
        successful = 0
        failed = 0
        
        output_dir = self.output_dir_var.get().strip() or None
        
        for i, input_file in enumerate(self.selected_files):
            self.root.after(0, lambda i=i: self.progress.config(value=i))
            self.root.after(0, lambda f=input_file: self.status.set(f"Processing: {os.path.basename(f)}"))
            
            try:
                # Determine output file
                if output_dir:
                    output_file = os.path.join(output_dir, f"unlocked_{os.path.basename(input_file)}")
                else:
                    output_file = f"unlocked_{input_file}"
                
                if self.process_single_file(input_file, output_file):
                    successful += 1
                    self.log_message(f"Successfully processed: {input_file}")
                else:
                    failed += 1
                    self.log_message(f"Failed to process: {input_file}")
                    
            except Exception as e:
                failed += 1
                self.log_message(f"Error processing {input_file}: {str(e)}")
        
        # Update UI in main thread
        self.root.after(0, lambda: self.processing_complete(successful, failed))
        
    def process_single_file(self, input_file, output_file):
        """Process a single PDF file."""
        try:
            # Validate file
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")
            
            # Create backup if requested
            if self.create_backup.get():
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    backup_name = f"{base_name}_backup_{timestamp}.pdf"
                    backup_path = os.path.join(os.path.dirname(input_file), backup_name)
                    shutil.copy2(input_file, backup_path)
                    self.log_message(f"Backup created: {backup_path}")
                except Exception as e:
                    self.log_message(f"Could not create backup: {e}")
                    
            # Read and process PDF
            reader = PdfReader(input_file)
            
            if not reader.is_encrypted:
                self.log_message(f"Warning: {input_file} is not password protected")
                return True
                
            if not reader.decrypt(self.password.get()):
                self.log_message(f"Incorrect password for: {input_file}")
                return False
                
            # Check if output file exists
            if os.path.exists(output_file) and not self.overwrite_files.get():
                # In GUI mode, we'll overwrite by default but log it
                self.log_message(f"Overwriting existing file: {output_file}")
                
            # Create writer and copy pages
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
                
            # Save unlocked PDF
            with open(output_file, "wb") as f:
                writer.write(f)
                
            return True
            
        except Exception as e:
            self.log_message(f"Error processing {input_file}: {str(e)}")
            return False
            
    def processing_complete(self, successful, failed):
        """Called when processing is complete."""
        self.processing = False
        self.process_btn.config(state="normal")
        self.password_entry.config(state="normal")
        self.progress.config(value=self.progress['maximum'])
        
        total = successful + failed
        self.status.set(f"Complete: {successful}/{total} successful")
        
        if failed == 0:
            messagebox.showinfo("Success", f"Successfully processed all {successful} files!")
        else:
            messagebox.showwarning("Partial Success", 
                                 f"Processed {successful}/{total} files successfully.\n"
                                 f"{failed} files failed. Check the log for details.")
        
        # Clear password for security
        self.password.set("")
        
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
        
        self.settings.save_settings()
        messagebox.showinfo("Settings", "Settings saved successfully!")
        
        # Update logging level
        new_level = getattr(logging, self.log_level_var.get())
        logging.getLogger().setLevel(new_level)
        
    def on_password_change(self, *args):
        """Called when password changes."""
        self.update_ui_state()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set up password change callback
    app = PDFPasswordRemoverGUIEnhanced(root)
    app.password.trace('w', app.on_password_change)
    
    root.mainloop()