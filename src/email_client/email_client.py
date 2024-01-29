import imaplib
import email

class EmailClient:
    def __init__(self, server, email, password):
        self.server = server
        self.email = email
        self.password = password
        self.connection = None

    def connect(self):
        self.connection = imaplib.IMAP4_SSL(self.server)
        self.connection.login(self.email, self.password)

    def fetch_emails(self, mailbox='INBOX'):
        self.connection.select(mailbox)
        typ, data = self.connection.search(None, 'ALL')
        for num in data[0].split():
            typ, msg_data = self.connection.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    print(msg['subject'], msg['from'])
                    # Process each email as needed

    def get_folders(self):
        folders = []
        typ, data = self.connection.list()
        print("Raw folder data:", data)
        for line in data:
            print("Processing line:", line)  # Debug print
            try:
                folder = line.decode().split('"')[-2]
                folders.append(folder)
            except IndexError as e:
                print("Error processing line:", line, "; Error:", e)
                continue
        return folders


    def disconnect(self):
        self.connection.close()
        self.connection.logout()
