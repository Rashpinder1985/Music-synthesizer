import streamlit as st
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, square, sawtooth
import wave

# Constants
SAMPLE_RATE = 44100  # 44.1 kHz sample rate
DURATION = 1.0       # 1-second sound

# Generate different waveforms
def generate_waveform(wave_type, frequency):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    if wave_type == "Sine":
        wave = np.sin(2 * np.pi * frequency * t)
    elif wave_type == "Square":
        wave = square(2 * np.pi * frequency * t)
    elif wave_type == "Sawtooth":
        wave = sawtooth(2 * np.pi * frequency * t)
    else:
        wave = np.zeros_like(t)
    return t, wave

# Apply filters
def apply_filter(data, low_cutoff, high_cutoff, filter_type="low"):
    nyquist = 0.5 * SAMPLE_RATE
    if filter_type == "low":
        normal_cutoff = low_cutoff / nyquist
        b, a = butter(5, normal_cutoff, btype='low', analog=False)
    elif filter_type == "high":
        normal_cutoff = high_cutoff / nyquist
        b, a = butter(5, normal_cutoff, btype='high', analog=False)
    elif filter_type == "band":
        if low_cutoff >= high_cutoff:
            return data
        low_normal = low_cutoff / nyquist
        high_normal = high_cutoff / nyquist
        b, a = butter(5, [low_normal, high_normal], btype='band', analog=False)
    else:
        return data  # No filtering

    return lfilter(b, a, data)

# Streamlit UI
st.title("🎵 Real-Time Music Synthesizer")

# User inputs
wave_type = st.selectbox("Select Waveform", ["Sine", "Square", "Sawtooth"], index=0)
frequency = st.slider("Frequency (Hz)", 100, 2000, 440)
filter_type = st.selectbox("Select Filter Type", ["low", "high", "band"], index=0)
low_cutoff = st.slider("Low Cutoff (Hz)", 100, 4000, 500)
high_cutoff = st.slider("High Cutoff (Hz)", 500, 5000, 2000)

# Generate waveform
t, wave = generate_waveform(wave_type, frequency)

# Apply selected filter
if filter_type == "band":
    filtered_wave = apply_filter(wave, low_cutoff, high_cutoff, "band")
else:
    filtered_wave = apply_filter(wave, low_cutoff, high_cutoff, filter_type)

# Automatically play sound when waveform or frequency is changed
sd.stop()  # Stop any ongoing playback before playing new sound
sd.play(filtered_wave, SAMPLE_RATE)

# Save to WAV file function
def save_wave():
    filename = f"{wave_type}_{filter_type}_filtered.wav"
    wave_int16 = np.int16(filtered_wave * 32767)

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(wave_int16.tobytes())

    st.success(f"Saved: {filename}")

# Save button
if st.button("💾 Save as WAV"):
    save_wave()

# Plot waveform
fig, ax = plt.subplots(figsize=(5, 3))
ax.plot(t[:1000], filtered_wave[:1000])
ax.set_title(f"{wave_type} Wave ({filter_type}-pass)")
ax.set_xlabel("Time")
ax.set_ylabel("Amplitude")
st.pyplot(fig)

