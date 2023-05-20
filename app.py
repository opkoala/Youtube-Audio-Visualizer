from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import librosa
from pytube import YouTube
import sounddevice as sd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        link = request.form.get('url')
        try:
            url = YouTube(link)
            url.check_availability()
            session['link'] = link
            return redirect(url_for('download'))
        except:
            return render_template('error.html')
    return render_template('home.html')

@app.route('/download')
def download():
    link = session.get('link')
    if link:
        youtube = YouTube(link)
        audio_stream = youtube.streams.filter(only_audio=True).first()
        download_name = audio_stream.download()
        session['download_name'] = download_name
        return redirect(url_for('visualize'))
    else:
        return redirect(url_for('home'))

@app.route('/visualize')
def visualize():
    download_name = session.get('download_name')
    if download_name:
        audio_data, sample_rate = librosa.load(download_name, sr=None)

        CHUNK = 1024  # Number of samples per chunk

        plt.ion()  # Turn on interactive mode
        fig, ax = plt.subplots()
        x = np.arange(0, CHUNK)  # x-axis for the plot
        line, = ax.plot(x, np.zeros(CHUNK))
        ax.set_xlim(0, CHUNK)
        ax.set_ylim(-1, 1)  # Adjust based on your audio input range

        # Start playing the audio
        sd.play(audio_data[:CHUNK], sample_rate)

        while True:
            # Update the plot with the new audio signal
            audio_signal = audio_data[:CHUNK]
            line.set_ydata(audio_signal)
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Remove the plotted samples from the audio data
            audio_data = audio_data[CHUNK:]

            if len(audio_data) < CHUNK:
                # End of the audio file
                break

        sd.stop()  # Stop audio playback
        plt.close(fig)

        return render_template('index.html', message='Audio played and visualized.')
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
