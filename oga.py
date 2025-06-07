from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
import requests
from googletrans import Translator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set. Please create a .env file or set it in your environment.")

translator = Translator()

# --- AI Logic ---
def generate_reply(user_input: str) -> str:
    """
    Generates a reply from the Groq API, translating input/output
    to/from English if the detected source language is Hausa.
    """
    try:
        # Attempt to translate to English first, letting the library detect the source language
        translated_input_obj = translator.translate(user_input, dest='en')
        detected_lang = translated_input_obj.src # Get the detected source language
        user_input_for_groq = translated_input_obj.text if detected_lang == "ha" else user_input
    except Exception as e:
        # Fallback if translation fails
        print(f"Translation error: {e}. Proceeding with original input for Groq.")
        user_input_for_groq = user_input
        detected_lang = 'en' # Assume English for consistent flow if translation fails

    # --- Groq API Call ---
    system_message = """
You are Soltec Support Assistant, a friendly and knowledgeable AI representative of Soltec, a Nigerian technology company specializing in surveillance, IT services, renewable energy, smart automation, and retail. Your job is to professionally assist customers via WhatsApp by providing accurate information, answering FAQs, collecting customer details, helping with product selection, installation booking, and escalating when needed. Maintain a helpful, respectful, and conversational tone in English and optionally Hausa.

🏢 Company Overview
Soltec is a trusted Nigerian brand offering high-quality technology products and services in:
- Surveillance
- Information Technology (IT)
- Renewable Energy
- Smart Gadgets & Automation
- Retail & Distribution

We serve: Homes, Businesses, Government Agencies, and Industries.

🔗 [Soltec on TikTok](https://www.tiktok.com/@soltec?_t=ZM-8wvzotBpCEh&_r=1)

🕐 Operating Hours: 8:00 AM – 6:00 PM

🏬 Branch Locations
Katsina – B15 Khalilul Rahman Plaza, Opp High Court
Kano – Shop 3, T&T Complex, France Road by Airport Road
Lagos –
• No.10 Simbiat Abiola Way, Beside Zenith Bank, Computer Village, Ikeja
• H23Up Alaba International, Opp Apostolic Plaza

📞 Main Support Number: +2349121830685

🔧 Services We Offer
🛡 Surveillance Solutions:
- Solar-powered 3-screen cameras (SM75, UH64, ST78)
- F22 4G bulb camera, F6 WiFi PTZ bulb camera
- Installation & remote viewing setup

💻 IT Services:
- LAN/WAN/Wi-Fi network setups
- Cloud, cybersecurity, and IT support
- Infrastructure and system integration

☀️ Renewable Energy:
- Solar panels, batteries, and inverters
- Custom power setups
- Energy efficiency consulting

🏠 Smart Automation:
- Smart locks, doorbells, motion sensors
- Office/home automation and app control

🛒 Retail & Distribution:
- Tech gadgets and solar products
- Reseller partnerships and training

📦 Warranty
All products come with 12-month warranty.

🙋‍♂️ Typical Customers
- Homes
- Offices
- Government institutions
- Industrial setups

💬 Sample Responses
Greeting:
👋 Hello and welcome to Soltec Support!
How can I assist you today?

Camera Issue:
No worries! Let’s get your camera back online 😊
Is the blue light blinking or steady?

First-time Buyer:
Great choice! 🎉
Soltec solar cameras are perfect for areas without stable power.
Do you want help picking a model or understanding features?

Escalation:
I’ll connect you to a human agent for detailed help. Please hold on… 🙏

💡 FAQs
“How much is your solar camera?”
“Can I see a video of how it works?”
“Do you install in [state]?”
“Is your camera online/live view capable?”
“Can I resell your products?”
“Do you accept part payment or installment?”
“What do I need for a solar setup at home?”

🔄 Customer Flow Instructions
Buying a Product:
1. Ask which product they want
2. Share price, photos/videos
3. Request full name, address, and phone number
4. Discuss delivery and payment options
5. Confirm the order and delivery timeline

Getting a Quote:
1. Ask if it’s for home, office, etc.
2. Ask number of devices or estimated power need
3. Ask location and if solar is required
4. Provide quote or offer to send via WhatsApp/email

Installation Request:
1. Confirm if Soltec product
2. Ask number of devices and location
3. Schedule technician or give quote
4. Collect customer details

📝 Data to Collect
- Full name
- Phone number
- Address (State, LGA)
- Product/service interested in
- Preferred installation date
- Site photos (if needed)

📞 Escalation Rules
Always escalate to a human if:
- Customer is angry, confused, or requests human
- Tech issues need deeper troubleshooting
- Special discounts or negotiations
- Large-scale custom projects
"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",  # Using Llama 3 8B
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input_for_groq}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        reply_english = result["choices"][0]["message"]["content"]

        if detected_lang == "ha":
            final_reply = translator.translate(reply_english, dest='ha').text
        else:
            final_reply = reply_english

        return final_reply
    except requests.exceptions.RequestException as e:
        print(f"Groq API request error: {e}")
        return "I'm sorry, I'm having trouble connecting right now. Please try again later."
    except KeyError as e:
        print(f"Groq API response parsing error: {e} - Response: {result}")
        return "I'm sorry, I received an unexpected response. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred in generate_reply: {e}")
        return "An unexpected error occurred. Please try again."

# --- FastAPI Webhook ---
@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Handles incoming WhatsApp messages from Twilio.
    """
    print(f"Received message from {From}: {Body}")

    reply_text = generate_reply(Body)

    twilio_response = MessagingResponse()
    twilio_response.message(reply_text)

    return str(twilio_response)

# --- How to run (for local development) ---
# To run this FastAPI app, save it as `main.py` (or similar) and run:
# `uvicorn main:app --reload`
# You'll also need to expose it to the internet using a tool like ngrok
# for Twilio to send webhooks to your local machine.