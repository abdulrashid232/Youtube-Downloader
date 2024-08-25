import tkinter
from pytube import YouTube, Stream
import sqlite3
from datetime import datetime
import threading

class YoutubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.geometry('500x300')
        self.root.resizable(1060,1027)
        self.root.title("Youtube Video Downloader")

        tkinter.Label(self.root, text='Youtube Video Downloader', font='arial 20 bold').pack()

        self.link = tkinter.StringVar()
        tkinter.Label(self.root, text='Paste Link Here:', font='arial 15 bold').place(x=160, y=60)
        link_enter = tkinter.Entry(self.root, width=70, textvariable=self.link).place(x=32, y=90)

        self.download_label = tkinter.Label(self.root, text='', font='arial 15')
        self.download_label.place(x=180, y=210)

        tkinter.Button(self.root, text='DOWNLOAD', font='arial 15 bold', bg='blue', padx=2, command=self.downloader).place(x=180, y=150)
        tkinter.Button(self.root, text='VIEW HISTORY', font='arial 15 bold', bg='green', padx=2, command=self.view_history).place(x=160, y=250)

        # Database connection and table creation
        self.conn = sqlite3.connect("download_history.db", check_same_thread=False)  # Allow database access from multiple threads
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS download_history (id INTEGER PRIMARY KEY, url TEXT, timestamp TEXT)")
        self.conn.commit()

        # Lock to synchronize database operations
        self.db_lock = threading.Lock()

    def downloader(self):
        url = str(self.link.get())  # Convert the URL to a string
        video = YouTube(url)
        self.download_thread = threading.Thread(target=self.download_video, args=(video, url))
        self.download_thread.start()

        self.download_label.config(text='Downloading...')

    def download_video(self, video, url):
        stream = self.select_stream_to_download(video.streams)
        if stream:
            stream.download()
            self.save_to_history(url)
            self.root.event_generate("<<DownloadComplete>>", when="tail")
        else:
            self.root.event_generate("<<DownloadFailed>>", when="tail")

    def select_stream_to_download(self, streams: Stream):
        #customize the selection of stream based on your preferences here
        # Let's say you want to download the highest resolution available
        highest_resolution_stream = streams.get_highest_resolution()
        return highest_resolution_stream

    def save_to_history(self, url):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db_lock:  
            self.cursor.execute("INSERT INTO download_history (url, timestamp) VALUES (?, ?)", (url, timestamp))
            self.conn.commit()

    def view_history(self):
        self.cursor.execute("SELECT * FROM download_history")
        history = self.cursor.fetchall()
        if history:
            history_window = tkinter.Toplevel(self.root)
            history_window.title("Download History")
            history_text = tkinter.Text(history_window)
            history_text.pack()

            for entry in history:
                history_text.insert(tkinter.END, f"URL: {entry[1]}\nDownloaded on: {entry[2]}\n\n")

root = tkinter.Tk()

downloader = YoutubeDownloader(root)

def on_download_complete(event):
    downloader.download_label.config(text='Downloaded')

def on_download_failed(event):
    downloader.download_label.config(text='Download failed')

root.bind("<<DownloadComplete>>", on_download_complete)
root.bind("<<DownloadFailed>>", on_download_failed)

root.mainloop()