# Quick Start Guide - Agent Vocal IA

This guide will help you get started with Agent Vocal IA in 5 minutes.

## 📋 Prerequisites

- Python 3.10 or higher
- Google Colab with GPU (recommended) or local machine with CUDA
- Internet connection for initial setup (downloading models)

## 🚀 Step-by-Step Setup

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/Romainmlt123/agent_vocal_IA.git
cd agent_vocal_IA

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download LLM Model (Required)

Download a GGUF language model. We recommend Mistral 7B for French:

```bash
# Create models directory if needed
mkdir -p models/llm

# Download Mistral 7B (4.4 GB)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/llm/model.gguf
```

**Alternative smaller model (Phi-2, 1.6 GB):**
```bash
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf \
  -O models/llm/model.gguf
```

### Step 3: Run Environment Check

```bash
# Open the notebook to verify everything is working
jupyter notebook 00_env_sanity.ipynb
```

Or in Colab:
1. Upload `00_env_sanity.ipynb` to Colab
2. Run all cells
3. Check for ✓ marks

### Step 4: Index Your Documents (Optional)

The project comes with example materials. To index them:

```bash
python demo_cli.py --index
```

To add your own materials:
1. Place `.txt` files in `data/maths/`, `data/physique/`, or `data/anglais/`
2. Run the index command above

### Step 5: Start Using!

#### Text Mode (Easiest)
```bash
python demo_cli.py --mode text
```

Type your questions and get answers!

#### Python API
```python
from src.pipeline import create_pipeline

# Initialize
pipeline = create_pipeline({
    "llm_model_path": "models/llm/model.gguf",
    "device": "cuda"  # or "cpu"
})

# Ask a question
result = pipeline.process_text_query(
    question="Qu'est-ce que le théorème de Pythagore?",
    use_rag=True
)

print(result['response'])
```

#### Web Interface (Advanced)
```python
from ui.gradio_interface import launch_interface
launch_interface()
```

## 📊 Google Colab Quick Start

```python
# 1. Clone and setup
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA
!pip install -q -r requirements.txt

# 2. Download model
!mkdir -p models/llm
!wget -q https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/llm/model.gguf

# 3. Import and use
from src.pipeline import create_pipeline

pipeline = create_pipeline({
    "llm_model_path": "models/llm/model.gguf",
    "device": "cuda"
})

# Ask a question
result = pipeline.process_text_query(
    "Explique-moi la gravité en physique",
    use_rag=True
)

print(result['response'])
```

## 🎯 Common Issues

### "No module named 'torch'"
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "Model not found"
Make sure you downloaded the model to `models/llm/model.gguf`

### "CUDA out of memory"
Use a smaller model or set `device="cpu"` in the config

### "Piper not found"
For TTS functionality:
```bash
pip install piper-tts
```

## 📚 What's Next?

1. **Add Your Content**: Place course materials in `data/` folders
2. **Customize**: Modify the system prompts in `src/llm.py`
3. **Experiment**: Try different models and configurations
4. **Extend**: Add new subjects or features

## 🔗 Resources

- [Main README](README.md) - Detailed documentation
- [00_env_sanity.ipynb](00_env_sanity.ipynb) - Environment verification
- [Model Directory](models/llm/README.md) - Model recommendations
- [Data Directory](data/maths/README.md) - Content guidelines

## 💡 Tips

- **GPU**: Use GPU for faster inference (50-100x speedup)
- **Model Size**: Larger models = better quality but slower
- **Context**: RAG works best with well-structured course materials
- **Language**: System supports French, English, and more

---

**Need Help?** Open an issue on GitHub!