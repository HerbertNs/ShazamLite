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

def identify_song(sample_filepath, cursor, top_n=1):
    sample_fingerprints = generate_fingerprints(sample_filepath)
    hash_list = [fp[0] for fp in sample_fingerprints]
    if not hash_list:
        print("No fingerprints can be  generated from sample.")
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

    if not results:
        print("No matching song found.")
        return None

    song_id = results[0][0]
    cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (song_id,))
    song_info = cursor.fetchone()
    print(f"Best match: {song_info[0]} - {song_info[1]} (matches: {results[0][1]})")
    return song_info

if __name__ == "__main__":
    sample_path = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\sample.mp3'  
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    identify_song(sample_path, cursor)
    conn.close()