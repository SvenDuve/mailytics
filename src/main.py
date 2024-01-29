
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui.login_window import LoginWindow
from email_client.email_client import EmailClient

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Mailytics")
        self.initialize_ui()

    def initialize_ui(self):
        # Create a PanedWindow
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left Pane: Folder Browser
        self.folder_list = ttk.Treeview(paned_window)
        self.folder_list.heading('#0', text='Mail Folders')
        paned_window.add(self.folder_list)

        # Right Pane: Text Window for Analytics
        self.analytics_text = tk.Text(paned_window)
        paned_window.add(self.analytics_text)

        # For demonstration, let's add a sample mail folder
        self.folder_list.insert('', 'end', text='Inbox')
        # And some placeholder text in analytics window
        self.analytics_text.insert('end', 'Analytics Output Will Appear Here')


        # Open the login window
        login_window = LoginWindow(self.root)

        self.email_client = EmailClient('imap.one.com', 'buchhaltung@duve-lc.ch', 'Pilsener/123')
        self.populate_folders()

    def populate_folders(self):
        try:
            self.email_client.connect()
            folders = self.email_client.get_folders()  # Implement this method in EmailClient
            for folder in folders:
                print("Adding folder:", folder)
                self.folder_list.insert('', 'end', text=folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch folders: {str(e)}")


def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
