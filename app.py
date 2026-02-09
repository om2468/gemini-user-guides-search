"""
GSPP User Guides - Streamlit Search App

Requirements:
    pip install google-genai python-dotenv streamlit

Usage:
    1. First run: python setup.py (to create store and upload PDFs)
    2. Then run: python -m streamlit run app.py
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
CONFIG_FILE = "file_search_config.json"
MODEL = "gemini-3-flash-preview"

# System instruction to restrict to documentation only
SYSTEM_INSTRUCTION = """You are a documentation assistant for GSPP software. 
You MUST ONLY answer questions using information found in the provided user guide documents.

CRITICAL RULES:
1. ONLY use information from the GSPP Job Planning Application User Guide and GSPP Sweet Editor User Guide.
2. If the answer is not found in these documents, say: "I could not find information about this in the GSPP user guides."
3. DO NOT use any external knowledge or make assumptions beyond what is in the documents.
4. When citing information, always mention the specific section or topic name from the document.
5. If you're unsure whether information is in the documents, say so clearly.

Be helpful and precise, but never fabricate information that isn't in the documentation."""


# Page config
st.set_page_config(
    page_title="GSPP User Guides Search",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .citation-box {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .citation-title {
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    .citation-text {
        color: #6b7280;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: 0.5rem;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    """Load configuration from setup, secrets, or user input."""
    # Try local config file first
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    # Fall back to Streamlit secrets (for cloud deployment)
    if hasattr(st, 'secrets') and 'STORE_NAME' in st.secrets:
        return {
            'store_name': st.secrets['STORE_NAME'],
            'store_display_name': 'GSPP-User-Guides',
            'pdf_files': [
                {'display_name': 'GSPP Job Planning User Guide'},
                {'display_name': 'GSPP Sweet Editor User Guide'},
            ]
        }
    
    # Check if user has entered store name in this session
    if 'user_store_name' in st.session_state and st.session_state.user_store_name:
        return {
            'store_name': st.session_state.user_store_name,
            'store_display_name': 'GSPP-User-Guides',
            'pdf_files': [
                {'display_name': 'GSPP Job Planning User Guide'},
                {'display_name': 'GSPP Sweet Editor User Guide'},
            ]
        }
    
    return None


def prompt_for_store_name():
    """Display a prompt for users to enter the store name."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #667eea;">🔐 Access Required</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Please enter the File Search Store ID to access the user guides.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        store_name = st.text_input(
            "Store ID",
            placeholder="fileSearchStores/...",
            help="Contact your administrator for access"
        )
        
        if st.button("🔓 Access Guides", use_container_width=True):
            if store_name and store_name.startswith("fileSearchStores/"):
                st.session_state.user_store_name = store_name
                st.rerun()
            elif store_name:
                st.error("⚠️ Invalid Store ID format. It should start with 'fileSearchStores/'")
            else:
                st.warning("Please enter a Store ID")


@st.cache_resource
def get_client():
    """Initialize the Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ Please set GEMINI_API_KEY in your .env file")
        st.stop()
    return genai.Client(api_key=api_key)


def query_guides(client, store_name, question):
    """Query the user guides."""
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            ]
        )
    )
    return response


def extract_citations(response, show_debug=False):
    """Extract citations with section information."""
    citations = []
    debug_info = {}
    
    if not response.candidates:
        debug_info['error'] = 'No candidates in response'
        return citations, debug_info
    
    candidate = response.candidates[0]
    metadata = getattr(candidate, 'grounding_metadata', None)
    
    if not metadata:
        debug_info['error'] = 'No grounding_metadata in candidate'
        debug_info['candidate_attrs'] = [attr for attr in dir(candidate) if not attr.startswith('_')]
        return citations, debug_info
    
    # Log all metadata attributes for debugging
    debug_info['metadata_attrs'] = [attr for attr in dir(metadata) if not attr.startswith('_')]
    
    # Try different attribute names the API might use
    grounding_chunks = (
        getattr(metadata, 'grounding_chunks', None) or
        getattr(metadata, 'groundingChunks', None) or
        []
    )
    
    grounding_supports = (
        getattr(metadata, 'grounding_supports', None) or
        getattr(metadata, 'groundingSupports', None) or
        []
    )
    
    # Also check for retrieval_metadata (alternative structure)
    retrieval_metadata = getattr(metadata, 'retrieval_metadata', None)
    if retrieval_metadata:
        debug_info['has_retrieval_metadata'] = True
        debug_info['retrieval_metadata_attrs'] = [attr for attr in dir(retrieval_metadata) if not attr.startswith('_')]
    
    debug_info['grounding_chunks_count'] = len(grounding_chunks) if grounding_chunks else 0
    debug_info['grounding_supports_count'] = len(grounding_supports) if grounding_supports else 0
    
    # Build chunk info map
    chunk_info = {}
    for i, chunk in enumerate(grounding_chunks):
        info = {'index': i}
        chunk_attrs = [attr for attr in dir(chunk) if not attr.startswith('_')]
        debug_info[f'chunk_{i}_attrs'] = chunk_attrs
        
        # Try different attribute names for retrieved context
        ctx = (
            getattr(chunk, 'retrieved_context', None) or
            getattr(chunk, 'retrievedContext', None)
        )
        
        if ctx:
            info['title'] = getattr(ctx, 'title', '') or getattr(ctx, 'displayName', 'Unknown Source')
            info['uri'] = getattr(ctx, 'uri', '')
        
        # Get chunk text
        info['text'] = getattr(chunk, 'text', '') or getattr(chunk, 'content', '')
        
        chunk_info[i] = info
    
    # If we have chunks but no supports, just use chunks directly
    if grounding_chunks and not grounding_supports:
        for i, info in chunk_info.items():
            if info.get('text') or info.get('title'):
                citations.append({
                    'title': info.get('title', 'Source Document'),
                    'source_text': info.get('text', ''),
                    'uri': info.get('uri', ''),
                })
    else:
        # Process grounding supports
        for support in grounding_supports:
            chunk_indices = (
                getattr(support, 'grounding_chunk_indices', []) or
                getattr(support, 'groundingChunkIndices', []) or
                []
            )
            
            for idx in chunk_indices:
                if idx in chunk_info:
                    info = chunk_info[idx]
                    citations.append({
                        'title': info.get('title', 'Unknown'),
                        'source_text': info.get('text', ''),
                        'uri': info.get('uri', ''),
                    })
    
    # Deduplicate
    seen = set()
    unique_citations = []
    for c in citations:
        key = (c['title'], c['source_text'][:100] if c['source_text'] else '')
        if key not in seen:
            seen.add(key)
            unique_citations.append(c)
    
    return unique_citations, debug_info


def main():
    # Header
    st.markdown('<h1 class="main-header">📚 GSPP User Guides Search</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about the Job Planning Application and Sweet Editor</p>', unsafe_allow_html=True)
    
    # Load config
    config = load_config()
    if not config:
        prompt_for_store_name()
        st.stop()
    
    # Initialize
    client = get_client()
    store_name = config['store_name']
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📖 Indexed Documents")
        for pdf_info in config['pdf_files']:
            st.markdown(f"✅ {pdf_info['display_name']}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.markdown(f"**Model:** `{MODEL}`")
        st.markdown("**Mode:** Documentation-only")
        
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        examples = [
            "How do I create a new job?",
            "What are the keyboard shortcuts?",
            "How do I export data?",
            "What file formats are supported?",
        ]
        for example in examples:
            if st.button(example, key=example):
                st.session_state.question = example
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    question = st.chat_input("Ask a question about the GSPP user guides...")
    
    if "question" in st.session_state and st.session_state.question:
        question = st.session_state.question
        st.session_state.question = None
    
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching user guides..."):
                try:
                    response = query_guides(client, store_name, question)
                    answer = response.text
                    citations, debug_info = extract_citations(response)
                    
                    st.markdown(answer)
                    
                    # Show raw grounding metadata (expanded by default)
                    if response.candidates:
                        metadata = response.candidates[0].grounding_metadata
                        if metadata:
                            chunks = getattr(metadata, 'grounding_chunks', []) or []
                            supports = getattr(metadata, 'grounding_supports', []) or []
                            with st.expander("🔧 Raw Grounding Metadata", expanded=True):
                                # Build clean output without empty lines
                                output = {
                                    'grounding_chunks': [str(c) for c in chunks] if chunks else [],
                                    'grounding_supports': [str(s) for s in supports] if supports else [],
                                }
                                st.json(output)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
