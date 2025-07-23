import streamlit as st
import requests
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import re
import random

# CONFIGURATION
GROQ_API_KEY = ""
GROQ_MODEL = "llama3-70b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
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
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=JetBrains+Mono:wght@500&display=swap');
    body {{
      background: url('{BG_IMAGE_URL}') no-repeat center center fixed !important;
      background-size: cover !important; min-height:100vh; font-family:'Montserrat',sans-serif;
    }}
    .stApp {{
      background: rgba(18,20,41,0.86); min-height:100vh; color:#f4f4f7; box-shadow: 0 0 80px 28px #0e123083 inset; padding-bottom:3vw;
    }}
    .title {{
      font-family:'Montserrat'; font-size:2.4em; color:#fff; text-align:center; font-weight:900; margin:12px 0 8px 0; letter-spacing:.8px;
      background:linear-gradient(93deg,#00c3ff 14%,#ff9800 88%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
      text-shadow:0 3px 30px #191b3a60;
    }}
    .description {{
      font-size:1.07em; color:#f8f8ff; text-align:center; margin-bottom:16px; opacity:.97;
      font-family:'Montserrat'; font-weight:600;
    }}
    .ai-tips {{
      background:rgba(255,255,255,0.09);
      color:#ffe47a; border-radius:25px; padding:12px 22px 13px 24px; font-size:1.07em;
      font-family:'Montserrat'; font-weight:700; text-align:center; max-width:550px;margin:10px auto 18px auto;
      border:1.2px solid #00c2ef23;
      text-shadow:0 1px 8px #1c418f14;
    }}
    .glass-wrap {{
      background: rgba(41,51,92,0.88); border-radius:22px; box-shadow: 0 3px 24px 7px #00c3ff14;
      margin:21px auto 10px auto; max-width:930px;
      padding: 20px 30px 15px 24px; border:1.65px solid #ffb86c22; backdrop-filter: blur(8px) saturate(127%);
    }}
    .generated-info, .translations {{
      font-size:1.15em; font-family:'Montserrat',sans-serif;
      color:#f4f1fd; background:rgba(23,30,52,0.97); border-radius:13px;
      border: 1.2px solid #00c3ff2a; box-shadow:0 2px 9px 0 #2c536452;
      margin-bottom:10px; padding:16px 20px 12px 15px; word-break:break-word; line-height:1.6;
      overflow-wrap:break-word; max-height:none;
    }}
    .copy-btn {{
      background:linear-gradient(96deg,#00c3ff 50%,#ff9800 100%);
      color:#fff; border:none; padding: 6px 15px; border-radius: 16px;
      font-family:'Montserrat'; font-size:1em; font-weight:700;
      cursor:pointer; margin-left:10px; margin-bottom:3px;
      transition: background .18s, transform .10s;
      box-shadow:0 1px 5px #00c3ff17;
    }}
    .copy-btn:active {{
      background:linear-gradient(96deg,#ff9800 10%,#00c3ff 90%);
      transform:scale(.98);
    }}
    .language-caption {{
      color:#ff9800; font-weight:700; font-size:1.10em; margin-bottom:6px; letter-spacing:0.018em;
    }}
    .voice-glow {{
      background:linear-gradient(90deg,#fff7,#ffd58cfa); border-radius:27px;
      box-shadow:0 0 19px 8px #ffd58c22,0 0 21px 11px #ff980014;
      padding:10px 15px 9px 15px; margin:8px 0 0 0; text-align:center;
      font-weight:700; font-size:1.07em; color:#191a1d;
    }}
    .caption {{
      color:#ffe18c; text-align:center; background:linear-gradient(99deg,#00c3ff39,#ffb06d31 60%,#ff98003b 100%);
      border-radius:13px; font-size:1.05em; margin:22px 0 10px 0; padding:8px 0 11px 0;
      font-family:'Montserrat'; font-weight:700; letter-spacing:.021em;
      text-shadow:0 2.3px 13px #00c3ff24; box-shadow:0 2px 13px #ff980018;
    }}
    .stButton>button {{
      background:linear-gradient(87deg,#00c3ff 37%,#ff9800 99%);
      color:#fff; border:none; padding:12px 27px; border-radius:17px;
      font-size:1.13em; font-family:'Montserrat'; font-weight:700;
      margin-bottom:13px;margin-top:11px; cursor:pointer;
      box-shadow:0 0 13px 2px #00c3ff1e;
      transition:transform 0.12s,box-shadow 0.13s,background 0.18s;
    }}
    .stButton>button:hover {{
      background:linear-gradient(87deg,#ff9800 12%,#00c3ff 100%)!important;
      color:#27292d; transform:scale(1.045);
      box-shadow:0 0 25px 6px #ff98003e,0 0 5px 1px #00c3ff27;
    }}
    .stSelectbox>div>div, .stTextInput>div>div>input{{
      background:rgba(30,34,55,0.68)!important; color:#fff !important;
      border-radius:10px; font-family:'JetBrains Mono',monospace;
      font-size:1.04em; font-weight:500; padding-left:11px;
    }}
    .stAudio audio {{ width:96% !important; margin:9px 0 7px 0; border-radius:6px; }}
    .stImage img {{
      border-radius:16px; box-shadow:0 2px 13px 0 #ff980041,0 0 13px 4px #00c3ff13;
      margin-top:6px; margin-bottom:0.38em; border:1.5px solid #00c3ff3b;
      background:#fff; object-fit:cover; filter:saturate(1.06) brightness(1.02);
    }}
    .stInfo {{
      background:rgba(255,255,255,0.16)!important; border-radius:7px; font-size:.98em;
      color:#faf6ea; margin-bottom: 7px; padding:6px 15px; font-family:'Montserrat',monospace;
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
    match = re.search(r"\(([^)]+)\)", lang_display)
    if match:
        return match.group(1).strip().lower()
    return "en"

def is_voice_supported(code):
    return code in tts_supported

def llama70b(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(GROQ_URL, json=data, headers=headers, timeout=90)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            try: err = r.json()
            except Exception: err = r.text
            return f"Error: {err}"
    except Exception as e:
        return f"Exception: {e}"

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
        print(f"Voice error ({code}): {e}")
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
        print(f"Pexels error: {e}")
    return None

def fetch_unsplash_image(query):
    if not UNSPLASH_KEY:
        return None
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
    try:
        resp = requests.get(url, timeout=20)
        data = resp.json()
        image_url = data.get('urls', {}).get('regular')
        return image_url
    except Exception as e:
        print(f"Unsplash error: {e}")
    return None

def fetch_best_image(query):
    pexels_img = fetch_pexels_image(query)
    if pexels_img:
        return pexels_img
    unsplash_img = fetch_unsplash_image(query)
    return unsplash_img

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
        # --- Rich output (never scrolls, always fully visible) ---
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
