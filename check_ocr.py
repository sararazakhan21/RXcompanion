import os
import platform

print("=" * 60)
print("OCR DIAGNOSTIC")
print("=" * 60)

# 1. Check Python packages
print("\n[1] Python packages:")
try:
    import cv2
    print(f"    ✅ opencv: {cv2.__version__}")
except ImportError as e:
    print(f"    ❌ opencv NOT installed: {e}")

try:
    import pytesseract
    print(f"    ✅ pytesseract installed")
except ImportError as e:
    print(f"    ❌ pytesseract NOT installed: {e}")

try:
    from PIL import Image
    print(f"    ✅ PIL (Pillow) installed")
except ImportError as e:
    print(f"    ❌ PIL NOT installed: {e}")

# 2. Check Tesseract binary paths
print("\n[2] Tesseract executable paths:")
paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
]
for p in paths:
    exists = "✅" if os.path.exists(p) else "❌"
    print(f"    {exists} {p}")

# 3. Try running tesseract
print("\n[3] Trying pytesseract.get_tesseract_version():")
try:
    import pytesseract
    for p in paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            print(f"    Testing: {p}")
            break
    ver = pytesseract.get_tesseract_version()
    print(f"    ✅ Tesseract version: {ver}")
except Exception as e:
    print(f"    ❌ Error: {type(e).__name__}: {e}")

# 4. Platform info
print(f"\n[4] Platform: {platform.system()} {platform.release()}")
print(f"    Python executable: {os.sys.executable}")

print("\n" + "=" * 60)