# 🚀 Guide de Démarrage Rapide

Guide étape par étape pour utiliser Agent Vocal IA

## 📋 Prérequis

- Python 3.10+
- GPU NVIDIA recommandé (T4 ou A100 sur Google Colab)
- 10-15 GB d'espace disque pour les modèles

## ⚡ Démarrage Rapide (5 minutes)

### 1. Installation sur Google Colab

```python
# Cellule 1: Cloner le dépôt
!git clone https://github.com/Romainmlt123/agent_vocal_IA.git
%cd agent_vocal_IA

# Cellule 2: Installer les dépendances
!pip install -q -r requirements.txt

# Cellule 3: Installer FAISS GPU et llama-cpp avec CUDA
!pip install -q faiss-gpu
!CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install -q llama-cpp-python --upgrade --force-reinstall --no-cache-dir

# Cellule 4: Vérifier l'installation
from src.utils import check_environment
env = check_environment()
print("✅ Environnement prêt!" if all(env.values()) else "⚠️ Certains composants manquants")
```

### 2. Télécharger les Modèles

```python
# LLM: Phi-3 Mini (2.4 GB) - Recommandé pour T4
!wget -P models/llm/ https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Voix TTS française
!wget -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
!wget -P models/voices/ https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json
```

### 3. Construire les Indices RAG

Les exemples de cours sont déjà fournis. Construisez les indices :

```bash
# Construire tous les indices
python -m src.rag_build --subject all

# Ou un seul à la fois
python -m src.rag_build --subject maths
python -m src.rag_build --subject physique
python -m src.rag_build --subject anglais
```

### 4. Tester les Modules

```bash
# Test ASR (si vous avez un fichier audio)
python -m src.asr --audio test.wav

# Test RAG
python -m src.rag --query "Comment résoudre une équation?" --subject maths

# Test LLM
python -m src.llm --question "Explique le théorème de Pythagore"

# Test TTS
python -m src.tts --text "Bonjour, je suis votre tuteur"
```

### 5. Lancer l'Interface

```python
# Dans Colab
from ui.app import launch_ui
launch_ui(share=True)  # share=True pour lien public
```

Ou en ligne de commande :

```bash
python ui/app.py --share
```

## 📝 Exemples d'Utilisation

### Mode CLI - Question Texte

```bash
python demo_cli.py --text "Comment calculer la dérivée de x²?" --subject maths
```

### Mode CLI - Interactif

```bash
python demo_cli.py --interactive
```

Puis posez vos questions :

```
❓ Votre question: Quelle est la loi d'Ohm ?
❓ Votre question: How do you form the past tense?
```

### Mode Audio (avec fichier WAV)

```bash
python demo_cli.py --audio question.wav
```

## 🔧 Configuration

Modifiez `config.yaml` pour ajuster :

```yaml
asr:
  model_name: "small"  # tiny, base, small, medium, large

llm:
  model_path: "models/llm/phi-3-mini-4k-instruct.Q4_K_M.gguf"
  n_gpu_layers: 35  # Plus = plus rapide mais plus de VRAM
  temperature: 0.7  # Créativité (0.1-1.0)

tts:
  speed: 1.0  # Vitesse de parole
```

## 🎯 Cas d'Usage Typiques

### 1. Aide aux Devoirs

**Question:** "Je ne comprends pas comment résoudre 2x + 5 = 13"

**Réponse du tuteur:**
- Indice 1: Que faut-il faire pour isoler x ?
- Indice 2: Commence par soustraire 5 des deux côtés
- Indice 3: Tu obtiens 2x = 8, maintenant divise par 2

### 2. Révision de Cours

**Question:** "C'est quoi le principe d'inertie ?"

**Réponse:** Explication avec contexte des documents de physique

### 3. Pratique d'Anglais

**Question:** "Quelle est la différence entre 'since' et 'for' ?"

**Réponse:** Explication grammaticale avec exemples

## 🐛 Résolution de Problèmes

### Erreur: GPU non détecté

```bash
# Vérifier CUDA
nvidia-smi

# Si pas de GPU, modifier config.yaml :
asr:
  device: "cpu"
  compute_type: "int8"
```

### Erreur: Modèle LLM non trouvé

```bash
# Vérifier le chemin dans config.yaml
# Télécharger à nouveau si nécessaire
ls -lh models/llm/
```

### Erreur: RAG index not found

```bash
# Construire les indices
python -m src.rag_build --subject all
```

### TTS ne fonctionne pas

```bash
# Installer piper-tts
pip install piper-tts

# Ou utiliser le binaire Piper
# Télécharger depuis: https://github.com/rhasspy/piper/releases
```

## 📚 Ajouter Vos Propres Documents

1. Ajoutez des fichiers PDF ou TXT dans `data/{matiere}/`
2. Reconstruisez l'indice :

```bash
python -m src.rag_build --subject maths --input data/maths/
```

3. Testez :

```bash
python -m src.rag --query "votre question" --subject maths
```

## 🧪 Lancer les Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_utils.py -v
pytest tests/test_integration.py -v
```

## 📖 Ressources

- Documentation complète: `README.md`
- Configuration: `config.yaml`
- Setup Colab: `setup_colab.ipynb`
- Exemples: `demo_cli.py`

## 💡 Conseils

1. **Première utilisation lente?** Les modèles sont chargés à la demande, c'est normal
2. **GPU T4?** Utilisez Whisper Small et Phi-3 Mini
3. **GPU A100?** Vous pouvez utiliser Whisper Medium et des LLMs plus gros
4. **Pas de GPU?** Tout fonctionne sur CPU mais 5-10x plus lent
5. **Questions complexes?** Le système donne des indices, pas des solutions complètes!

## 🎓 Prêt à Commencer?

```bash
python demo_cli.py --interactive
```

**Amusez-vous bien avec votre tuteur vocal IA! 🚀**
