import sounddevice as sd
import scipy.io.wavfile

fs = 44100
duration = 5  # seconds
recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
sd.wait()

scipy.io.wavfile.write('../resources/recording.wav', fs, recording)
