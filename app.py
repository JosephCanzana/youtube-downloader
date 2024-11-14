import os

from pytubefix import YouTube
from flask import Flask, flash, redirect, render_template, request, send_file

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":

        url = request.form.get("url")

        try:
            yt = YouTube(url)
            title = yt.title
            file_path = yt.streams.get_highest_resolution().download(output_path='./downloads')
            file = send_file(file_path, as_attachment=True, download_name=f"{title}.mp4")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            return file 
        except:
            return apology("Invalid URL", 400) 
    else:
        return render_template("index.html")

    
def apology(message, code):
    return render_template("apology.html", message=message, code=code)

if __name__ == "__main__":
    app.run()