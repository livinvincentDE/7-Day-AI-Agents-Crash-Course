# 🤖 AI FAQ Assistant

> **Stop searching. Start asking.**
> An intelligent chatbot that reads DataTalksClub FAQs so you don't have to.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Chat%20UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLM%20Powered-F55036?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

---

## 🧩 What Is This?

Students in DataTalksClub courses constantly ask the same questions — buried across hundreds of FAQ files, Slack threads, and markdown docs. Finding answers takes forever.

**This project fixes that.**

You ask a question in plain English. The assistant finds the most relevant FAQ content, sends it to an AI, and returns a clear, grounded answer — all in seconds.

---

## ✨ Features at a Glance

| Feature | Description |
|---|---|
| 🔍 **Hybrid Search** | Combines keyword + semantic (vector) search for best results |
| 🧠 **RAG Architecture** | Answers are grounded in real FAQ data, not hallucinated |
| ⚡ **Groq LLM (Llama 3.3)** | Fast, high-quality language model responses |
| 💬 **Chat UI** | Clean Streamlit interface — just type and go |
| 📋 **Logging** | Every conversation is saved for review |
| 📊 **Auto Evaluation** | LLM-as-a-judge scores relevance, clarity, and hallucination |

---

## 🏗️ How It Works

Here's the journey of your question, from input to answer:

```
You type a question
        │
        ▼
┌─────────────────────┐
│   Hybrid Search     │  ← Finds the most relevant FAQ chunks
│  (Text + Vector)    │    using both keyword and semantic search
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Context Builder   │  ← Assembles the top results into a prompt
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Groq LLM Agent   │  ← Generates a clear, grounded answer
│  (Pydantic AI)      │    (no making things up!)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Streamlit Chat    │  ← You see the answer + it's logged
└─────────────────────┘
```

> **Why Hybrid Search?** Pure keyword search misses meaning. Pure vector search misses exact terms. Hybrid search gets the best of both — better results, fewer misses.

---

## 📁 Project Structure

```
📦 ai-faq-assistant/
│
├── 📄 app.py                  ← Main Streamlit app (start here)
├── 📄 search.py               ← Text, vector & hybrid search logic
├── 📄 agent.py                ← Pydantic AI agent (Groq LLM)
├── 📄 data_generation.py      ← Generates test questions
├── 📄 generate_questions.py   ← Runs evaluation on generated Q&A
├── 📄 requirements.txt        ← All Python dependencies
├── 📄 .env                    ← Your API keys (never commit this!)
└── 📁 logs/                   ← Saved conversation logs
```

---

## 🚀 Getting Started

Follow these steps in order. They should take about **5 minutes** on any machine.

### Step 1 — Get the Code

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### Step 2 — Create a Virtual Environment

A virtual environment keeps this project's dependencies isolated from your system Python.

```bash
# Create it
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

> ✅ You'll know it worked when you see `(venv)` at the start of your terminal prompt.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs everything the project needs (Streamlit, Groq SDK, sentence-transformers, etc.).

### Step 4 — Add Your API Key

Create a file called `.env` in the project root:

```bash
# Create the file (Mac/Linux)
touch .env

# Or just open any text editor and save a file named ".env"
```

Add this line inside it:

```
GROQ_API_KEY=your_api_key_here
```

> 🔑 **Get a free Groq API key at:** https://console.groq.com
>
> ⚠️ **Never share or commit your `.env` file.** It's already in `.gitignore` if you cloned this repo.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

A browser tab will open automatically at `http://localhost:8501`.
Type any DataTalksClub course question — the assistant handles the rest.

---

## 🧪 Testing & Evaluation

Want to measure how well the assistant performs? Run these two commands:

```bash
# 1. Generate a set of test questions from the FAQ data
python data_generation.py

# 2. Run the LLM-based evaluation on those questions
python generate_questions.py
```

The evaluation checks every answer for:
- **Relevance** — Did it actually answer the question?
- **Clarity** — Is the answer easy to understand?
- **Hallucination** — Did it make anything up?

Logs are saved to the `/logs/` folder for review.

### Search Quality Metrics

The search layer is also benchmarked using:
- **Hit Rate** — Was the right document in the top results?
- **MRR (Mean Reciprocal Rank)** — How highly was the correct result ranked?

---

## ☁️ Deploy to Hugging Face Spaces (Free Hosting)

You can host this app publicly in minutes:

1. Push your repo to [Hugging Face Spaces](https://huggingface.co/spaces)
2. In your Space settings, go to **Secrets** and add:
   ```
   Name:  GROQ_API_KEY
   Value: your_api_key_here
   ```
3. Set the **SDK** to `Streamlit` and the **entry file** to `app.py`
4. Your app will build and go live automatically 🎉

---

## 🔮 What's Next

Planned improvements for future versions:

- [ ] Show source citations with links in the chat UI
- [ ] Add multi-document context ranking
- [ ] Build a visual evaluation scoring dashboard
- [ ] Add user feedback buttons (👍 / 👎)
- [ ] Add conversation memory (follow-up questions)

---

## 🤝 Contributing

Found a bug? Have an idea? Contributions are welcome.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Make your changes and commit
4. Open a pull request — describe what you changed and why

---

## 👨‍💻 Author

Built by **Livin Vincent**

If this project helped you, consider ⭐ starring the repo — it helps others find it too.

---

*Built with 🧠 Pydantic AI · ⚡ Groq · 🔍 Hybrid Search · 💬 Streamlit*