import os
import sqlite3
import librosa
import numpy as np
from scipy.signal import find_peaks
import sounddevice as sd
from scipy.io.wavfile import write

DB_PATH = 'ShazamLite\\shazam2.db'

def record_sample(output_path, duration=10, fs=44100):
    print(f"Recording {duration} seconds of audio...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(output_path, fs, recording)
    print(f"Saved recording to {output_path}")

def generate_fingerprints(filepath):
    y, sr = librosa.load(filepath, mono=True, duration=30)
    S = np.abs(librosa.stft(y))
    fingerprints = []
    for freq_bin in range(S.shape[0]):
        peak_indices, _ = find_peaks(S[freq_bin], height=np.max(S[freq_bin]) * 0.5)
        for t in peak_indices:
            hash_val = f"{freq_bin}-{t}"
            fingerprints.append((hash_val, t))
    return fingerprints

def identify_song(sample_filepath, cursor, top_n=1):
    sample_fingerprints = generate_fingerprints(sample_filepath)
    hash_list = [fp[0] for fp in sample_fingerprints]
    if not hash_list:
        print("No fingerprints generated from sample.")
        return None

    placeholders = ','.join('?' for _ in hash_list)
    query = f"""
        SELECT song_id, COUNT(*) as match_count
        FROM fingerprints
        WHERE hash IN ({placeholders})
        GROUP BY song_id
        ORDER BY match_count DESC
        LIMIT ?
    """
    cursor.execute(query, (*hash_list, top_n))
    results = cursor.fetchall()

    if not results or results[0][1] < 100:
        print("No matching song found.")
        return None

    song_id = results[0][0]
    cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (song_id,))
    song_info = cursor.fetchone()
    print(f"Best match: {song_info[0]} - {song_info[1]} (matches: {results[0][1]})")
    return song_info

if __name__ == "__main__":
    sample_path = 'ShazamLite\\mic_sample.wav'
    record_sample(sample_path, duration=10)  # Record 8 seconds from mic

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    identify_song(sample_path, cursor)
    conn.close()

    # Delete the recorded sample after matching
    if os.path.exists(sample_path):
        os.remove(sample_path)
