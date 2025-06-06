import os
import sqlite3
import librosa
import numpy as np
from scipy.signal import find_peaks

SONGS_FOLDER = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\songs'
DB_PATH = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\shazam2.db'

def ensure_tables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        filepath TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fingerprints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER NOT NULL,
        hash TEXT NOT NULL,
        offset INTEGER NOT NULL,
        FOREIGN KEY(song_id) REFERENCES songs(id)
    )
    ''')

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
ensure_tables(cursor)
conn.commit()

# Insert or update songs and filepaths
for filename in os.listdir(SONGS_FOLDER):
    if filename.endswith('.mp3'):
        name = filename[:-4]
        if '-' in name:
            title, artist = name.split('-', 1)
            title = title.strip()
            artist = artist.strip()
        else:
            print(f"Skipping file with unexpected name format: {filename}")
            continue

        filepath = os.path.join(SONGS_FOLDER, filename)
        # Check if song already exists
        cursor.execute("SELECT id FROM songs WHERE title = ? AND artist = ?", (title, artist))
        result = cursor.fetchone()
        if result:
            # Update filepath if needed
            cursor.execute(
                "UPDATE songs SET filepath = ? WHERE id = ?",
                (filepath, result[0])
            )
            song_id = result[0]
            print(f"Updated: {title} - {artist} ({filepath})")
        else:
            # Insert new song
            cursor.execute(
                "INSERT INTO songs (title, artist, filepath) VALUES (?, ?, ?)",
                (title, artist, filepath)
            )
            song_id = cursor.lastrowid
            print(f"Added: {title} - {artist} ({filepath})")

        # Check if fingerprints already exist for this song
        cursor.execute("SELECT COUNT(*) FROM fingerprints WHERE song_id = ?", (song_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Skipping fingerprints for {title} - {artist} (already exists)")
            continue

        # Generate and insert fingerprints
        try:
            fingerprints = generate_fingerprints(filepath)
            for hash_val, offset in fingerprints:
                cursor.execute(
                    "INSERT INTO fingerprints (song_id, hash, offset) VALUES (?, ?, ?)",
                    (song_id, hash_val, offset)
                )
            print(f"Inserted {len(fingerprints)} fingerprints for {title} - {artist}")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

conn.commit()
conn.close()