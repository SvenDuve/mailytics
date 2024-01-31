
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui.login_window import LoginWindow
from email_client.email_client import EmailClient

import openai
from langchain_openai import OpenAI
from language_model.processor import process_text, TextRequest

from dotenv import load_dotenv
import os
import re

load_dotenv()


class MainApplication:
    """
    The main application class for Mailytics.

    Attributes:
        root (tk.Tk): The root Tkinter window.
        email_client (EmailClient): The email client instance.
        selected_emails (list): A list of selected email bodies.
        email_content_text (tk.Text): The text widget for displaying email content.
        llm (OpenAI): The OpenAI language model instance.
    """

    def __init__(self, root):
        """
        Initializes the MainApplication.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Mailytics")
        self.email_client = EmailClient('imap.gmail.com', 'user@example.com', os.getenv("MAILPASSWORD"))
        self.selected_emails = []
        self.email_content_text = None
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize OpenAI LLM
        self.initialize_ui()

    def initialize_ui(self):
        """
        Initializes the user interface.
        """
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

        v_paned_window = tk.PanedWindow(paned_window, orient=tk.VERTICAL)

        # Add another text window for email content
        self.email_content_text = tk.Text(v_paned_window)
        v_paned_window.add(self.email_content_text)
        self.summarize_button = tk.Button(self.root, text="Summarize", command=self.on_summarize_click)
        self.summarize_button.pack()
        # Right Pane: Text Window for Analytics
        self.analytics_text = tk.Text(v_paned_window)
        v_paned_window.add(self.analytics_text)

        paned_window.add(v_paned_window)

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
        """
        Populates the folder list with email folders.
        """
        try:
            self.email_client.connect()
            folders = self.email_client.get_folders()  # Implement this method in EmailClient
            for folder in folders:
                print("Adding folder:", folder)
                self.folder_list.insert('', 'end', text=folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch folders: {str(e)}")
    
    def populate_emails(self, folder_name):
        """
        Populates the email list with emails from the selected folder.

        Args:
            folder_name (str): The name of the selected folder.
        """
        self.email_client.select_folder(folder_name)
        emails = self.email_client.fetch_emails()  # Implement this in EmailClient
        for email in emails:
            self.email_list.insert('', 'end', text=email['id'], values=(email['from'], email['subject'], email['date']))

    def on_folder_select(self, event):
        """
        Event handler for folder selection.

        Args:
            event: The event object.
        """
        selected_folder = self.folder_list.item(self.folder_list.selection()[0])['text']
        self.populate_emails(selected_folder)

    def on_email_select(self, event):
        """
        Event handler for email selection.

        Args:
            event: The event object.
        """
        selected_items = self.email_list.selection()
        self.selected_emails.clear()  # Clear previously selected emails
        
        for item in selected_items:
            email_id = self.email_list.item(item)['text']
            email_body = self.email_client.fetch_email_body(email_id)  # Implement this in EmailClient
            self.selected_emails.append(email_body)


        if self.selected_emails:
            self.email_content_text.delete('1.0', tk.END)
            self.email_content_text.insert(tk.END, self.selected_emails[-1])
            # original_content = self.selected_emails[-1]
            # summary = self.summarize_email(original_content)
            # self.analytics_text.delete('1.0', tk.END)
            # self.analytics_text.insert(tk.END, summary)

    def summarize_email(self, content):
        """
        Summarizes the given email content using LangChain and OpenAI.

        Args:
            content (str): The email content to be summarized.

        Returns:
            str: The summarized email content.
        """
        # Remove email addresses
        content = re.sub(r'\S+@\S+', '', content)
        # Remove hyperlinks
        content = re.sub(r'http\S+', '', content)
        print(content)
        response = process_text(TextRequest(text=content))
        # Use LangChain and OpenAI for summarization
        # response = self.llm.generate([content])
        print(response)
        # return response.generations[0][0].text
        return response["processed_text"]
    
    def on_summarize_click(self):
        if self.selected_emails:
            original_content = self.selected_emails[-1]
            summary = self.summarize_email(original_content)
            self.analytics_text.delete('1.0', tk.END)
            self.analytics_text.insert(tk.END, summary)



def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
