import os

from pytubefix import YouTube
from flask import Flask, redirect, render_template, request, send_file,session,after_this_request,url_for
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
        if not url.startswith("https://www.youtube.com/") and not url.startswith("https://youtu.be/"):
            return apology("Invalid YouTube URL. Please provide a valid link.", 400)

        try:
            yt = YouTube(url, use_po_token=True)
        except EOFError:
            print("Error: No data received. Please try again.")
            return apology("Failed to retrieve video. Try again later. line 28", 400)
        # Error handling
        try:

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

        except Exception as e:
            print(f"Error occurred: {e}")
            return apology(f"An error occurred: {str(e)}", 400)
    else:
        return render_template("index.html")

@app.route("/resolution", methods=["GET", "POST"])
def resolution():
    # Getting the session url
    # Ensure the video URL exists in the session
    if "video_url" not in session:
        return redirect("/")
    
    yt = YouTube(session["video_url"], use_po_token=True)

    if request.method == "POST":

        # Preparing itag for resolution
        resolution = request.form.get("stream_itag")
        stream = yt.streams.get_by_itag(resolution)

        # If stream has no error
        if stream:

            # Create temporary file holder (server side)
            download_folder = os.path.join(os.getcwd(), "downloads")
            os.makedirs(download_folder, exist_ok=True)
          
            # Download the file and send to the temporary folder         
            try:
                stream_path = stream.download(output_path=download_folder)

                # Schedule file cleanup after response
                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(stream_path)
                    except Exception as e:
                        print(f"Error removing file: {e}")
                    return response

                # Send file to the client
                return send_file(stream_path,as_attachment=True,download_name=f"{yt.title}.mp4",)
            
            except Exception as e:
                print(f"Error downloading file: {e}")
                return apology("Failed to download the video.", 400)
        else:
            return apology("Invalid stream selected", 400)
    else:
        return redirect("/")

# Apology function
def apology(message, code=400):
    return render_template("apology.html", message=message, code=code),code

if __name__ == "__main__":
    app.run(debug=True)