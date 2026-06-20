import requests

def extract_text(image_path):
    # ضعي مفتاحك هنا بين علامتي التنصيص
    api_key = "K84489712688957" 
    url = "https://api.ocr.space/parse/image"
    
    try:
        with open(image_path, 'rb') as f:
            payload = {
                'apikey': api_key,
                'language': 'ara',  # يقرأ العربية
                'isOverlayRequired': False,
            }
            files = {'file': f}
            response = requests.post(url, data=payload, files=files)
            
        result = response.json()
        
        # التأكد أن الـ API رد بنجاح
        if result.get("IsErroredOnProcessing"):
            return "حدث خطأ في الاتصال بالخدمة."
        
        # استخراج النص من النتيجة
        return result["ParsedResults"][0]["ParsedText"]
        
    except Exception as e:
        return f"خطأ برمجيا: {str(e)}"
