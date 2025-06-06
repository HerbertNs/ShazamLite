import os
import sqlite3

SONGS_FOLDER = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\songs'
DB_PATH = 'c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\shazam1.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add the filepath column if it doesn't exist
try:
    cursor.execute("ALTER TABLE songs ADD COLUMN filepath TEXT NOT NULL DEFAULT ''")
    print("Added 'filepath' column to 'songs' table.")
except sqlite3.OperationalError:
    pass

conn.commit()
# Do NOT close the connection here

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
        # Update the filepath for the matching song
        cursor.execute(
            "UPDATE songs SET filepath = ? WHERE title = ? AND artist = ?",
            (filepath, title, artist)
        )
        print(f"Updated: {title} - {artist} ({filepath})")

conn.commit()
conn.close()