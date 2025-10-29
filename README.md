# 🎓 Agent Vocal IA - Tuteur Éducatif Local

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Un assistant vocal éducatif **100% local** pour l'apprentissage interactif. Conçu pour Google Colab (GPU T4/A100), sans aucune dépendance à des APIs externes.

**🎤 Parlez à votre IA - Elle vous répond vocalement avec des indices progressifs !**

---

## 🎯 Objectif

Créer un tuteur vocal IA capable de :

- 🎤 **Écouter** : L'utilisateur parle (français ou anglais) → Transcription vocale avec Faster-Whisper
- 🔍 **Chercher** : Récupération d'informations pertinentes via RAG (FAISS + SentenceTransformers)
- 🧠 **Raisonner** : Génération de réponses pédagogiques avec LLM local (Phi-3 Mini)
- 🔊 **Parler** : Réponse vocale avec Piper-TTS
- 💡 **Guider** : Fournir 3 niveaux d'indices progressifs sans jamais donner la solution complète

### Matières Supportées
- 📐 **Mathématiques** : Algèbre, géométrie, calcul
- ⚡ **Physique** : Mécanique, électricité, énergie
- 🇬🇧 **Anglais** : Grammaire, vocabulaire, traduction

---

## ✨ Fonctionnalités

### 🎤 Modes d'Interaction

#### 1. **Mode Conversation Continue** (Recommandé)
- Cliquez une fois pour démarrer
- Parlez naturellement autant que vous voulez
- Détection automatique de fin de parole (VAD)
- L'IA répond vocalement après chaque question
- Cliquez pour arrêter quand vous avez fini

#### 2. **Mode Vocal Manuel**
- Cliquez pour commencer l'enregistrement
- Parlez votre question
- Cliquez pour arrêter
- L'IA traite et répond

#### 3. **Mode Texte**
- Tapez votre question
- Option de génération vocale de la réponse

### 🧠 Système d'Indices Progressifs

L'IA ne donne **jamais** la solution complète. Elle guide avec 3 niveaux :

**Exemple : "Résoudre x² - 4 = 0"**

```
Indice 1 (Léger) : "As-tu pensé à la factorisation ?"
Indice 2 (Moyen) : "C'est une différence de carrés : a² - b²"
Indice 3 (Fort) : "Factorise en (x-2)(x+2) = 0, puis applique le produit nul"
```

L'élève doit trouver : **x = 2 ou x = -2**

---

## 🚀 Installation sur Google Colab

### Option 1 : Installation Automatique (Recommandée)

1. **Cliquez sur le badge** → [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)

2. **Activez le GPU** :
   - Menu "Exécution" → "Modifier le type d'exécution"
   - Sélectionnez "T4 GPU" ou "A100 GPU"
   - Cliquez "Enregistrer"

3. **Exécutez toutes les cellules** :
   - Menu "Exécution" → "Tout exécuter"
   - Attendez ~10-15 minutes (installation + téléchargement des modèles)

4. **Lancez l'interface** :
   - Un lien public Gradio s'affichera : `https://xxxxx.gradio.live`
   - Cliquez dessus pour ouvrir l'interface

5. **Commencez à parler** ! 🎤

### Option 2 : Installation Manuelle

```python
# Cellule 1 : Vérifier le GPU
!nvidia-smi

# Cellule 2 : Cloner le projet
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA

# Cellule 3 : Installer les dépendances
!pip install -q -r requirements.txt
!pip install -q faiss-gpu
!CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install -q llama-cpp-python --upgrade --force-reinstall --no-cache-dir

# Cellule 4 : Télécharger les modèles IA
!mkdir -p models/llm models/voices

# LLM : Phi-3 Mini 4K Instruct (2.4 GB)
!wget -q --show-progress -P models/llm/ \
  https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# TTS : Voix française Piper (60 MB)
!wget -q --show-progress -P models/voices/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
!wget -q --show-progress -P models/voices/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json

# Cellule 5 : Construire les indices RAG
!python -m src.rag_build --subject maths
!python -m src.rag_build --subject physique
!python -m src.rag_build --subject anglais

# Cellule 6 : Lancer l'interface
from ui.app import launch_ui
launch_ui(share=True)
```

---

## 💻 Utilisation

### Interface Gradio (Mode Principal)

Une fois l'interface lancée :

1. **Autorisez le microphone** dans votre navigateur
2. **Sélectionnez une matière** ou laissez la détection automatique
3. **Choisissez votre mode** :

#### Mode Conversation Continue 💬
```
1. Cliquez "🎤 Démarrer la conversation"
2. Parlez : "Comment résoudre une équation du second degré ?"
3. Attendez 1 seconde (le VAD détecte automatiquement la fin)
4. Écoutez la réponse vocale (~20 secondes de traitement)
5. Continuez à parler sans recliquer !
6. Cliquez "🛑 Arrêter" quand vous avez fini
```

