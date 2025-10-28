# 🎓 Agent Vocal IA - Tuteur Éducatif Local

Un assistant vocal éducatif **100% local** conçu pour fonctionner sur Google Colab (GPU T4/A100), sans aucune dépendance à des APIs externes.

## 🎯 Objectif

Créer un tuteur vocal IA capable de :

- 🎤 **Écouter** : Transcription vocale avec Faster-Whisper + Silero VAD
- 🔍 **Chercher** : Récupération d'informations pertinentes via RAG (FAISS + SentenceTransformers)
- 🧠 **Raisonner** : Génération de réponses avec LLM local (llama-cpp-python)
- 🔊 **Parler** : Synthèse vocale avec Piper-TTS
- 💡 **Guider** : Fournir 3 niveaux d'indices progressifs sans donner la solution complète

### Matières supportées
- 📐 **Mathématiques** : Algèbre, géométrie, calcul
- ⚡ **Physique** : Mécanique, électricité, énergie
- 🇬🇧 **Anglais** : Grammaire, vocabulaire, traduction

---

## 🏗️ Architecture

```
agent_vocal_IA/
├── README.md                 # Documentation principale
├── requirements.txt          # Dépendances Python
├── config.yaml              # Configuration centralisée
├── setup_colab.ipynb        # Installation et vérification sur Colab
├── demo_cli.py              # Démonstration CLI end-to-end
│
├── src/                     # Code source principal
│   ├── __init__.py
│   ├── asr.py              # Reconnaissance vocale (ASR)
│   ├── rag.py              # Recherche RAG
│   ├── rag_build.py        # Construction des indices RAG
│   ├── llm.py              # Génération LLM locale
│   ├── tts.py              # Synthèse vocale (TTS)
│   ├── orchestrator.py     # Orchestration du pipeline
│   └── utils.py            # Utilitaires et helpers
│
├── ui/                      # Interface utilisateur
│   └── app.py              # Interface Gradio
│
├── data/                    # Données d'entraînement
│   ├── maths/              # Documents de mathématiques
│   ├── physique/           # Documents de physique
│   ├── anglais/            # Documents d'anglais
│   └── indices/            # Indices FAISS générés
│
├── models/                  # Modèles locaux
│   ├── llm/                # Modèles LLM (GGUF)
│   └── voices/             # Voix TTS (ONNX)
│
├── outputs/                 # Sorties générées
│   └── audio/              # Fichiers audio TTS
│
└── tests/                   # Tests unitaires et intégration
    ├── test_asr.py
    ├── test_rag.py
    ├── test_llm.py
    ├── test_tts.py
    └── test_integration.py
```

---

## 🚀 Installation sur Google Colab

### 1. Cloner le dépôt

```python
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA
```

### 2. Installer les dépendances

Ouvrez `setup_colab.ipynb` et exécutez toutes les cellules, ou utilisez :

```python
!pip install -r requirements.txt
```

### 3. Vérifier l'installation

```python
# Vérifier le GPU
!nvidia-smi

# Importer et tester les modules
from src.utils import check_environment
check_environment()
```

### 4. Télécharger les modèles

Les modèles seront automatiquement téléchargés lors de la première utilisation, ou manuellement :

```python
# LLM (exemple : Phi-3 Mini 4K Instruct Q4_K_M)
!wget -P models/llm/ https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# TTS (Piper French voice)
!wget -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
!wget -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

---

## 💻 Utilisation

### Mode CLI (Ligne de commande)

```bash
# Pipeline complet : voix → transcription → RAG → LLM → TTS
python demo_cli.py --audio input.wav --subject maths

# Construire un indice RAG
python -m src.rag_build --subject maths --input data/maths/

# Test ASR seul
python -m src.asr --demo --audio test.wav

# Test TTS seul
python -m src.tts --text "Bonjour, je suis votre tuteur vocal" --output output.wav
```

### Mode UI (Interface Gradio)

```python
from ui.app import launch_ui
launch_ui()
```

Ou directement :

```bash
python ui/app.py
```

L'interface sera accessible à `http://localhost:7860`

---

## 🧪 Tests

Exécuter tous les tests :

```bash
pytest tests/ -v
```

Tests individuels :

