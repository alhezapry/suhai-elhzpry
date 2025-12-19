from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os  # أضف هذا السطر

app = Flask(__name__)
CORS(app)

# استخدم متغير بيئة بدلاً من المفتاح المباشر
API_KEY = os.environ.get('HF_TOKEN', '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')
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

@app.route('/')
def home():
    return jsonify({
        "status": "Yaqeen AI Proxy is running!",
        "service": "Yemeni AI Assistant",
        "developer": "سهيل الهزبري"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "الخادم يعمل"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"success": False, "error": "الرسالة فارغة"})
        
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL}",
            headers=headers,
            json={"inputs": f"أنت مساعد يمني ذكي اسمه يقين AI. ارد بالعربية: {user_message}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result[0].get('generated_text', '...')
            return jsonify({"success": True, "text": ai_response})
        else:
            return jsonify({
                "success": False, 
                "error": f"خطأ من الخادم: {response.status_code}"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
