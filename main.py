"""
app.py — Streamlit UI
Run with: streamlit run app.py
Imports only from search_agent.py and logs.py — NOT from main.py.
"""

import asyncio
import os

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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
:root {
    --bg-primary:#0e0e10;--bg-secondary:#18181b;--bg-card:#1c1c1f;
    --bg-input:#27272a;--accent-orange:#f97316;--accent-amber:#fbbf24;
    --text-primary:#f4f4f5;--text-muted:#71717a;--border:#3f3f46;--radius:12px;
}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg-primary)!important;font-family:'IBM Plex Sans',sans-serif;color:var(--text-primary);}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stMain"]>div{max-width:760px;margin:0 auto;padding:2rem 1rem 6rem;}
h1{font-family:'IBM Plex Sans',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;color:var(--text-primary)!important;letter-spacing:-0.02em;}
[data-testid="stCaptionContainer"] p{color:var(--text-muted)!important;font-size:0.875rem!important;}
[data-testid="stChatMessage"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:1rem 1.25rem!important;margin-bottom:0.75rem!important;}
[data-testid="chatAvatarIcon-assistant"]{background-color:var(--accent-amber)!important;}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li{color:var(--text-primary)!important;font-size:0.95rem!important;line-height:1.65!important;}
[data-testid="stChatMessage"] pre{background:var(--bg-input)!important;border:1px solid var(--border)!important;border-radius:8px!important;padding:.75rem 1rem!important;font-family:'JetBrains Mono',monospace!important;font-size:.82rem!important;}
[data-testid="stChatMessage"] code{background:var(--bg-input)!important;border-radius:4px!important;padding:.1em .35em!important;font-family:'JetBrains Mono',monospace!important;font-size:.85em!important;color:var(--accent-amber)!important;}
[data-testid="stChatInput"]{position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;width:min(760px,96vw)!important;background:var(--bg-secondary)!important;border-top:1px solid var(--border)!important;padding:.75rem 1rem!important;z-index:999!important;}
[data-testid="stChatInput"] textarea{background:var(--bg-input)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text-primary)!important;font-family:'IBM Plex Sans',sans-serif!important;font-size:.95rem!important;caret-color:var(--accent-orange)!important;}
[data-testid="stChatInput"] textarea:focus{border-color:var(--accent-orange)!important;box-shadow:0 0 0 2px rgba(249,115,22,.2)!important;}
[data-testid="stChatInput"] textarea::placeholder{color:var(--text-muted)!important;}
[data-testid="stChatInputSubmitButton"]{background:var(--accent-orange)!important;border-radius:6px!important;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg-primary);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_agent():
    import search_agent
    return search_agent.init_agent()


agent = init_agent()

st.title("🤖 AI FAQ Assistant")
st.caption("Ask me anything about the DataTalksClub/faq repository")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching docs and thinking..."):
            import search_agent as sa
            context = sa.build_context(prompt, search_mode="hybrid")
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
            try:
                result = asyncio.run(agent.run(full_prompt))
                answer = result.output
            except Exception as exc:
                answer = f"❌ Error: {exc}"
                result = None
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    if result:
        try:
            import logs
            log_path = logs.log_interaction_to_file(agent, result.all_messages(), source="user")
            if log_path:
                st.toast(f"📝 Logged → {log_path.name}", icon="✅")
        except Exception:
            pass
