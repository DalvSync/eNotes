import os
from pathlib import Path
from crypto import encrypt, decrypt

NOTES_DIR = Path('notes')
NOTES_DIR.mkdir(parents=True, exist_ok=True)

def list_notes() -> list[str]:
    return [p.stem for p in NOTES_DIR.glob('*.enc')]

def save_note(name: str, text: str, password: str):
    data = encrypt(text.encode('utf-8'), password)
    with open(NOTES_DIR / f'{name}.enc', 'wb') as f:
        f.write(data)

def load_note(name: str, password: str) -> str:
    blob = (NOTES_DIR / f'{name}.enc').read_bytes()
    pt = decrypt(blob, password)
    return pt.decode('utf-8')
