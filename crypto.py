import sys
import os
import ctypes

def resource_path(relative_path):
    """ Отримує абсолютний шлях до ресурсів у скомпільованому файлі або локально """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

lib_name = "core.dll" if os.name == "nt" else "libcore.so"

lib_path = resource_path(lib_name)

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Криптографічне ядро не знайдено: {lib_path}")

lib = ctypes.cdll.LoadLibrary(lib_path)

if not os.path.exists(lib_path):
    print(f"ПОПЕРЕДЖЕННЯ: Ядро {lib_name} не знайдено. Переконайтесь, що ви його скомпілювали.")
else:
    core = ctypes.CDLL(lib_path)
    core.enotes_encrypt.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)), ctypes.POINTER(ctypes.c_size_t)]
    core.enotes_encrypt.restype = ctypes.c_int
    core.enotes_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)), ctypes.POINTER(ctypes.c_size_t)]
    core.enotes_decrypt.restype = ctypes.c_int
    core.enotes_free.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
    core.enotes_free.restype = None

    def encrypt(data: bytes, password: str) -> bytes:
        out_buffer = ctypes.POINTER(ctypes.c_uint8)()
        out_len = ctypes.c_size_t(0)
        res = core.enotes_encrypt(data, len(data), password.encode('utf-8'), ctypes.byref(out_buffer), ctypes.byref(out_len))
        if res != 0: raise Exception(f"Помилка шифрування у C-ядрі (код {res})")
        result_bytes = ctypes.string_at(out_buffer, out_len.value)
        core.enotes_free(out_buffer, out_len.value)
        return result_bytes

    def decrypt(blob: bytes, password: str) -> bytes:
        out_buffer = ctypes.POINTER(ctypes.c_uint8)()
        out_len = ctypes.c_size_t(0)
        res = core.enotes_decrypt(blob, len(blob), password.encode('utf-8'), ctypes.byref(out_buffer), ctypes.byref(out_len))
        if res == -5: raise Exception("Невірний пароль або пошкоджений файл")
        elif res != 0: raise Exception(f"Помилка розшифрування у C-ядрі (код {res})")
        result_bytes = ctypes.string_at(out_buffer, out_len.value)
        core.enotes_free(out_buffer, out_len.value)
        return result_bytes

def get_auth_hash(password: str) -> str:
    """Генерує токен для сервера з пароля."""
    return hashlib.sha256((password + "eNotes_cloud_salt").encode()).hexdigest()