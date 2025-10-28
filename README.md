# 🎓 Agent Vocal IA - Tuteur Éducatif Local

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)
[![Documentation](https://img.shields.io/badge/docs-START_HERE-blue)](START_HERE.md)
[![Guide Colab](https://img.shields.io/badge/guide-COLAB_QUICKSTART-green)](COLAB_QUICKSTART.md)

Un assistant vocal éducatif **100% local** conçu pour fonctionner sur Google Colab (GPU T4/A100), sans aucune dépendance à des APIs externes.

**🎤 Parlez à votre IA - Elle vous répond vocalement en français !**

---

## 🚀 Démarrage Ultra-Rapide

**Nouveau sur le projet ?** → Consultez [START_HERE.md](START_HERE.md) (2 minutes)

**Premier lancement sur Colab ?** → Suivez [COLAB_QUICKSTART.md](COLAB_QUICKSTART.md) (15 minutes)

**Documentation complète ?** → Continuez ci-dessous ⬇️

---

## 🎯 Objectif

Créer un tuteur vocal IA capable de :

- 🎤 **Écouter** : L'utilisateur **parle** (français ou anglais) → Transcription vocale avec Faster-Whisper + Silero VAD
- 🔍 **Chercher** : Récupération d'informations pertinentes via RAG (FAISS + SentenceTransformers)
- 🧠 **Raisonner** : Génération de réponses pédagogiques avec LLM local (llama-cpp-python)
- 🔊 **Parler** : L'IA **répond vocalement** → Synthèse vocale avec Piper-TTS
- 💡 **Guider** : Fournir 3 niveaux d'indices progressifs sans donner la solution complète

### 🎙️ Fonctionnement Vocal - Pipeline Complet

**L'utilisateur discute avec l'IA via sa voix :**

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎤 CONVERSATION VOCALE                       │
└─────────────────────────────────────────────────────────────────┘

1. 🗣️  VOUS PARLEZ (FR/EN)
   ↓
   "Comment résoudre x² - 4 = 0 ?"
   ↓
   
2. 👂 ASR (Faster-Whisper + Silero VAD)
   ↓
   Transcription : "Comment résoudre x² - 4 = 0 ?"
   ↓
   
3. 🔍 RAG (FAISS + SentenceTransformers)
   ↓
   Cherche dans data/maths/ → Trouve "différence de carrés"
   ↓
   
4. 🧠 LLM Local (Phi-3 Mini avec prompt éducatif)
   ↓
   Génère 3 indices progressifs (SANS la solution complète)
   ↓
   
5. 🔊 TTS (Piper-TTS voix française)
   ↓
   Synthèse vocale de la réponse
   ↓
   
6. 👂 VOUS ÉCOUTEZ la réponse vocale
   ↓
   
7. 🔁 Vous posez une question de suivi...
```

**⚡ Temps total : ~15-20 secondes sur GPU T4, ~5-7 secondes sur GPU A100**

**🌍 Conversation naturelle et fluide en français et anglais !**

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

## 🚀 Installation sur Google Colab - Guide Complet

### 📖 Comment ouvrir le notebook sur Google Colab ?

**Option 1 : Depuis GitHub (Recommandé)**
1. Allez sur [Google Colab](https://colab.research.google.com/)
2. Cliquez sur "Fichier" → "Ouvrir un notebook"
3. Sélectionnez l'onglet "GitHub"
4. Collez l'URL : `https://github.com/Romainmlt123/agent_vocal_IA`
5. Sélectionnez `setup_colab.ipynb`
6. Le notebook s'ouvre automatiquement dans Colab

**Option 2 : Lien direct**
Cliquez sur ce lien : [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)

### ⚡ Installation Complète - Commandes à Exécuter

**Copiez et collez ces commandes dans des cellules Google Colab :**

#### 📦 Cellule 1 : Cloner le projet et vérifier le GPU

```python
# Vérifier le GPU disponible
!nvidia-smi

# Cloner le dépôt
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA

# Afficher la structure
!ls -la
```

#### 📚 Cellule 2 : Installer les dépendances

```python
# Installation des packages Python (prend 5-10 minutes)
!pip install -q -r requirements.txt

# FAISS GPU pour recherche vectorielle rapide
!pip install -q faiss-gpu

# llama-cpp-python avec support CUDA pour LLM local
!CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install -q llama-cpp-python --upgrade --force-reinstall --no-cache-dir

print("✅ Installation terminée!")
```

#### 🤖 Cellule 3 : Télécharger les modèles IA

```python
import os

# Créer les dossiers si nécessaire
!mkdir -p models/llm models/voices

# Télécharger le modèle LLM Phi-3 Mini (2.4 GB - optimisé pour T4)
print("📥 Téléchargement du modèle LLM (2.4 GB)...")
!wget -q --show-progress -P models/llm/ https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Télécharger la voix TTS française (60 MB)
print("🔊 Téléchargement de la voix française...")
!wget -q --show-progress -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
!wget -q --show-progress -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json

# Vérifier les téléchargements
print("\n✅ Modèles téléchargés:")
!ls -lh models/llm/
!ls -lh models/voices/
```

#### 🔍 Cellule 4 : Construire les indices RAG (base de connaissances)

```python
# Construire les indices FAISS pour les 3 matières
# Ces indices permettent la recherche rapide dans les documents

print("🔨 Construction des indices RAG...")
!python -m src.rag_build --subject maths
!python -m src.rag_build --subject physique
!python -m src.rag_build --subject anglais

print("\n✅ Indices RAG créés:")
!ls -lh data/indices/
```

#### ✅ Cellule 5 : Vérifier l'installation

```python
from src.utils import check_environment, setup_logging
import logging

setup_logging(level='INFO')

print("🔍 Vérification de l'environnement...\n")
env = check_environment()

for component, available in env.items():
    status = "✅" if available else "❌"
    print(f"{status} {component}")

if all(env.values()):
    print("\n🎉 Tout est prêt! Vous pouvez lancer l'interface.")
else:
    print("\n⚠️ Certains composants manquent. Revérifiez l'installation.")
```

#### 🎤 Cellule 6 : Lancer l'interface vocale interactive

```python
# Lancer l'interface Gradio avec partage public
from ui.app import launch_ui

print("🚀 Lancement de l'interface Agent Vocal IA...")
print("📱 L'interface sera accessible via un lien public")
print("\n⚠️ IMPORTANT:")
print("   1. Cliquez sur le lien qui s'affichera")
print("   2. Autorisez l'accès au microphone dans votre navigateur")
print("   3. Cliquez sur 🎤 pour enregistrer votre question")
print("   4. Parlez en français ou en anglais")
print("   5. L'IA vous répondra avec des indices progressifs\n")

# Lancement avec partage public (génère un lien temporaire)
launch_ui(share=True)
```

---

## 🎤 Comment Utiliser l'Agent Vocal ?

### Mode d'Interaction Principal : **VOCAL**

L'Agent Vocal IA est conçu pour une **conversation vocale naturelle** :

1. **🎤 Activez votre micro** : Cliquez sur le bouton microphone dans l'interface
2. **💬 Posez votre question** : Parlez naturellement en français ou en anglais
   - "Comment résoudre une équation du second degré ?"
   - "Explique-moi la loi d'Ohm"
   - "How do you form the present perfect tense?"
3. **🔄 Le système traite votre voix** :
   - **ASR** : Transcrit votre voix en texte (Faster-Whisper)
   - **RAG** : Cherche dans les documents pertinents (FAISS)
   - **LLM** : Génère une réponse pédagogique avec indices progressifs
   - **TTS** : Convertit la réponse en voix (Piper-TTS)
4. **🔊 Écoutez la réponse** : L'IA vous répond vocalement avec 3 niveaux d'indices
5. **🔁 Continuez la conversation** : Posez des questions de suivi

### 🌍 Langues Supportées

- **🇫🇷 Français** : ASR (reconnaissance), LLM (compréhension), TTS (voix française naturelle)
- **🇬🇧 Anglais** : ASR (reconnaissance), LLM (compréhension), TTS (voix française pour réponses)

**Note** : L'IA comprend et répond en français ET en anglais, mais la voix de sortie est en français (voix Piper française).

### 💡 Système d'Indices Progressifs

L'IA ne donne **JAMAIS** la solution complète directement. Elle fournit 3 niveaux d'aide :

1. **Indice Niveau 1 (Léger)** : Question guidante ou rappel de concept
2. **Indice Niveau 2 (Moyen)** : Méthode ou approche à utiliser  
3. **Indice Niveau 3 (Fort)** : Début de résolution mais sans la réponse finale

**Exemple :**
```
Vous : "Comment résoudre x² + 2x - 3 = 0 ?"

IA : "
  Indice 1 : As-tu pensé à la formule du discriminant ?
  Indice 2 : Calcule d'abord Δ = b² - 4ac avec a=1, b=2, c=-3
  Indice 3 : Tu trouves Δ = 16. Maintenant utilise les formules x₁ et x₂
"
```

---

## 💻 Utilisation Avancée

### 🎯 Mode Interface Vocale (Recommandé)

**Dans Google Colab :**

```python
from ui.app import launch_ui

# Lance l'interface avec lien public
launch_ui(share=True)
```

Cliquez sur le lien généré (ex: `https://xxxxx.gradio.live`) pour accéder à l'interface.

**Étapes d'utilisation :**
1. Autorisez l'accès au microphone dans votre navigateur
2. Sélectionnez la matière (Mathématiques, Physique, Anglais)
3. Cliquez sur 🎤 et posez votre question vocalement
4. Attendez la transcription et la réponse vocale
5. Continuez la conversation

### 📝 Mode CLI (Ligne de commande - Pour tests)

```bash
# Mode interactif avec détection automatique de matière
python demo_cli.py --interactive

# Test avec un fichier audio
python demo_cli.py --audio input.wav --subject maths

# Test avec texte
python demo_cli.py --text "Explique-moi le théorème de Pythagore"
```

### 🔧 Commandes de maintenance

```bash
# Reconstruire un indice RAG
python -m src.rag_build --subject maths --input data/maths/

# Tester ASR seul
python -m src.asr --demo --audio test.wav

# Tester TTS seul
python -m src.tts --text "Bonjour, je suis votre tuteur vocal" --output output.wav
```

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

### 1. 🎤 Reconnaissance Vocale (ASR)
- **Modèle** : Faster-Whisper (Small par défaut)
- **VAD** : Silero pour détecter les silences et segmenter la parole
- **Langues** : Français et Anglais (détection automatique)
- **Streaming** : Transcription en temps réel possible
- **Entrée** : Microphone direct ou fichiers audio (WAV, MP3)

### 2. 🔍 RAG (Retrieval Augmented Generation)
- **Embeddings** : SentenceTransformers (all-MiniLM-L6-v2)
- **Index** : FAISS pour recherche vectorielle rapide sur GPU/CPU
- **Sources** : PDF et TXT, chunking intelligent avec overlap
- **Matières** : Base de connaissances en maths, physique, anglais
- **Top-K** : Récupère les 3 passages les plus pertinents

### 3. 🧠 LLM Local (Génération de Réponses)
- **Modèles supportés** : Phi-3, Qwen, Mistral (format GGUF)
- **Inférence** : llama-cpp-python avec GPU offloading (35 layers)
- **Langues** : Comprend français et anglais
- **Système de hints** : 3 niveaux d'indices progressifs sans donner la solution
- **Contexte** : Utilise les documents RAG pour des réponses précises

### 4. 🔊 Synthèse Vocale (TTS)
- **Moteur** : Piper-TTS (neural TTS)
- **Voix** : Français natif (siwis medium - naturelle et claire)
- **Qualité** : 22kHz, streaming pour textes longs
- **Sortie** : Fichiers WAV ou lecture directe

### 5. 🎨 Interface Gradio (UI Vocale)
- ✅ Enregistrement audio en un clic depuis le navigateur
- ✅ Autorisation microphone automatique
- ✅ Sélection de matière (ou détection auto)
- ✅ Affichage en temps réel : transcription → réponse → sources RAG
- ✅ Lecture audio de la réponse
- ✅ Historique de conversation
- ✅ Design responsive et intuitif

### 6. 🎯 Orchestration Intelligente
- **Pipeline automatique** : ASR → RAG → LLM → TTS
- **Détection de matière** : Keywords-based (automatique ou manuel)
- **Gestion d'erreurs** : Fallback gracieux si un composant échoue
- **Historique** : Mémorisation du contexte conversationnel

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

## 🔒 Limitations et Notes Importantes

- **100% local** : Aucune API externe → nécessite GPU pour performances acceptables (minimum T4)
- **Langues** : 
  - ✅ **ASR** : Comprend français ET anglais (détection automatique)
  - ✅ **LLM** : Répond en français ET anglais selon la question
  - ⚠️ **TTS** : Voix française uniquement (répond en français même si vous parlez anglais)
- **Mémoire GPU** : 
  - **T4 (15 GB)** : Whisper Small + Phi-3 Mini (performant)
  - **A100 (40 GB)** : Whisper Medium + modèles plus gros possibles
- **Précision RAG** : Dépend de la qualité des documents fournis dans `data/`
- **Hints progressifs** : Le LLM est instruit de ne pas donner la solution complète, mais peut parfois révéler trop d'informations (amélioration continue via prompt engineering)
- **Latence** : 
  - Sur T4 : ~15-20 secondes par question (normal)
  - Sur A100 : ~5-7 secondes par question
- **Connexion Internet** : Nécessaire uniquement pour le téléchargement initial des modèles (~3 GB). Ensuite, tout fonctionne offline.

### 🌍 Support Multilingue Détaillé

| Composant | Français 🇫🇷 | Anglais 🇬🇧 |
|-----------|--------------|-------------|
| **Écoute (ASR)** | ✅ Oui | ✅ Oui |
| **Compréhension (LLM)** | ✅ Oui | ✅ Oui |
| **Réponse écrite** | ✅ Oui | ✅ Oui |
| **Voix (TTS)** | ✅ Oui (voix native) | ⚠️ Texte français uniquement |

**Note** : L'IA peut comprendre et transcrire l'anglais, mais répondra toujours avec une voix française. Pour une voix anglaise, il faudrait télécharger une voix Piper anglaise supplémentaire.

---

## ❓ FAQ - Questions Fréquentes

### 🎤 Comment utiliser le microphone sur Google Colab ?

1. Lancez l'interface avec `launch_ui(share=True)`
2. Cliquez sur le lien public généré (https://xxxxx.gradio.live)
3. Autorisez l'accès au microphone dans votre navigateur
4. Cliquez sur le bouton 🎤 dans l'onglet "Mode Vocal"
5. Parlez normalement, puis arrêtez l'enregistrement

**Note** : Le microphone ne fonctionne PAS directement dans l'iframe Colab, utilisez toujours le lien public Gradio.

### 🌐 Puis-je poser des questions en anglais ?

**Oui !** L'IA comprend parfaitement l'anglais :
- ✅ Vous pouvez parler en anglais
- ✅ L'IA transcrit correctement
- ✅ L'IA répond en anglais (texte)
- ⚠️ Mais la voix est en français

Pour une voix anglaise, modifiez `config.yaml` :
```yaml
tts:
  model_path: "models/voices/en_US-amy-medium.onnx"
```
Et téléchargez une voix anglaise depuis [Piper Voices](https://huggingface.co/rhasspy/piper-voices).

### 🔇 Puis-je utiliser le système sans voix (texte uniquement) ?

**Oui !** Utilisez l'onglet "Mode Texte" dans l'interface Gradio, ou le CLI :

```bash
python demo_cli.py --text "Votre question ici"
```

### 📱 Ça marche sur mobile ?

**Oui !** Le lien Gradio public (`https://xxxxx.gradio.live`) fonctionne sur :
- 📱 Smartphones (iOS/Android)
- 💻 Tablettes
- 🖥️ Ordinateurs

Assurez-vous d'autoriser le microphone dans votre navigateur mobile.

### ⏱️ Pourquoi c'est lent sur T4 ?

C'est **normal** ! Le GPU T4 est gratuit mais moins puissant :
- Transcription : ~2s
- Recherche RAG : <0.5s
- Génération LLM : ~10-15s (c'est ici que ça prend du temps)
- Synthèse vocale : ~1s

**Total : ~15-20 secondes par question**

Pour accélérer :
- Utilisez un GPU A100 (si disponible)
- Réduisez `llm.max_tokens` dans `config.yaml`
- Utilisez un modèle plus petit (Phi-3 Mini est déjà optimisé)

### 💾 Mes données sont-elles sauvegardées ?

**Non**, les fichiers sur Colab sont temporaires (session de ~12h). Pour sauvegarder :

```python
# Sauvegarder sur Google Drive
from google.colab import drive
drive.mount('/content/drive')
!cp -r /content/agent_vocal_IA /content/drive/MyDrive/
```

### 📚 Comment ajouter mes propres documents ?

1. Ajoutez vos fichiers PDF ou TXT dans `data/{matiere}/`
2. Reconstruisez l'indice RAG :

```python
!python -m src.rag_build --subject maths --input data/maths/
```

3. L'IA utilisera vos nouveaux documents !

### 🔄 Le lien Gradio a expiré, comment le relancer ?

Les liens Gradio publics expirent après ~72h. Pour en générer un nouveau :

```python
from ui.app import launch_ui
launch_ui(share=True)
```

### 🤖 Puis-je utiliser un autre modèle LLM ?

**Oui !** Téléchargez un modèle GGUF depuis [Hugging Face](https://huggingface.co/models?library=gguf) :

```python
# Exemple : Mistral 7B
!wget -P models/llm/ https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

Puis mettez à jour `config.yaml` :
```yaml
llm:
  model_path: "models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
  n_gpu_layers: 35
```

### 🎓 L'IA donne la solution complète, comment l'empêcher ?

Le système utilise un **prompt éducatif** qui interdit de donner la solution. Si ça arrive :

1. Ajustez la température dans `config.yaml` (plus bas = plus strict) :
```yaml
llm:
  temperature: 0.5  # Au lieu de 0.7
```

2. Reformulez votre question pour demander explicitement des indices :
"Donne-moi des indices pour résoudre..." au lieu de "Résous..."

### 🔴 Erreur "CUDA out of memory"

Votre GPU est saturé. Solutions :

1. Redémarrez le runtime Colab (Menu "Exécution" → "Redémarrer la session")
2. Réduisez `n_gpu_layers` dans `config.yaml` :
```yaml
llm:
  n_gpu_layers: 20  # Au lieu de 35
```
3. Utilisez un modèle plus petit (Phi-3 Mini est déjà optimal pour T4)

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