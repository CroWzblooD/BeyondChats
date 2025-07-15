# Reddit User Persona Analyzer

> **Assignment for BeyondChats AI/LLM Engineer Intern**

---

## 📋 Assignment Overview

**Task:**
- Take a Reddit user’s profile URL as input (e.g., `https://www.reddit.com/user/kojied/`)
- Scrape the user's posts and comments
- Build a comprehensive User Persona based on their Reddit activity
- Output the persona in a text file **with citations** for each characteristic
- (Bonus) Generate a visually rich, single-page PDF persona document

**Technologies Used:**
- Python 3.8+
- [PRAW](https://praw.readthedocs.io/) (Reddit API)
- [Google Gemini LLM](https://aistudio.google.com/app/apikey) (for persona analysis)
- [ReportLab](https://www.reportlab.com/dev/docs/) (for PDF generation)
- dotenv, requests, PIL, and standard Python libraries

---

## 🚀 Features
- **Reddit Scraping:** Fetches all public posts and comments for any Reddit user
- **AI Persona Analysis:** Uses Gemini LLM to analyze user behavior, motivations, and personality
- **Citations:** Each persona trait is linked to specific posts/comments as evidence
- **Text & PDF Output:** Generates both a detailed text file and a beautiful, single-page PDF persona
- **Modern, Professional Layout:** PDF matches industry-standard persona templates

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/CroWzblooD/BeyondChats.git
cd BeyondChats
```

---

## 2. Install Python Requirements
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
- Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- Edit `.env` and add your API keys:
  - `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` (see below)
  - `GEMINI_API_KEY` (see below)

#### Reddit API Credentials
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click **Create App** (type: Script)
3. Set Redirect URI to `http://localhost:8080`
4. Copy your **Client ID** and **Client Secret** into `.env`

#### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new Gemini API key
3. Add it to `.env` as `GEMINI_API_KEY`

---

## ▶️ Usage

### Run the Analyzer
```bash
python reddit_persona_analyzer.py
```

### Follow the Prompts
- Enter a Reddit user profile URL (e.g., `https://www.reddit.com/user/kojied/`)
- The script will:
  1. Fetch posts and comments
  2. Analyze the user with Gemini LLM
  3. Generate persona files (text and PDF)
- Output files are saved in `data/sample_outputs/`

### Example Output
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

## 📝 Sample Outputs
- Example persona files for:
  - `kojied`
  - `Hungry-Move-6603`
- See `data/sample_outputs/` for reference

---

## 🧑‍💻 Troubleshooting
- **Missing API Keys:** Check your `.env` file
- **Reddit API Errors:** Ensure credentials are correct and app type is "Script"
- **Gemini API Errors:** Check your API key and quota
- **User Not Found:** The Reddit user may not exist or have a private/deleted account
- **Rate Limiting:** The script is rate-limited, but Reddit may still impose limits

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