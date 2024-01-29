import tkinter as tk
from tkinter import messagebox
from email_client.email_client import EmailClient


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Mailytics - Login")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the login fields
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Email field
        email_label = tk.Label(frame, text="Email:")
        email_label.pack()
        self.email_entry = tk.Entry(frame)
        self.email_entry.pack()

        # Password field
        password_label = tk.Label(frame, text="Password:")
        password_label.pack()
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.pack()

        # Login button
        login_button = tk.Button(frame, text="Login", command=self.on_login_click)
        login_button.pack()

    def on_login_click(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        # Initialize and connect to the email client
        self.email_client = EmailClient('imap.gmail.com', email, password)
        try:
            self.email_client.connect()
            messagebox.showinfo("Login", "Login successful!")
            # Proceed to fetch and display emails
        except Exception as e:
            messagebox.showerror("Login", f"Failed to login: {str(e)}")



def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
