# 🚀 AI Agents - Day 1: GitHub Data Ingestion Pipeline

## 📌 Overview
This project downloads and processes GitHub repository documentation using a modular data pipeline.

## ⚙️ Features
- 📥 Download GitHub repo as ZIP
- 📂 Extract markdown (.md/.mdx) files
- 🧠 Parse frontmatter metadata
- 🧩 Modular pipeline design

## 🏗️ Architecture

Download Repo → Extract Files → Parse Content

## 🧪 Example

```python
data = load_github_repo("DataTalksClub", "faq")
print(len(data))
