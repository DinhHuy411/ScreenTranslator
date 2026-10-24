"""Phần 5 - Dịch bằng Azure Translator (REST API)."""
import os, requests

URL = "https://api.cognitive.microsofttranslator.com/translate"
CODES = {"zh-CN": "zh-Hans"}  # Azure dùng mã khác cho tiếng Trung giản thể


def translate(text, source="auto", target="vi"):
    key = os.environ.get("AZURE_TRANSLATOR_KEY")
    region = os.environ.get("AZURE_TRANSLATOR_REGION", "global")
    if not key:
        raise RuntimeError("Chưa cấu hình biến môi trường AZURE_TRANSLATOR_KEY.")
    params = {"api-version": "3.0", "to": target}
    if source != "auto":
        params["from"] = CODES.get(source, source)
    headers = {"Ocp-Apim-Subscription-Key": key,
               "Ocp-Apim-Subscription-Region": region,
               "Content-Type": "application/json"}
    try:
        r = requests.post(URL, params=params, headers=headers,
                          json=[{"Text": text[:10000]}], timeout=15)
    except requests.exceptions.RequestException:
        raise RuntimeError("Mất kết nối Internet. Vui lòng kiểm tra mạng.")
    if r.status_code in (401, 403):
        raise RuntimeError("Key hoặc Region Azure không đúng.")
    if r.status_code == 429:
        raise RuntimeError("Đã vượt giới hạn sử dụng. Hãy thử lại sau.")
    if not r.ok:
        raise RuntimeError(f"Dịch thất bại (HTTP {r.status_code}).")
    return r.json()[0]["translations"][0]["text"]
