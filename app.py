import os

from pytubefix import YouTube
from flask import Flask, flash, redirect, render_template, request, send_file,session,after_this_request,url_for
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=10)

# Home page
@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":

        #looking for the cookie if it exist
        if 'used' not in session:
            session['used'] = False

        url = request.form.get("url")

        # Error handling
        try:
            yt = YouTube(url)
            # Storing url to the session
            session["video_url"] = url

            # Storing non duplicates streams
            initial_streams = yt.streams
            streams = []
            seen_resolutions = set()  
            for stream in initial_streams:
                if stream.mime_type == "video/mp4" and stream.resolution not in seen_resolutions:
                    streams.append(stream)
                    seen_resolutions.add(stream.resolution)

            return render_template("resolution.html", title=yt.title ,streams=streams)

        except:
            return apology("Invalid URL", 400)
    else:
        return render_template("index.html")

@app.route("/resolution", methods=["GET", "POST"])
def resolution():
    # Getting the session url
    yt = YouTube(session["video_url"])

    if request.method == "POST":

        # Preparing itag for resolution
        resolution = request.form.get("stream_itag")
        stream = yt.streams.get_by_itag(resolution)

        # If stream has no error
        if stream:

            # Create temporary file holder (server side)
            download_folder = "./downloads"
            os.makedirs(download_folder, exist_ok=True)
          
            # Download the file and send to the temporary folder          
            stream_path = stream.download(output_path=download_folder)

            # After request to delete the file from the temporary folder
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(stream_path) 
                except Exception as e:
                    print(f"Error removing file: {e}")
                return response

            # Save file to the client side computer
            return send_file(stream_path, as_attachment=True,download_name=f"{yt.title}.mp4")
        else:
            return apology("Invalid stream selected", 400)
    else:
        return redirect("/")

# Apology function
def apology(message, code):
    return render_template("apology.html", message=message, code=code)

if __name__ == "__main__":
    app.run()