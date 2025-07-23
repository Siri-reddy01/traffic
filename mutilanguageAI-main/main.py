import streamlit as st
import requests
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import re
import random
import boto3
import json

# CONFIGURATION
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") or "66rqaiQNC3XdRL7BZuFMmvnO33bKZNOp2209fmVhPuAe813HEzxjSd0h"
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY") or ""
BG_IMAGE_URL = "https://photutorial.com/wp-content/uploads/2023/04/Featured-image-AI-image-generators-by-Midjourney.png"

translator = Translator()
tts_supported = tts_langs()
translator_supported = {k.lower(): v.title() for k, v in LANGUAGES.items()}

ALL_LANGUAGE_CHOICES = [
    f"{name} ({code}){' (🔊 Voice)' if code in tts_supported else ' (📝 Text)'}"
    for code, name in sorted(translator_supported.items(), key=lambda x: x[1])
]
TIP_LIST = [
    "🌎 Over 200 languages • Enjoy text & voice answers instantly.",
    "🔊 Voice output enabled for Kannada, Hindi, Tamil and more.",
    "🖼️ Images fetched from best AI image APIs.",
    "✨ Try: Explain AI in French, Python basics in Telugu.",
    "💡 'Copy' any box with a click for instant reuse."
]

def add_custom_styles():
    st.markdown(f"""
    <style>
    body {{
      background: url('{BG_IMAGE_URL}') no-repeat center center fixed !important;
      background-size: cover !important; min-height:100vh;
    }}
    .stApp {{
      background: rgba(18,20,41,0.86); min-height:100vh; color:#f4f4f7;
    }}
    </style>
    """, unsafe_allow_html=True)

def add_emojis(text):
    emojis = {
        "title": "🤖", "generated_info": "📜", "translation": "🌍",
        "button": "🔄", "language": "🗣️", "creator": "💡"
    }
    for name, emoji in emojis.items():
        text = text.replace(f"{{{name}_emoji}}", emoji)
    return text

def get_language_code(lang_display):
    match = re.search(r"\\(([^)]+)\\)", lang_display)
    if match:
        return match.group(1).strip().lower()
    return "en"

def is_voice_supported(code):
    return code in tts_supported

def llama70b(prompt):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")  # change to your region
    model_id = "meta.llama3-70b-instruct-v1:0"
    body = {
        "prompt": f"<s>[INST] {prompt} [/INST]",
        "max_gen_len": 1024,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response["body"].read())
        return response_body["generation"].strip()
    except Exception as e:
        return f"Bedrock Exception: {e}"

def translate_text(text, code):
    try:
        result = translator.translate(text, dest=code.lower())
        return result.text
    except Exception as e:
        return f"Translation error: {e}"

def synthesize_speech(text, code):
    try:
        tts = gTTS(text=text, lang=code.lower())
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            audio_bytes = open(fp.name, "rb").read()
        os.unlink(fp.name)
        return audio_bytes
    except Exception as e:
        return None

def fetch_pexels_image(query):
    if not PEXELS_API_KEY:
        return None
    headers = {'Authorization': PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        data = resp.json()
        if data.get('photos'):
            return data['photos'][0]['src']['original']
    except Exception as e:
        return None

def fetch_unsplash_image(query):
    if not UNSPLASH_KEY:
        return None
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
    try:
        resp = requests.get(url, timeout=20)
        data = resp.json()
        return data.get('urls', {}).get('regular')
    except Exception as e:
        return None

def fetch_best_image(query):
    return fetch_pexels_image(query) or fetch_unsplash_image(query)

def main():
    add_custom_styles()
    st.markdown(f'<div class="title">{add_emojis("AI Multilanguage Assistant {title_emoji}")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="description">Modern AI: 200+ languages, smart images, full-voice, glass UI, and vibrant feel for all answers.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-tips">{random.choice(TIP_LIST)}</div>', unsafe_allow_html=True)
    with st.form("prompt-form", clear_on_submit=False):
        query = st.text_input("🔎 Enter your query here:")
        language_select = st.selectbox("🌐 Choose language (voice/text):", ALL_LANGUAGE_CHOICES, index=0)
        submit = st.form_submit_button("✨ Generate", use_container_width=True)
    code = get_language_code(language_select)
    can_voice = is_voice_supported(code)
    if submit:
        with st.spinner("Generating..."):
            ai_answer = llama70b(query)
            translation = translate_text(ai_answer, code)
            img_url = fetch_best_image(query)
        st.markdown(f'<div class="glass-wrap generated-info"><b>📜 Answer:</b><br><span style="font-size:1.04em;line-height:1.56;">{ai_answer}</span></div>', unsafe_allow_html=True)
        st.button("📋 Copy AI Answer", on_click=lambda: st.session_state.update({'ai_answer': ai_answer}), key="copyai")
        st.markdown(
            f"""<div class="glass-wrap translations"><div>
            <span class="language-caption">{add_emojis("{language_emoji}")} {translator_supported.get(code, code.upper())}</span><br>
            <span style="font-size:1.02em;line-height:1.56;">{translation}</span></div></div>""",
            unsafe_allow_html=True
        )
        st.button("📋 Copy Translation", on_click=lambda: st.session_state.update({'translation': translation}), key="copytrans")
        cols = st.columns([2, 1])
        with cols[0]:
            if can_voice:
                st.markdown('<div class="voice-glow">🔊 Voice Output (Click Play Below):</div>', unsafe_allow_html=True)
                audio = synthesize_speech(translation, code)
                if audio:
                    st.audio(audio, format='audio/mp3')
                else:
                    st.info("Sorry, there was a problem generating voice for this text/language.")
            else:
                st.info("Sorry, voice not available for this language (Google TTS doesn't support it).")
        with cols[1]:
            if img_url:
                st.image(img_url, caption="Related image", use_container_width=True)
            else:
                st.info("No related image found for your query.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="caption">Made with {add_emojis("{creator_emoji}")} by Raghavendra N . Bright Minds Academy <span>Contact: <a style="color:#ffe28c" href="mailto:info@brightmindsacademy.com">info@brightmindsacademy.com</a></span></div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