#### Mode Vocal Manuel 🎤
```
1. Cliquez sur le bouton micro
2. Parlez votre question
3. Cliquez à nouveau pour arrêter
4. Écoutez la réponse
```

#### Mode Texte 💬
```
1. Tapez votre question
2. Activez "Générer l'audio" si vous voulez la voix
3. Cliquez "Envoyer"
4. Lisez/écoutez la réponse
```

### CLI (Ligne de Commande)

```bash
# Mode interactif
python demo_cli.py --interactive

# Mode texte simple
python demo_cli.py --text "Explique-moi le théorème de Pythagore"

# Mode audio avec fichier
python demo_cli.py --audio question.wav --subject maths
```

---

## 🏗️ Architecture

```
agent_vocal_IA/
├── README.md                    # Ce fichier
├── CHANGELOG.md                 # Historique des modifications
├── requirements.txt             # Dépendances Python
├── config.yaml                  # Configuration centralisée
├── setup_colab.ipynb            # Installation automatique Colab
├── demo_cli.py                  # Interface CLI
│
├── src/                         # Code source principal
│   ├── __init__.py
│   ├── utils.py                 # Utilitaires (Config, logging)
│   ├── asr.py                   # Reconnaissance vocale (Faster-Whisper + VAD)
│   ├── rag_build.py             # Construction des indices RAG
│   ├── rag.py                   # Recherche RAG (FAISS)
│   ├── llm.py                   # Génération LLM (Phi-3 Mini)
│   ├── tts.py                   # Synthèse vocale (Piper-TTS)
│   ├── orchestrator.py          # Pipeline complet ASR→RAG→LLM→TTS
│   └── conversation_manager.py  # Gestion conversation continue avec VAD
│
├── ui/                          # Interface utilisateur
│   ├── __init__.py
│   └── app.py                   # Interface Gradio
│
├── data/                        # Données éducatives
│   ├── maths/                   # Cours de mathématiques
│   ├── physique/                # Cours de physique
│   ├── anglais/                 # Cours d'anglais
│   └── indices/                 # Indices FAISS (générés)
│
├── models/                      # Modèles IA (téléchargés)
│   ├── llm/                     # Phi-3 Mini GGUF (~2.4 GB)
│   └── voices/                  # Voix Piper ONNX (~60 MB)
│
├── outputs/                     # Sorties générées
│   └── audio/                   # Fichiers audio TTS
│
└── tests/                       # Tests unitaires
    ├── test_utils.py
    ├── test_rag.py
    └── test_integration.py
```

---

## ⚙️ Configuration

Tous les paramètres sont dans `config.yaml` :

### ASR (Reconnaissance Vocale)
```yaml
asr:
  model_name: "small"          # tiny, base, small, medium, large
  language: "fr"               # Français par défaut
  device: "cuda"               # GPU si disponible
  compute_type: "float16"      # int8, float16, float32
  vad_enabled: true
```

### RAG (Retrieval Augmented Generation)
```yaml
rag:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 512
  chunk_overlap: 50
  top_k: 3                     # Nombre de documents récupérés
```

### LLM (Modèle de Langage)
```yaml
llm:
  model_path: "models/llm/phi-3-mini-4k-instruct.Q4_K_M.gguf"
  n_gpu_layers: 35             # Offloading GPU
  temperature: 0.7
  max_tokens: 512
  progressive_hints: true
  hint_levels: 3
```

### Conversation Continue
```yaml
conversation:
  vad_threshold: 0.5           # Seuil détection parole (0-1)
  min_speech_duration_ms: 500  # Durée min de parole
  min_silence_duration_ms: 800 # Silence pour fin de phrase
```

### TTS (Synthèse Vocale)
```yaml
tts:
  model_path: "models/voices/fr_FR-siwis-medium.onnx"
  sample_rate: 22050
  speed: 1.0
```

---

## 🌍 Support Multilingue

| Composant | Français 🇫🇷 | Anglais 🇬🇧 |
|-----------|--------------|-------------|
| **Écoute (ASR)** | ✅ Oui | ✅ Oui |
| **Compréhension (LLM)** | ✅ Oui | ✅ Oui |
| **Réponse écrite** | ✅ Oui | ✅ Oui |
| **Voix (TTS)** | ✅ Oui (native) | ⚠️ Texte FR uniquement* |

*Pour une voix anglaise, téléchargez une voix Piper EN et modifiez `config.yaml`

---

## 📊 Performances

### Configuration Recommandée (Google Colab)

| Hardware | GPU T4 (Gratuit) | GPU A100 (Pro) |
|----------|------------------|----------------|
| VRAM | 15 GB | 40 GB |
| Coût | Gratuit | ~$10/mois |

### Temps de Réponse

| Étape | T4 | A100 |
|-------|-----|------|
| Transcription (10s audio) | ~2s | ~1s |
| Recherche RAG | <0.5s | <0.3s |
| Génération LLM (200 tokens) | ~10-15s | ~3-5s |
| Synthèse vocale | ~1s | ~0.5s |
| **TOTAL par question** | **~15-20s** | **~5-7s** |

