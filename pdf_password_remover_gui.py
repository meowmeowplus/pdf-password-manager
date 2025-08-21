import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter
import os
import threading

class PDFPasswordRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Remover")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_file = tk.StringVar()
        self.password = tk.StringVar()
        self.status = tk.StringVar(value="Select a PDF file to begin")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        ttk.Label(main_frame, text="Select PDF File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Password input
        ttk.Label(main_frame, text="Enter PDF Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password, show="*", width=40)
        self.password_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.password_entry.bind('<Return>', lambda e: self.remove_password())
        
        # Remove password button
        self.remove_btn = ttk.Button(main_frame, text="Remove Password", command=self.remove_password, state="disabled")
        self.remove_btn.grid(row=4, column=0, pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status, foreground="blue")
        self.status_label.grid(row=6, column=0, sticky=tk.W)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
            self.remove_btn.config(state="normal")
            self.status.set("File selected. Enter password and click 'Remove Password'")
            
    def remove_password(self):
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
            
        if not self.password.get():
            messagebox.showerror("Error", "Please enter the PDF password.")
            return
            
        # Disable UI during processing
        self.remove_btn.config(state="disabled")
        self.password_entry.config(state="disabled")
        self.progress.start()
        self.status.set("Processing...")
        
        # Run in separate thread to prevent UI freezing
        threading.Thread(target=self.process_pdf, daemon=True).start()
        
    def process_pdf(self):
        try:
            input_file = self.selected_file.get()
            password = self.password.get()
            
            # Create temporary output file
            temp_output = input_file + ".temp"
            
            # Read the encrypted PDF
            reader = PdfReader(input_file)
            
            if reader.is_encrypted:
                if not reader.decrypt(password):
                    self.update_ui_after_error("Incorrect password. Please try again.")
                    return
            else:
                self.update_ui_after_error("This PDF is not password protected.")
                return
            
            # Create a new PDF writer
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            # Save to temporary file
            with open(temp_output, "wb") as f:
                writer.write(f)
            
            # Replace original file with unlocked version
            os.replace(temp_output, input_file)
            
            self.update_ui_after_success()
            
        except Exception as e:
            # Clean up temp file if it exists
            temp_output = self.selected_file.get() + ".temp"
            if os.path.exists(temp_output):
                os.remove(temp_output)
            self.update_ui_after_error(f"An error occurred: {str(e)}")
    
    def update_ui_after_success(self):
        # Update UI in main thread
        self.root.after(0, self._success_callback)
        
    def update_ui_after_error(self, error_msg):
        # Update UI in main thread
        self.root.after(0, lambda: self._error_callback(error_msg))
    
    def _success_callback(self):
        self.progress.stop()
        self.remove_btn.config(state="normal")
        self.password_entry.config(state="normal")
        self.password.set("")  # Clear password
        self.status.set("Success! Password removed from PDF file.")
        messagebox.showinfo("Success", "Password successfully removed!\nThe original file has been updated.")
        
    def _error_callback(self, error_msg):
        self.progress.stop()
        self.remove_btn.config(state="normal")
        self.password_entry.config(state="normal")
        self.status.set("Error occurred. Please try again.")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFPasswordRemoverGUI(root)
    root.mainloop()