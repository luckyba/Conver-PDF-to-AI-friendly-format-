import pytesseract
from pdf2image import convert_from_path

# Đường dẫn Tesseract (Windows cần set)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Lucky Man\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

poppler_path = r"C:\Users\Lucky Man\Downloads\tools\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Chuyển PDF sang ảnh (300 DPI để rõ hơn)
pages = convert_from_path(r"C:\Users\Lucky Man\Downloads\baitap\Toán lớp 1 tập 2 kết nối tri thức cuộc sống.pdf", dpi=300, poppler_path=poppler_path)

results = []
for i, page in enumerate(pages, start=1):
    text = pytesseract.image_to_string(page, lang="vie")
    results.append({"page": i, "text": text})

# Xuất ra file JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("✅ Đã lưu kết quả OCR vào output.json")
