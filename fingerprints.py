import sqlite3
import librosa
import numpy as np
from scipy.signal import find_peaks

DB_PATH = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\shazam2.db'

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

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, filepath FROM songs WHERE filepath != ''")
songs = cursor.fetchall()

for song_id, filepath in songs:
    # Check if fingerprints already exist for this song
    cursor.execute("SELECT COUNT(*) FROM fingerprints WHERE song_id = ?", (song_id,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Skipping song ID {song_id} (fingerprints already exist)")
        continue

    print(f"Generating fingerprints for: {filepath}")
    try:
        fingerprints = generate_fingerprints(filepath)
        for hash_val, offset in fingerprints:
            cursor.execute(
                "INSERT INTO fingerprints (song_id, hash, offset) VALUES (?, ?, ?)",
                (song_id, hash_val, offset)
            )
        print(f"Inserted {len(fingerprints)} fingerprints for song ID {song_id}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

conn.commit()
conn.close()