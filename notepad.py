import tkinter as tk  
from tkinter import filedialog, messagebox, simpledialog  
import requests
import sys
import os

import json  

class Notepad:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("*Untitled - Notepad")
        if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
    # Running in a normal Python environment
            base_path = os.path.dirname(__file__)

# Full path to the icon
        icon_path = os.path.join(base_path, 'notepadico.ico')

# Use the icon path
        root.wm_iconbitmap(icon_path)
        self.root.geometry("800x600")  

        # Create Text Widget  
        self.text_area = tk.Text(self.root, wrap='word', undo=True)  
        self.text_area.pack(fill='both', expand=True)  

        # Status Bar  
        self.status_bar = tk.Label(self.root, text="Ln 1, Col 0  |  100%  |  Windows (CRLF)  |  UTF-8", bd=1, relief=tk.SUNKEN, anchor="e")  
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)  

        # Bind Enter key for API integration  
        self.text_area.bind('<Return>', self.process_selected_text)  
        self.text_area.bind('<KeyRelease>', self.update_status)  

        # Initialize file  
        self.file = None  
        
        # Create Menu  
        self.create_menu()  

    def create_menu(self):  
        menu_bar = tk.Menu(self.root)  

        # File menu  
        file_menu = tk.Menu(menu_bar, tearoff=0)  
        file_menu.add_command(label="New", command=self.new_file, accelerator='Ctrl+N')  
        file_menu.add_command(label="Open", command=self.open_file, accelerator='Ctrl+O')  
        file_menu.add_command(label="Save", command=self.save_file, accelerator='Ctrl+S')  
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator='Ctrl+Shift+S')  
        file_menu.add_separator()  
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator='Ctrl+Q')  
        menu_bar.add_cascade(label="File", menu=file_menu)  

        # Edit menu  
        edit_menu = tk.Menu(menu_bar, tearoff=0)  
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator='Ctrl+Z')  
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)  
        edit_menu.add_separator()  
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator='Ctrl+X')  
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator='Ctrl+C')  
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator='Ctrl+V')  
        edit_menu.add_command(label="Delete", command=self.delete_selected_text)  
        edit_menu.add_command(label="Select All", command=self.select_all_text, accelerator='Ctrl+A')  
        menu_bar.add_cascade(label="Edit", menu=edit_menu)  

        # Format menu  
        format_menu = tk.Menu(menu_bar, tearoff=0)  
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)  
        format_menu.add_command(label="Font...", command=self.change_font)  
        menu_bar.add_cascade(label="Format", menu=format_menu)  

        # View menu  
        view_menu = tk.Menu(menu_bar, tearoff=0)  
        self.status_var = tk.BooleanVar(value=True)  # Check if status bar is visible  
        view_menu.add_checkbutton(label="Status Bar", onvalue=True, offvalue=False, variable=self.status_var, command=self.toggle_status_bar)  
        menu_bar.add_cascade(label="View", menu=view_menu)  

        # Help menu  
        help_menu = tk.Menu(menu_bar, tearoff=0)  
        help_menu.add_command(label="View Help", command=self.show_help)  
        help_menu.add_command(label="Send Feedback", command=self.send_feedback)  
        help_menu.add_command(label="About", command=self.show_about)  
        menu_bar.add_cascade(label="Help", menu=help_menu)  

        self.root.config(menu=menu_bar)  

    def new_file(self):  
        self.file = None  
        self.text_area.delete(1.0, tk.END)  
        self.root.title("*Untitled - Notepad Clone")  
    
    def open_file(self):  
        self.file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])  
        if self.file:  
            with open(self.file, 'r') as file:  
                self.text_area.delete(1.0, tk.END)  
                self.text_area.insert(1.0, file.read())  
            self.root.title(f"*{self.file} - Notepad Clone")  
    
    def save_file(self):  
        if self.file:  
            with open(self.file, 'w') as file:  
                file.write(self.text_area.get(1.0, tk.END))  
        else:  
            self.save_as_file()  
    
    def save_as_file(self):  
        self.file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])  
        if self.file:  
            with open(self.file, 'w') as file:  
                file.write(self.text_area.get(1.0, tk.END))  
            self.root.title(f"*{self.file} - Notepad Clone")  
    
    def exit_app(self):  
        if messagebox.askokcancel("Exit", "Do you want to exit?"):  
            self.root.destroy()  

    def show_about(self):  
        messagebox.showinfo("About", "Notepad Clone\nCreated with Python and Tkinter")  

    def process_selected_text(self, event):  
        try:  
            selected_text = self.text_area.selection_get()  
            response = self.get_api_response(selected_text)  

            # Insert the response after the cursor  
            cursor_position = self.text_area.index(tk.INSERT)  
            self.text_area.insert(cursor_position, response)  
        except tk.TclError:  
            messagebox.showinfo("Info", "No text selected.")  
        return "break"  # Prevent the default Enter key behavior  

    def get_api_response(self, selected_text):  
        url = "http://127.0.0.1:11434/api/chat"  
        headers = {  
            "Content-Type": "application/json"  
        }  
        payload = {  
            "model": "llama3.2",  
            "messages": [  
                {"role": "system", "content": "You are a salty pirate."},  
                {"role": "user", "content": selected_text}  
            ],  
            "stream": False  
        }  
        try:  
            response = requests.post(url, headers=headers, json=payload)  
            response.raise_for_status()  
            data = response.json()  
            return data.get("message", {}).get("content", "No content found.")  
        except requests.RequestException as e:  
            messagebox.showerror("Error", f"API request failed: {e}")  
            return "Error fetching response."  

    def update_status(self, event=None):  
        line, column = self.text_area.index(tk.END).split('.')  
        current_text = self.text_area.get(1.0, tk.END)  
        line_count = int(line) - 1  
        total_chars = len(current_text) - 1  # Remove the trailing newline  
        status_text = f"Ln {line_count}, Col {int(column) + 1}  |  {total_chars / 10}%  |  Windows (CRLF)  |  UTF-8"  
        self.status_bar.config(text=status_text)  

    def delete_selected_text(self):  
        try:  
            self.text_area.delete("sel.first", "sel.last")  
        except tk.TclError:  
            messagebox.showinfo("Info", "No text selected to delete.")  

    def select_all_text(self):  
        self.text_area.tag_add("sel", 1.0, "end")  

    def toggle_word_wrap(self):  
        current_wrap = self.text_area.cget("wrap")  
        self.text_area.config(wrap='word' if current_wrap == 'none' else 'none')  

    def change_font(self):  
        font_name = simpledialog.askstring("Font", "Enter font name (e.g., Arial):")  
        if font_name:  
            self.text_area.config(font=(font_name, 12))  

    def toggle_status_bar(self):  
        if self.status_var.get():  
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)  
        else:  
            self.status_bar.pack_forget()  

    def show_help(self):  
        messagebox.showinfo("Help", "This is a Notepad Clone. You can edit text, save files, and more.")  

    def send_feedback(self):  
        feedback = simpledialog.askstring("Feedback", "Enter your feedback:")  
        if feedback:  
            messagebox.showinfo("Feedback Received", "Thank you for your feedback!")  

if __name__ == "__main__":  
    root = tk.Tk()  
    app = Notepad(root)  
    root.mainloop()
