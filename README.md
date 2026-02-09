# 📚 PDF Guide Search

A Streamlit-powered search application that uses Google's Gemini AI to answer questions from your PDF documents. The app leverages Gemini's File Search capability to provide accurate, documentation-based answers with citations.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)

## ✨ Features

- **🔍 AI-Powered Search** – Ask natural language questions about your documents
- **📄 Citation Support** – Get answers with direct citations from your PDFs
- **💬 Chat Interface** – Intuitive conversational UI with chat history
- **📖 Documentation-Only Mode** – Answers strictly from indexed documents
- **🔐 Access Control** – Optional Store ID prompt for secure deployments
- **🔧 Debug Mode** – View raw API metadata for troubleshooting

## 📋 Prerequisites

- **Python 3.9+**
- **Google Gemini API Key** – Get one from [Google AI Studio](https://aistudio.google.com/apikey)
- **PDF Documents** – Place your PDFs in the `user guides/` folder

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install google-genai python-dotenv streamlit
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-api-key-here
```

### 3. Add Your PDFs

Place your PDF documents in the `user guides/` folder, then update `setup.py` with your file names:

```python
PDF_FILES = [
    ("user guides/Your Document 1.pdf", "Display Name 1"),
    ("user guides/Your Document 2.pdf", "Display Name 2"),
]
```

### 4. Run Setup (First Time Only)

This creates a File Search store in Gemini and uploads your PDFs:

```bash
python setup.py
```

### 5. Launch the Application

```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📁 Project Structure

```
├── app.py                      # Main Streamlit application
├── setup.py                    # Initial setup script
├── requirements.txt            # Python dependencies
├── file_search_config.json     # Generated config (after setup)
├── .env                        # Your API key (gitignored)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── user guides/                # Your PDF documents
```

## ☁️ Deploying to Streamlit Cloud

### 1. Push to GitHub

Your `.gitignore` already excludes sensitive files. Push your code:

```bash
git add .
git commit -m "Ready for deployment"
git push
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub and select your repo
3. Set `app.py` as the main file

### 3. Configure Secrets

In **Advanced settings** → **Secrets**, add:

```toml
GEMINI_API_KEY = "your-api-key"
```

If you want users to enter the Store ID themselves (for access control):
- Leave `STORE_NAME` out of secrets
- Share the Store ID only with authorized users

Or pre-configure access:

```toml
GEMINI_API_KEY = "your-api-key"
STORE_NAME = "fileSearchStores/your-store-id"
```

## ⚙️ Customization

### Change the Model

Edit the `MODEL` constant in `app.py`:

```python
MODEL = "gemini-3-flash-preview"
```

### Customize System Instructions

Modify `SYSTEM_INSTRUCTION` in `app.py` to change how the AI responds.

### Update Branding

Edit the header text and styling in `app.py` to match your organization.

## 🔧 Troubleshooting

### "Access Required" Prompt

If you see this, either:
- Enter your Store ID (from `file_search_config.json`)
- Add `STORE_NAME` to Streamlit secrets

### API Key Error

Ensure your `.env` file contains a valid key:

```env
GEMINI_API_KEY=your-actual-api-key
```

### Re-indexing Documents

Delete `file_search_config.json` and run `setup.py` again:

```bash
del file_search_config.json   # Windows
rm file_search_config.json    # Mac/Linux
python setup.py
```

## 📝 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

Contributions welcome! Please open an issue or pull request.