**Note** : Le mode conversation continue a un délai de traitement après chaque question, mais l'utilisateur peut enchaîner plusieurs questions sans recliquer.

---

## 🧪 Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_utils.py -v
pytest tests/test_rag.py -v
pytest tests/test_integration.py -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html
```

---

## 🎓 Exemples de Questions

### 📐 Mathématiques
```
"Comment résoudre x² + 2x - 3 = 0 ?"
"Explique-moi le théorème de Pythagore"
"C'est quoi une dérivée ?"
"Comment factoriser une expression ?"
```

### ⚡ Physique
```
"Quelle est la loi de Newton ?"
"Explique-moi la loi d'Ohm"
"Différence entre énergie cinétique et potentielle ?"
"Comment calculer une force ?"
```

### 🇬🇧 Anglais
```
"When do we use the present perfect?"
"Quelle est la différence entre 'do' et 'make' ?"
"Comment conjuguer 'to be' au passé ?"
"Explique-moi les phrasal verbs"
```

---

## 📚 Ajouter Vos Propres Documents

1. **Ajoutez vos fichiers** (PDF ou TXT) dans `data/{matiere}/`
   ```bash
   # Exemple
   cp mes_cours.pdf data/maths/
   ```

2. **Reconstruisez l'indice RAG**
   ```python
   !python -m src.rag_build --subject maths
   ```

3. **L'IA utilisera vos nouveaux documents !**

---

## ❓ FAQ

### Le microphone ne fonctionne pas sur Colab

**Solution** : Le micro ne fonctionne PAS dans l'iframe Colab. Utilisez le **lien public Gradio** (`https://xxxxx.gradio.live`) qui s'affiche dans les logs.

### C'est trop lent sur T4

**Normal !** Le GPU T4 gratuit est limité. Solutions :
- Utilisez un GPU A100 (Colab Pro)
- Réduisez `llm.max_tokens` dans `config.yaml`
- Utilisez le mode texte pour les tests rapides

### Le VAD coupe ma phrase trop tôt

**Ajustez les paramètres** dans `config.yaml` :
```yaml
conversation:
  min_silence_duration_ms: 1200  # Au lieu de 800
```

### Comment changer de modèle LLM ?

1. Téléchargez un modèle GGUF depuis [Hugging Face](https://huggingface.co/models?library=gguf)
2. Placez-le dans `models/llm/`
3. Modifiez `config.yaml` :
   ```yaml
   llm:
     model_path: "models/llm/votre-modele.gguf"
   ```

### Le lien Gradio a expiré

Les liens publics expirent après ~72h. **Relancez simplement** :
```python
from ui.app import launch_ui
launch_ui(share=True)
```

### Erreur "CUDA out of memory"

**Réduisez l'utilisation GPU** dans `config.yaml` :
```yaml
llm:
  n_gpu_layers: 20  # Au lieu de 35
```

Ou **redémarrez le runtime Colab** : Menu "Exécution" → "Redémarrer la session"

---

## 🔒 Limitations

- **100% local** : Nécessite GPU pour performances acceptables (T4 minimum)
- **Latence** : ~15-20s par question sur T4 (normal pour LLM local)
- **Voix française uniquement** : Pour l'anglais, il faut télécharger une voix EN
- **VAD peut couper** : Sur pauses longues (> 800ms), ajustable dans config
- **Pas de streaming transcription** : La transcription apparaît d'un coup (limitation Faster-Whisper)
- **Connexion Internet** : Nécessaire uniquement pour le téléchargement initial des modèles (~3 GB)

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez (`git commit -m 'Ajout fonctionnalité X'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

### Standards de Code
- Type hints sur toutes les fonctions
- Docstrings (style Google)
- Tests unitaires pour nouvelles fonctionnalités
- PEP8 (formatage avec Black)

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

Merci aux projets open-source :
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) (SYSTRAN)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [FAISS](https://github.com/facebookresearch/faiss) (Meta)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [Piper TTS](https://github.com/rhasspy/piper) (Rhasspy)
- [Gradio](https://www.gradio.app/)
- [Sentence Transformers](https://www.sbert.net/)

---

## 👤 Auteur

**Romain Mallet** - Intelligence Lab  
📧 GitHub : [Romainmlt123](https://github.com/Romainmlt123)

---

## 📞 Support

- 🐛 **Bugs** : [GitHub Issues](https://github.com/Romainmlt123/agent_vocal_IA/issues)
- 💬 **Questions** : [GitHub Discussions](https://github.com/Romainmlt123/agent_vocal_IA/discussions)
- 📖 **Documentation** : Ce README + [CHANGELOG.md](CHANGELOG.md)

---

**🎓 Transformez l'apprentissage avec l'IA vocale locale !**
