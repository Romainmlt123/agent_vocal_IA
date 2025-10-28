# 🎓 Agent Vocal IA - Offline Voice Tutor

An intelligent offline voice tutoring system for Google Colab GPU, featuring a complete ASR → RAG → LLM → TTS pipeline.

## 📋 Overview

**Agent Vocal IA** is an offline voice tutor designed for mathematics, physics, and English education. It runs entirely on GPU (or CPU) without internet connectivity, making it perfect for secure or offline learning environments.

### Key Features

- 🎤 **ASR (Automatic Speech Recognition)**: faster-whisper + silero-vad for accurate speech-to-text
- 📚 **RAG (Retrieval Augmented Generation)**: FAISS + SentenceTransformers for context-aware responses
- 🧠 **Local LLM**: llama-cpp-python for privacy-preserving language generation
- 🔊 **TTS (Text-to-Speech)**: piper-tts for natural voice synthesis
- 🚀 **GPU Optimized**: Designed for Google Colab with CUDA support
- 🔒 **Fully Offline**: No internet required after setup

## 🏗️ Project Structure

```
agent_vocal_IA/
├── src/                      # Core source code
│   ├── __init__.py
│   ├── asr.py               # Speech recognition module
│   ├── rag.py               # Document retrieval module
│   ├── llm.py               # Language model module
│   ├── tts.py               # Text-to-speech module
│   └── pipeline.py          # Complete pipeline orchestration
├── data/                     # Course materials
│   ├── maths/               # Mathematics content
│   ├── physique/            # Physics content
│   └── anglais/             # English content
├── models/                   # Model storage
│   ├── llm/                 # Language model files (GGUF)
│   └── voices/              # TTS voice models (ONNX)
├── ui/                       # User interface
│   ├── __init__.py
│   └── gradio_interface.py  # Gradio web interface
├── demo_cli.py              # Command-line demo
├── 00_env_sanity.ipynb      # Environment check notebook
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Romainmlt123/agent_vocal_IA.git
cd agent_vocal_IA
```

### 2. Install Dependencies

For Google Colab:
```python
!pip install -r requirements.txt
```

For local environment:
```bash
pip install -r requirements.txt
```

### 3. Download Models

#### LLM Model (Required)
Download a GGUF model and place it in `models/llm/`:

```bash
# Example: Mistral 7B Instruct (recommended for French)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/llm/model.gguf
```

See `models/llm/README.md` for more options.

#### TTS Voice Models (Optional but recommended)
Download Piper voices:

```bash
# French voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-fr-fr-siwis-medium.tar.gz
tar -xzf voice-fr-fr-siwis-medium.tar.gz -C models/voices/

# English voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz -C models/voices/
```

See `models/voices/README.md` for more options.

### 4. Add Course Materials

Add your course materials as `.txt` files to:
- `data/maths/` - Mathematics content
- `data/physique/` - Physics content
- `data/anglais/` - English content

### 5. Index Documents

```bash
python demo_cli.py --index
```

### 6. Run the Tutor

#### Command Line Interface
```bash
# Text mode (interactive)
python demo_cli.py --mode text

# Audio mode (with file)
python demo_cli.py --mode audio --audio path/to/audio.wav
```

#### Web Interface (Gradio)
```python
from ui.gradio_interface import launch_interface
launch_interface()
```

#### Python API
```python
from src.pipeline import create_pipeline

# Initialize pipeline
pipeline = create_pipeline({
    "llm_model_path": "models/llm/model.gguf",
    "whisper_model_size": "base",
    "device": "cuda"
})

# Index documents
pipeline.index_documents()

# Ask a question
result = pipeline.process_text_query(
    question="Qu'est-ce que la gravité?",
    use_rag=True
)
print(result['response'])
```

## 📓 Google Colab Usage

### Environment Setup

```python
# 1. Check environment
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA
!pip install -r requirements.txt

# 2. Run sanity check
# Open 00_env_sanity.ipynb and run all cells

# 3. Download models (see Quick Start section)
```

### Basic Usage

```python
from src.pipeline import create_pipeline

# Initialize with GPU
pipeline = create_pipeline({
    "llm_model_path": "models/llm/model.gguf",
    "device": "cuda"
})

# Add your documents and index
pipeline.index_documents()

# Start chatting!
response = pipeline.process_text_query(
    "Explique-moi le théorème de Pythagore",
    use_rag=True
)
print(response['response'])
```

## 🛠️ Configuration

### Pipeline Configuration

```python
config = {
    "llm_model_path": "models/llm/model.gguf",  # Path to GGUF model
    "data_dirs": [                               # Directories to index
        "data/maths",
        "data/physique",
        "data/anglais"
    ],
    "whisper_model_size": "base",                # tiny, base, small, medium, large
    "device": "cuda",                            # cuda or cpu
    "voices_dir": "models/voices"                # TTS voices directory
}
```

### CLI Options

```bash
python demo_cli.py \
  --mode text \                    # text or audio mode
  --model models/llm/model.gguf \  # LLM model path
  --whisper-size base \            # Whisper model size
  --device cuda \                  # Device (cuda/cpu)
  --index                          # Index documents before running
```

## 📦 Components

### ASR (Automatic Speech Recognition)
- **faster-whisper**: Optimized Whisper implementation
- **silero-vad**: Voice activity detection
- Supports multiple languages (French, English, etc.)

### RAG (Retrieval Augmented Generation)
- **FAISS**: Efficient similarity search
- **SentenceTransformers**: Multilingual embeddings
- Indexes course materials for context-aware responses

### LLM (Language Model)
- **llama-cpp-python**: Efficient CPU/GPU inference
- GGUF format support
- Context-aware tutoring with conversation history

### TTS (Text-to-Speech)
- **piper-tts**: High-quality neural TTS
- Multiple voices and languages
- ONNX format for efficient inference

## 🎯 Use Cases

1. **Offline Learning**: Use in environments without internet
2. **Privacy-Focused**: All processing happens locally
3. **Multilingual Tutoring**: Support for French, English, and more
4. **Voice Interaction**: Natural speech-based Q&A
5. **Course Integration**: RAG retrieves from your course materials

## 🔧 Development

### Adding New Modules

1. Create module in `src/`
2. Import in `src/__init__.py`
3. Integrate into `src/pipeline.py`

### Testing

```bash
# Run environment checks
jupyter notebook 00_env_sanity.ipynb

# Test individual components
python -c "from src.asr import SpeechRecognizer; print('ASR OK')"
python -c "from src.rag import RAGRetriever; print('RAG OK')"
python -c "from src.llm import LocalLLM; print('LLM OK')"
python -c "from src.tts import TextToSpeech; print('TTS OK')"
```

## 📝 Requirements

- Python 3.10+
- CUDA-capable GPU (recommended, 8GB+ VRAM)
- 10GB+ disk space for models
- See `requirements.txt` for full dependencies

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source. Please check individual model licenses:
- faster-whisper: MIT License
- FAISS: MIT License
- llama-cpp-python: MIT License
- piper-tts: MIT License

## 🙏 Acknowledgments

- OpenAI Whisper team
- Facebook AI Research (FAISS)
- SentenceTransformers team
- llama.cpp contributors
- Piper TTS project

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Made with ❤️ for offline education**