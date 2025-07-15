# Reddit User Persona Analyzer

[![GitHub Repo](https://img.shields.io/badge/GitHub-BeyondChats-blue?logo=github)](https://github.com/CroWzblooD/BeyondChats.git)

> **Assignment for BeyondChats AI/LLM Engineer Intern**

---

## 🌟 Quick Start (For Everyone)

**GitHub Repo:** [https://github.com/CroWzblooD/BeyondChats.git](https://github.com/CroWzblooD/BeyondChats.git)

**No experience needed! Just follow these steps:**

---

## 1. Clone the Project
```bash
git clone https://github.com/CroWzblooD/BeyondChats.git
cd BeyondChats
```

---

## 2. Install Python Requirements
```bash
pip install -r requirements.txt
```

---

## 3. Set Up Your .env File

- Copy the template:
  ```bash
  cp .env.example .env
  ```
- Open `.env` in any text editor and fill in your API keys:

### Example .env file
```env
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- **Where do I get these?**
  - [How to get Reddit API keys?](https://www.reddit.com/prefs/apps)
  - [How to get Gemini API key?](https://aistudio.google.com/app/apikey)

---

## 4. Run the Analyzer!
```bash
python reddit_persona_analyzer.py
```

- When asked, paste a Reddit user profile URL (like `https://www.reddit.com/user/kojied/`)
- Wait a minute for the magic to happen!
- Find your results in `data/sample_outputs/` (both text and PDF persona files)

---

## 5. Example Output
- `kojied_persona.txt` (text persona with citations)
- `kojied_persona_<timestamp>.pdf` (single-page PDF persona)

---

## 📁 Project Structure
```
BeyondChats/
├── README.md
├── requirements.txt
├── .env.example
├── reddit_persona_analyzer.py
├── src/
│   ├── reddit_scraper.py
│   ├── persona_analyzer.py
│   ├── output_generator.py
│   ├── pdf_persona_generator.py
│   └── utils.py
├── data/
│   └── sample_outputs/
└── tests/
```

---

## 📝 .env Template (Copy & Fill)
```env
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- Get your Reddit keys from: https://www.reddit.com/prefs/apps
- Get your Gemini key from: https://aistudio.google.com/app/apikey

---

## 🧑‍💻 Troubleshooting (If you get stuck)
- **Missing API Keys:** Double-check your `.env` file
- **Reddit API Errors:** Make sure your Reddit app is type "Script"
- **Gemini API Errors:** Check your Gemini API key and quota
- **User Not Found:** The Reddit user may not exist or is private
- **Still stuck?** Delete your `.env` and try again from the template!

---

## 🤝 Contributing
- Follows PEP-8 guidelines
- PRs and suggestions welcome (for assignment review only)

---

## 📜 License
This project is for the BeyondChats AI/LLM Engineer Intern assignment. Code is your property and will not be used unless you are selected for the paid internship.

---

## 📬 Contact
If you have any queries, please message via Internshala as per the assignment instructions. 