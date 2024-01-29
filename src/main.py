
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui.login_window import LoginWindow
from email_client.email_client import EmailClient


from dotenv import load_dotenv
import os

load_dotenv()


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Mailytics")
        self.email_client = EmailClient('imap.gmail.com', 'user@example.com', os.getenv("MAILPASSWORD"))
        self.selected_emails = []
        self.initialize_ui()

    def initialize_ui(self):
        # Create a PanedWindow
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left Pane: Folder Browser
        self.folder_list = ttk.Treeview(paned_window)
        self.folder_list.heading('#0', text='Mail Folders')
        paned_window.add(self.folder_list)

        # Middle Pane: Mail List
        self.email_list = ttk.Treeview(paned_window, columns=("From", "Subject", "Date"))
        self.email_list.heading('#0', text='ID')
        self.email_list.heading('From', text='From')
        self.email_list.heading('Subject', text='Subject')
        self.email_list.heading('Date', text='Date')
        paned_window.add(self.email_list)

        # Bind folder selection event
        self.folder_list.bind('<<TreeviewSelect>>', self.on_folder_select)


        # Right Pane: Text Window for Analytics
        self.analytics_text = tk.Text(paned_window)
        paned_window.add(self.analytics_text)

        # For demonstration, let's add a sample mail folder
        self.folder_list.insert('', 'end', text='Inbox')
        # And some placeholder text in analytics window
        self.analytics_text.insert('end', 'Analytics Output Will Appear Here')

        # Open the login window
        login_window = LoginWindow(self.root)
        self.email_client = EmailClient('imap.one.com', 'buchhaltung@duve-lc.ch', os.getenv("MAILPASSWORD"))
        self.populate_folders()

        self.email_list.bind('<<TreeviewSelect>>', self.on_email_select)


    def populate_folders(self):
        try:
            self.email_client.connect()
            folders = self.email_client.get_folders()  # Implement this method in EmailClient
            for folder in folders:
                print("Adding folder:", folder)
                self.folder_list.insert('', 'end', text=folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch folders: {str(e)}")
    
    # needs review obivously
    def populate_emails(self, folder_name):
        self.email_client.select_folder(folder_name)
        emails = self.email_client.fetch_emails()  # Implement this in EmailClient
        for email in emails:
            self.email_list.insert('', 'end', text=email['id'], values=(email['from'], email['subject'], email['date']))

    def on_folder_select(self, event):
        selected_folder = self.folder_list.item(self.folder_list.selection()[0])['text']
        self.populate_emails(selected_folder)

    def on_email_select(self, event):
        selected_items = self.email_list.selection()
        self.selected_emails.clear()  # Clear previously selected emails
        
        for item in selected_items:
            email_id = self.email_list.item(item)['text']
            email_body = self.email_client.fetch_email_body(email_id)  # Implement this in EmailClient
            self.selected_emails.append(email_body)
        print(self.selected_emails)


def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
