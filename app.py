"""
app.py — AI FAQ Assistant
NO streaming. Uses plain asyncio.run() — guaranteed to work on Windows + anyio.
Run with: streamlit run app.py
"""

import asyncio
import os
import nest_asyncio
nest_asyncio.apply()   # must be before any other import

import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)

st.set_page_config(
    page_title="AI FAQ Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --bg:#0a0a0f;--surface:#111118;--card:#16161f;--card-border:#2a2a3d;
    --input-bg:#1e1e2e;--orange:#ff6b2b;--orange-glow:rgba(255,107,43,0.18);
    --amber:#f59e0b;--purple:#a78bfa;--teal:#2dd4bf;
    --text:#f0f0ff;--muted:#8b8ba8;--radius:14px;
}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;font-family:'Space Grotesk',sans-serif!important;color:var(--text)!important;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"]{display:none!important;}
[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMain"]>div{max-width:780px;margin:0 auto;padding:2.5rem 1.5rem 7rem;}
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--card-border)!important;border-radius:var(--radius)!important;padding:1.1rem 1.4rem!important;margin-bottom:0.85rem!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){border-left:3px solid var(--orange)!important;background:linear-gradient(135deg,#1a1218 0%,var(--card) 100%)!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]){border-left:3px solid var(--purple)!important;background:linear-gradient(135deg,#13111f 0%,var(--card) 100%)!important;}
[data-testid="chatAvatarIcon-user"]{background:linear-gradient(135deg,var(--orange),var(--amber))!important;border-radius:10px!important;}
[data-testid="chatAvatarIcon-assistant"]{background:linear-gradient(135deg,var(--purple),var(--teal))!important;border-radius:10px!important;}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li{color:var(--text)!important;font-size:0.96rem!important;line-height:1.72!important;font-family:'Space Grotesk',sans-serif!important;}
[data-testid="stChatMessage"] strong{color:var(--amber)!important;font-weight:600!important;}
[data-testid="stChatMessage"] a{color:var(--teal)!important;text-decoration:underline!important;text-underline-offset:3px!important;}
[data-testid="stChatMessage"] pre{background:#0d0d18!important;border:1px solid #2a2a3d!important;border-radius:10px!important;padding:1rem 1.2rem!important;font-family:'JetBrains Mono',monospace!important;font-size:0.83rem!important;}
[data-testid="stChatMessage"] code{background:#1e1e2e!important;border-radius:5px!important;padding:0.15em 0.45em!important;font-family:'JetBrains Mono',monospace!important;font-size:0.84em!important;color:var(--teal)!important;}
[data-testid="stChatInput"]{position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;width:min(780px,96vw)!important;background:var(--surface)!important;border-top:1px solid var(--card-border)!important;padding:1rem 1.25rem!important;z-index:999!important;}
[data-testid="stChatInput"] textarea{background:var(--input-bg)!important;border:1.5px solid var(--card-border)!important;border-radius:10px!important;color:var(--text)!important;font-family:'Space Grotesk',sans-serif!important;font-size:0.96rem!important;caret-color:var(--orange)!important;}
[data-testid="stChatInput"] textarea:focus{border-color:var(--orange)!important;box-shadow:0 0 0 3px var(--orange-glow)!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--muted)!important;}
[data-testid="stChatInputSubmitButton"]>button{background:linear-gradient(135deg,var(--orange),var(--amber))!important;border-radius:8px!important;border:none!important;}
[data-testid="stSpinner"] p{color:var(--muted)!important;font-size:0.875rem!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:#2a2a3d;border-radius:3px;}
</style>
""", unsafe_allow_html=True)


# ── Cached resources ───────────────────────────────────────────────────────────
@st.cache_resource
def load_search():
    from search import text_search, vector_search, hybrid_search
    return text_search, vector_search, hybrid_search

@st.cache_resource
def init_agent():
    import search_agent
    return search_agent.init_agent()

with st.spinner("🔄 Loading model (first run only)..."):
    _, _, _ = load_search()
    agent = init_agent()


# ── Simple non-streaming answer (Windows-safe) ─────────────────────────────────
async def get_answer(prompt: str) -> str:
    """Single asyncio.run() call — no streaming, no cancel-scope issues."""
    import search_agent as sa
    context = sa.build_context(prompt, search_mode="hybrid")
    full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
    result = await agent.run(full_prompt)
    # Log quietly
    try:
        import logs
        logs.log_interaction_to_file(agent, result.all_messages(), source="user")
    except Exception:
        pass
    return result.output


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:0.5rem;padding-top:0.5rem">
  <div style="width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#ff6b2b,#f59e0b);display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0;box-shadow:0 0 24px rgba(255,107,43,0.35)">🤖</div>
  <div>
    <h1 style="margin:0;padding:0;font-size:2rem;font-weight:700;background:linear-gradient(135deg,#ff6b2b 0%,#f59e0b 45%,#a78bfa 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.03em;line-height:1.1">AI FAQ Assistant</h1>
    <p style="margin:0;color:#8b8ba8;font-size:0.88rem;font-family:'Space Grotesk',sans-serif;margin-top:2px">Powered by Llama 3.3 · Groq · Hybrid Search</p>
  </div>
</div>
<div style="height:1px;background:linear-gradient(90deg,#ff6b2b22,#a78bfa44,#2dd4bf22);margin-bottom:1.5rem"></div>
""", unsafe_allow_html=True)


# ── Chat state ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("""
    <div style="margin:2rem 0 1rem">
      <p style="color:#8b8ba8;font-size:0.8rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.75rem">Try asking</p>
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
        <span style="background:#1e1e2e;border:1px solid #2a2a3d;border-radius:20px;padding:0.4rem 0.9rem;font-size:0.84rem;color:#c0c0e0">When can I start the course?</span>
        <span style="background:#1e1e2e;border:1px solid #2a2a3d;border-radius:20px;padding:0.4rem 0.9rem;font-size:0.84rem;color:#c0c0e0">Can I join without experience?</span>
        <span style="background:#1e1e2e;border:1px solid #2a2a3d;border-radius:20px;padding:0.4rem 0.9rem;font-size:0.84rem;color:#c0c0e0">How do I get a certificate?</span>
        <span style="background:#1e1e2e;border:1px solid #2a2a3d;border-radius:20px;padding:0.4rem 0.9rem;font-size:0.84rem;color:#c0c0e0">Is the course free?</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Farewell detection ─────────────────────────────────────────────────────────
FAREWELL_WORDS = {
    "bye", "goodbye", "good bye", "see you", "see ya", "quit",
    "exit", "stop", "ciao", "later", "take care", "farewell",
    "thanks bye", "thank you bye", "that's all", "thats all",
    "i'm done", "im done", "done", "close"
}

def is_farewell(text: str) -> bool:
    return text.strip().lower() in FAREWELL_WORDS


# ── Goodbye screen ─────────────────────────────────────────────────────────────
if st.session_state.get("terminated"):
    st.markdown("""
    <div style="
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        min-height:60vh;text-align:center;gap:1.5rem">
      <div style="
        width:80px;height:80px;border-radius:20px;
        background:linear-gradient(135deg,#ff6b2b,#a78bfa);
        display:flex;align-items:center;justify-content:center;
        font-size:40px;box-shadow:0 0 40px rgba(255,107,43,0.3)">👋</div>
      <h2 style="
        font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
        background:linear-gradient(135deg,#ff6b2b,#f59e0b,#a78bfa);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;margin:0">
        Goodbye! See you soon.
      </h2>
      <p style="color:#8b8ba8;font-size:1rem;font-family:'Space Grotesk',sans-serif;margin:0">
        The AI FAQ Assistant has been terminated.<br>
        Refresh the page to start a new session.
      </p>
      <div style="
        background:#16161f;border:1px solid #2a2a3d;border-radius:12px;
        padding:0.75rem 1.5rem;color:#8b8ba8;font-size:0.85rem;
        font-family:'Space Grotesk',sans-serif">
        Session ended · Chat history cleared
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()   # halt all further Streamlit rendering


# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask your question..."):

    # ── Farewell path ──────────────────────────────────────────────────────────
    if is_farewell(prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            st.markdown("👋 **Goodbye!** It was great helping you. See you next time!")

        # Clear history and mark session terminated
        st.session_state.messages = []
        st.session_state.terminated = True
        import time; time.sleep(1.2)   # brief pause so user sees the farewell
        st.rerun()

    # ── Normal question path ───────────────────────────────────────────────────
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching docs and thinking..."):
                try:
                    answer = asyncio.run(get_answer(prompt))
                except Exception as e:
                    answer = f"❌ Error: {e}"
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