```bash
# ASR
pytest tests/test_asr.py -v

# RAG
pytest tests/test_rag.py -v

# LLM
pytest tests/test_llm.py -v

# TTS
pytest tests/test_tts.py -v

# Intégration complète
pytest tests/test_integration.py -v
```

---

## ⚙️ Configuration

Tous les paramètres sont dans `config.yaml` :

- **ASR** : Modèle Whisper, langue, VAD
- **RAG** : Modèle d'embeddings, chunk size, top-k
- **LLM** : Chemin du modèle, température, tokens max
- **TTS** : Voix, vitesse, sample rate
- **Orchestrator** : Détection auto de matière, keywords

### Exemple : Changer le modèle LLM

```yaml
llm:
  model_path: "models/llm/qwen2.5-3b-instruct.Q4_K_M.gguf"
  n_gpu_layers: 35
  temperature: 0.7
```

---

## 🧠 Fonctionnalités Clés

### 1. Transcription Vocale (ASR)
- **Modèle** : Faster-Whisper (Small par défaut)
- **VAD** : Silero pour détecter les silences
- **Streaming** : Transcription en temps réel

### 2. RAG (Retrieval Augmented Generation)
- **Embeddings** : SentenceTransformers (all-MiniLM-L6-v2)
- **Index** : FAISS pour recherche vectorielle rapide
- **Sources** : PDF et TXT, chunking intelligent

### 3. LLM Local
- **Modèles supportés** : Phi-3, Qwen, Mistral (format GGUF)
- **Inférence** : llama-cpp-python avec GPU offloading
- **Système de hints** : 3 niveaux d'indices progressifs

### 4. Synthèse Vocale (TTS)
- **Moteur** : Piper-TTS
- **Voix** : Français natif (siwis, upmc, tom)
- **Qualité** : 22kHz, streaming possible

### 5. Interface Gradio
- Enregistrement audio en un clic
- Sélection de matière
- Affichage des sources RAG
- Lecture de la réponse vocale

---

## 📊 Performances

### Configuration recommandée (Colab)

| Composant | GPU T4 | GPU A100 |
|-----------|--------|----------|
| ASR (Whisper Small) | ~2s / 10s audio | ~1s / 10s audio |
| RAG (recherche) | <0.5s | <0.3s |
| LLM (génération 200 tokens) | ~10-15s | ~3-5s |
| TTS (1 phrase) | ~1s | ~0.5s |

### Mémoire

- **GPU T4 (15 GB)** : Whisper Small + Phi-3 Mini (4K) ou Qwen 2.5B
- **GPU A100 (40 GB)** : Whisper Medium + Mistral 7B ou Qwen 7B

---

## 🛠️ Développement

### Standards de qualité
- ✅ Type hints sur toutes les fonctions
- ✅ Docstrings (Google style)
- ✅ Logging centralisé (niveau DEBUG/INFO)
- ✅ Gestion d'erreurs explicite
- ✅ Tests unitaires et intégration
- ✅ PEP8 (formaté avec Black)

### Contribuer

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité X'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 🔒 Limitations

- **100% local** : Aucune API externe → nécessite GPU pour performances acceptables
- **Langues** : Optimisé pour le français (ASR/TTS), multilingue pour LLM
- **Mémoire** : Modèles lourds → ajuster selon GPU disponible
- **Précision RAG** : Dépend de la qualité des documents fournis
- **Hints progressifs** : L'IA peut parfois révéler trop d'informations (amélioration continue)

---

## 📚 Ressources

### Modèles
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [llama.cpp Python](https://github.com/abetlen/llama-cpp-python)
- [Piper TTS](https://github.com/rhasspy/piper)

### Documentation
- [Google Colab](https://colab.research.google.com/)
- [Gradio](https://www.gradio.app/)
- [Hugging Face](https://huggingface.co/)

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**Romain Mallet** - Intelligence Lab  
📧 Contact : [GitHub](https://github.com/Romainmlt123)

---

## 🙏 Remerciements

Merci aux communautés open-source qui rendent ce projet possible :
- Équipes Whisper (OpenAI), Piper (Rhasspy), FAISS (Meta)
- Contributeurs llama.cpp et llama-cpp-python
- Développeurs Gradio et SentenceTransformers

---

**Note** : Ce projet est conçu pour l'éducation et la recherche. Les performances peuvent varier selon le matériel et les modèles utilisés.