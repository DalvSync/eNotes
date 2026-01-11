import os
from pathlib import Path
from crypto import encrypt, decrypt

NOTES_DIR = Path('notes')
NOTES_DIR.mkdir(parents=True, exist_ok=True)

def list_notes() -> list[str]:
    """Список имён файлов без расширения."""
    return [p.stem for p in NOTES_DIR.glob('*.enc')]

def save_note(name: str, html_content: str, password: str):
    """
    Сохраняет заметку. html_content — строка HTML (может содержать data: URI для изображений).
    """
    if not isinstance(html_content, str):
        raise TypeError("html_content must be str")
    data = html_content.encode('utf-8')
    blob = encrypt(data, password)
    with open(NOTES_DIR / f'{name}.enc', 'wb') as f:
        f.write(blob)

def load_note(name: str, password: str) -> str:
    """
    Загружает и расшифровывает заметку, возвращает строку (HTML).
    """
    blob = (NOTES_DIR / f'{name}.enc').read_bytes()
    pt = decrypt(blob, password)
    return pt.decode('utf-8')
