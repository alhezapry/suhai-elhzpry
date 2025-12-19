from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# استرجاع مفتاح API من متغير البيئة الآمن - لا تضعه هنا مباشرة!
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
# إذا لم يتم ضبط المفتاح، نستخدم قيمة فارغة وسيفشل الاتصال بوضوح
if not GROQ_API_KEY:
    print("⚠️  تحذير: لم يتم تعيين متغير البيئة 'GROQ_API_KEY'. سيفشل الاتصال بـ Groq API.")

@app.route('/')
def home():
    return jsonify({
        "status": "Yaqeen AI Proxy is running!",
        "service": "Yemeni AI Assistant - يقين AI (مدعوم بـ Groq)",
        "developer": "سهيل الهزبري",
        "endpoints": {
            "/chat": "POST - إرسال رسالة للذكاء الاصطناعي",
            "/health": "GET - فحص حالة الخادم"
        },
        "provider": "Groq Cloud"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "✅ خادم يقين AI يعمل بنجاح مع تكامل Groq",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """النقطة الرئيسية للدردشة مع الذكاء الاصطناعي عبر Groq API"""
    try:
        # 1. التحقق من وجود مفتاح API
        if not GROQ_API_KEY:
            return jsonify({
                "success": False,
                "error": "مفتاح API غير مضبوط. الرجاء تعيين متغير البيئة 'GROQ_API_KEY' على Render."
            }), 500

        # 2. استقبال ومعالجة بيانات المستخدم
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "لم يتم إرسال بيانات."}), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"success": False, "error": "الرسالة فارغة. الرجاء كتابة سؤال."}), 400

        # 3. إعداد طلب Groq API (متوافق مع OpenAI)
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mixtral-8x7b-32768",  # نموذج Mixtral سريع وقوي من Groq
            "messages": [
                {
                    "role": "system",
                    "content": "أنت مساعد ذكي يمني اسمه 'يقين AI'. مهمتك هي مساعدة المستخدمين بلغة عربية واضحة ومفيدة مع الحفاظ على الود والاحترام. أضف لمسات يمنية ودية في ردودك عندما يكون ذلك مناسباً."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "stream": False
        }

        # 4. إرسال الطلب إلى Groq API
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45  # مهلة أطول قليلاً
        )

        # 5. معالجة الرد من Groq
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            return jsonify({
                "success": True,
                "text": ai_response,
                "provider": "Groq (mixtral-8x7b-32768)",
                "timestamp": datetime.now().isoformat(),
                "note": "مدعوم بـ Groq Cloud - واجهة متوافقة مع OpenAI"
            })

        elif response.status_code == 429:
            return jsonify({
                "success": False,
                "error": "تم تجاوز الحد المسموح من الطلبات للمفتاح المجاني. يرجى المحاولة لاحقاً.",
                "status_code": 429
            }), 429

        else:
            # محاولة إرجاع رسالة الخطأ من Groq إن وجدت
            error_detail = "تفاصيل غير متاحة"
            try:
                error_json = response.json()
                if 'error' in error_json and 'message' in error_json['error']:
                    error_detail = error_json['error']['message']
            except:
                error_detail = response.text[:200] if response.text else "لا يوجد نص للخطأ"

            return jsonify({
                "success": False,
                "error": f"خطأ من خادم Groq: {response.status_code}",
                "details": error_detail,
                "status_code": response.status_code
            }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "انتهت مهلة الاتصال بخادم Groq. يرجى المحاولة مرة أخرى."
        }), 408

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"حدث خطأ غير متوقع في الخادم: {str(e)[:150]}"
        }), 500

@app.route('/models', methods=['GET'])
def list_models():
    """نقطة نهاية إضافية لسرد النماذج المتاحة (للاطلاع فقط، قد تتطلب صلاحيات)"""
    if not GROQ_API_KEY:
        return jsonify({"success": False, "error": "مفتاح API مطلوب"}), 401

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=30)
        if response.status_code == 200:
            return jsonify({"success": True, "models": response.json()})
        else:
            return jsonify({"success": False, "error": f"خطأ: {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # تحذير في السجلات إذا لم يتم ضبط المفتاح
    if not GROQ_API_KEY:
        print("❌ تحذير حرج: متغير البيئة 'GROQ_API_KEY' غير مضبوط. لن تعمل نقطة /chat.")
    app.run(host='0.0.0.0', port=port, debug=False)
