# 📚 GSPP User Guides Search

A Streamlit-powered search application that uses Google's Gemini AI to answer questions about GSPP (Job Planning Application and Sweet Editor) user guides. The app leverages Gemini's File Search capability to provide accurate, documentation-based answers with citations.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)

## ✨ Features

- **🔍 AI-Powered Search** – Ask natural language questions about GSPP software
- **📄 Citation Support** – Get answers with direct citations from the documentation
- **💬 Chat Interface** – Intuitive conversational UI with chat history
- **📖 Documentation-Only Mode** – Answers strictly from the indexed user guides
- **🔧 Debug Mode** – Optional raw metadata view for troubleshooting

## 📋 Prerequisites

- **Python 3.9+**
- **Google Gemini API Key** – Get one from [Google AI Studio](https://aistudio.google.com/apikey)

## 🚀 Quick Start

### 1. Clone or Download the Repository

```bash
cd "OS user guides"
```

### 2. Install Dependencies

```bash
pip install google-genai python-dotenv streamlit
```

### 3. Configure Environment

Create a `.env` file in the project root (or copy from `.env.example`):

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your-api-key-here
```

### 4. Run Setup (First Time Only)

This creates a File Search store in Gemini and uploads the PDF user guides:

```bash
python setup.py
```

The setup will:
- ✅ Verify PDF files exist
- ✅ Create a File Search store named "GSPP-User-Guides"
- ✅ Upload and index both user guide PDFs
- ✅ Save configuration to `file_search_config.json`

### 5. Launch the Application

```bash
python -m streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
OS user guides/
├── app.py                      # Main Streamlit application
├── setup.py                    # Initial setup script
├── file_search_guides.py       # File search utilities
├── file_search_config.json     # Generated config (after setup)
├── .env                        # Your API key (gitignored)
├── .env.example                # Example environment file
├── README.md                   # This file
└── user guides/
    ├── GSPP Job Planning Application User Guide.pdf
    └── GSPP Sweet Editor User Guide.pdf
```

## 🎮 Usage

### Asking Questions

Simply type your question in the chat input at the bottom of the page. Examples:

- "How do I create a new job?"
- "What are the keyboard shortcuts?"
- "How do I export data?"
- "What file formats are supported?"

### Sidebar Features

- **📖 Indexed Documents** – Shows which PDFs are currently indexed
- **⚙️ Settings** – Displays current model and mode
- **💡 Example Questions** – Click to quickly ask common questions
- **🔧 Debug Mode** – Toggle to view raw API metadata

### Citations

Each answer includes expandable citations showing:
- The source document title
- The relevant text excerpt from the documentation

## ⚙️ Configuration

### Model

The app uses `gemini-3-flash-preview` by default. To change this, edit the `MODEL` constant in `app.py`:

```python
MODEL = "gemini-3-flash-preview"
```

### System Instructions

The AI is configured to only answer from the documentation. The system prompt can be customized in `app.py` via the `SYSTEM_INSTRUCTION` variable.

## 🔧 Troubleshooting

### "Setup Required" Error

If you see this error, run the setup script first:

```bash
python setup.py
```

### "GEMINI_API_KEY" Error

Ensure your `.env` file exists and contains a valid API key:

```env
GEMINI_API_KEY=your-actual-api-key
```

### PDF Files Not Found

Ensure the PDF files are in the `user guides/` subdirectory:
- `user guides/GSPP Job Planning Application User Guide.pdf`
- `user guides/GSPP Sweet Editor User Guide.pdf`

### Re-indexing Documents

If you need to re-upload the documents, delete `file_search_config.json` and run `setup.py` again:

```bash
del file_search_config.json
python setup.py
```

## 📝 License

This project is for internal use with GSPP documentation.

## 🤝 Contributing

For issues or feature requests, please contact the development team.
