# LLM Models Directory

Place your GGUF language model files here.

## Required Models

You need at least one GGUF format model for the local LLM.

### Recommended Models

1. **Mistral 7B GGUF** (Recommended for French)
   - Download from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   - File: `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (~4.4 GB)

2. **Llama 2 7B GGUF**
   - Download from: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
   - File: `llama-2-7b-chat.Q4_K_M.gguf` (~4 GB)

3. **Phi-2 GGUF** (Smaller, faster)
   - Download from: https://huggingface.co/TheBloke/phi-2-GGUF
   - File: `phi-2.Q4_K_M.gguf` (~1.6 GB)

### Model Format

- Format: GGUF (GGML Unified Format)
- Quantization: Q4_K_M or Q5_K_M recommended (good balance of quality/speed)

### Download Instructions

```bash
# Using huggingface-cli
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir models/llm/

# Or use wget
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O models/llm/model.gguf
```

### GPU Requirements

- Recommended: 8GB+ VRAM for 7B models
- Minimum: 4GB VRAM (may need smaller models or CPU offloading)

### Usage

The model will be automatically loaded by the pipeline. Ensure the path in your configuration matches the model filename.
