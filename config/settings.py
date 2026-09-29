"""Configuration module for TigerGraph Agentic GraphRAG System."""
from pathlib import Path
import os
from dotenv import load_dotenv

# Project Root Directory: F:\TigerGraph_Hackathon
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file
ENV_FILE = PROJECT_ROOT / '.env'
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    load_dotenv(override=True)

# Data Directories
DATA_DIR = PROJECT_ROOT / 'data'
CORPUS_DIR = DATA_DIR / 'corpus'
QUESTIONS_DIR = DATA_DIR / 'questions'
GRAPH_DIR = DATA_DIR / 'graph'

CORPUS_FILE = CORPUS_DIR / 'corpus.jsonl'
EVAL_PUBLIC_FILE = QUESTIONS_DIR / 'eval_public.jsonl'
EVAL_HIDDEN_FILE = QUESTIONS_DIR / 'eval_hidden.jsonl'
GRAPH_INDEX_FILE = GRAPH_DIR / 'olympic_graph.json'
FAISS_INDEX_FILE = DATA_DIR / 'vector_index.faiss'
CHUNKS_FILE = DATA_DIR / 'corpus_chunks.json'
EVAL_RESULTS_FILE = PROJECT_ROOT / 'evaluation_results.json'
SUBMISSION_HIDDEN_FILE = PROJECT_ROOT / 'submission_eval_hidden_output.jsonl'

# TigerGraph Configuration (PRIMARY BACKEND)
TIGERGRAPH_HOST = os.getenv('TIGERGRAPH_HOST', 'http://127.0.0.1:14240').strip()
TIGERGRAPH_USERNAME = os.getenv('TIGERGRAPH_USERNAME', 'tigergraph').strip()
TIGERGRAPH_PASSWORD = os.getenv('TIGERGRAPH_PASSWORD', 'tigergraph').strip()
TIGERGRAPH_GRAPH = os.getenv('TIGERGRAPH_GRAPH', 'OlympicGraph').strip()
TIGERGRAPH_SECRET = os.getenv('TIGERGRAPH_SECRET', '').strip()
TIGERGRAPH_TOKEN = os.getenv('TIGERGRAPH_TOKEN', '').strip()
USE_TIGERGRAPH = os.getenv('USE_TIGERGRAPH', 'true').lower() in ('true', '1', 'yes')

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
EMBEDDING_DIM = 384
TOP_K = int(os.getenv('TOP_K', '5'))

# LLM Provider Configuration (gemini, openai, groq, or offline)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '').strip()
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

# Server Port Configuration
API_PORT = int(os.getenv('API_PORT', '8000'))
API_HOST = os.getenv('API_HOST', '0.0.0.0')