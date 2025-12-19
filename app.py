from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # هذا يحل مشكلة CORS للأبد!

# سيأخذ المفتاح من متغير البيئة على Render.com
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

@app.route('/')
def home():
    return jsonify({
        "status": "Yaqeen AI Proxy Server",
        "service": "Yemeni AI Assistant - يقين AI",
        "developer": "سهيل الهزبري",
        "endpoints": {
            "/chat": "POST - إرسال رسالة للذكاء الاصطناعي",
            "/health": "GET - فحص حالة الخادم"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "✅ خادم يقين AI يعمل بنجاح",
        "timestamp": "2023-01-01T00:00:00Z"  # سيتغير تلقائياً
    })

@app.route('/chat', methods=['POST'])
def chat():
    """نقطة النهاية الرئيسية للدردشة مع الذكاء الاصطناعي"""
    try:
        # الحصول على البيانات من الطلب
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "لم يتم إرسال بيانات"
            }), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "الرسالة فارغة. الرجاء كتابة سؤال."
            }), 400
        
        if not HF_TOKEN:
            return jsonify({
                "success": False,
                "error": "مفتاح API غير مضبوط. الرجاء إضافة HF_TOKEN في متغيرات البيئة."
            }), 500
        
        # إعداد الطلب لـ Hugging Face API
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # نص الذكاء الاصطناعي (مع توجيه للرد بالعربية)
        prompt = f"""أنت مساعد ذكي يمني اسمه 'يقين AI'. 
        مهمتك هي مساعدة المستخدمين باللغة العربية.
        كن مفيداً، دقيقاً، ومحترماً مع إضافة لمسات يمنية أحياناً.
        
        سؤال المستخدم: {user_message}
        
        رَدٌّ المساعد (باللغة العربية):"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        # إرسال الطلب إلى Hugging Face
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODEL}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # معالجة الرد
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', 'لم أتمكن من توليد رد.')
            else:
                ai_response = "عذراً، لم أتلقَ رداً من النموذج."
            
            return jsonify({
                "success": True,
                "text": ai_response,
                "provider": MODEL,
                "tokens_used": "unknown"
            })
            
        elif response.status_code == 503:
            # النموذج قيد التحميل
            return jsonify({
                "success": False,
                "error": "النموذج قيد التحميل. يرجى المحاولة مرة أخرى خلال 20-30 ثانية.",
                "status_code": 503
            }), 200
            
        else:
            return jsonify({
                "success": False,
                "error": f"خطأ من خادم Hugging Face: {response.status_code}",
                "details": response.text[:200] if response.text else ""
            }), 200
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "انتهت مهلة الانتظار. الخادم مشغول جداً."
        }), 408
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"خطأ داخلي: {str(e)[:100]}"
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """نقطة نهاية للاختبار السريع"""
    return jsonify({
        "success": True,
        "message": "✅ خادم يقين AI يعمل!",
        "next_step": "أرسل POST request إلى /chat مع {message: 'نصك هنا'}"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
