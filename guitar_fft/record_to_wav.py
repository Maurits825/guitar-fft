import sounddevice as sd
import scipy.io.wavfile

fs = 44100
duration = 5  # seconds
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
sd.wait()

scipy.io.wavfile.write('recording.wav', fs, myrecording)
