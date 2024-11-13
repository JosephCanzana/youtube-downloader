from pytubefix import YouTube
from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        try:
            yt = YouTube(url)
            title = yt.title
            yt.streams.get_highest_resolution().download(output_path='./downloads')
        except:
            return apology("Invalid URL", 400)   

        return render_template("success.html", title=title)
    else:
        return render_template("index.html")
    
def apology(message, code):
    return render_template("apology.html", message=message, code=code)

if __name__ == "__main__":
    app.run()