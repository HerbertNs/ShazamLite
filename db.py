import sqlite3

conn = sqlite3.connect('c:\\Users\\kbherbs\\Documents\\projects\\ShazamLite\\shazam1.db')
cursor = conn.cursor()

# Create table for song metadata
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL
)
''')

# Create table for fingerprints
cursor.execute('''
CREATE TABLE IF NOT EXISTS fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL,
    hash TEXT NOT NULL,
    offset INTEGER NOT NULL,
    FOREIGN KEY(song_id) REFERENCES songs(id)
)
''')

conn.commit()
conn.close()