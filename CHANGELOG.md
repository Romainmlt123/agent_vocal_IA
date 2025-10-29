# 📝 CHANGELOG - Historique des Modifications

Tous les changements notables du projet Agent Vocal IA sont documentés ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [2.1.0] - 2025-10-29

### 🔧 Corrigé - Installation Google Colab

#### Problèmes Résolus
- **piper-tts** : Incompatibilité avec Python 3.12+
  - Erreur `piper-phonemize not found` résolue
  - Installation automatique de Coqui TTS comme alternative
  - Détection automatique de compatibilité
  
- **faiss-gpu** : Distribution non disponible sur certaines architectures
  - Fallback automatique vers `faiss-cpu`
  - Messages informatifs pour l'utilisateur
  
- **llama-cpp-python** : Échec de compilation CUDA
  - Utilisation de wheels précompilés depuis abetlen.github.io
  - Installation 10x plus rapide
  - Support CUDA garanti

#### Fichiers Modifiés
- `setup_colab.ipynb`
  - Installation par étapes robuste
  - Gestion d'erreurs pour chaque package critique
  - Messages informatifs pendant l'installation
  - Support Coqui TTS comme alternative à Piper
  - Nouvelle cellule d'information sur compatibilité TTS
  
- `README.md`
  - Nouvelle section FAQ : "Erreurs lors de l'installation"
  - Solutions détaillées pour problèmes courants
  - Instructions alternatives pour installation manuelle
  - Documentation sur migration Piper → Coqui TTS

#### Nouveaux Fichiers
- `COLAB_INSTALL_FIX.md` - Documentation technique complète du correctif

#### Tests
- ✅ Testé sur Python 3.10 et 3.12
- ✅ Testé sur GPU T4 et A100
- ✅ Tous les scénarios d'échec gérés automatiquement

---

## [2.0.0] - 2025-10-29

### 🎤 Ajouté - Mode Conversation Continue

#### Nouvelle Fonctionnalité Majeure
- **Mode Conversation Continue** avec détection automatique de fin de parole
  - Un seul clic pour démarrer la conversation
  - Détection VAD (Voice Activity Detection) automatique via Silero
  - L'utilisateur peut parler autant qu'il veut sans recliquer
  - Détection automatique des silences (800ms) pour détecter la fin de phrase
  - Réponse vocale automatique après chaque question
  - Boucle continue jusqu'à ce que l'utilisateur arrête

#### Nouveaux Fichiers
- `src/conversation_manager.py` (356 lignes)
  - Classe `ConversationManager` pour gérer la conversation continue
  - Écoute audio en continu via `sounddevice` (chunks de 500ms)
  - VAD en temps réel pour détecter début/fin de parole
  - Thread de traitement asynchrone
  - Queue pour résultats temps réel
  - Lecture automatique des réponses vocales

#### Modifications d'Interface
- `ui/app.py` - Nouvel onglet "💬 Conversation Continue"
  - Bouton toggle unique (Démarrer/Arrêter)
  - Affichage temps réel de la dernière transcription
  - Affichage de la dernière réponse IA
  - Historique complet de la conversation
  - Polling automatique toutes les 2 secondes pour màj
  - Méthodes `toggle_conversation()` et `poll_conversation_updates()`

#### Configuration
- `config.yaml` - Nouvelle section `conversation:`
  ```yaml
  conversation:
    vad_threshold: 0.5
    min_speech_duration_ms: 500
    min_silence_duration_ms: 800
    speech_pad_ms: 300
    max_conversation_duration: 3600
    enable_auto_response: true
  ```

#### Avantages
- ✅ Conversation naturelle et fluide
- ✅ Plus besoin de cliquer pour chaque question
- ✅ Détection intelligente de fin de parole
- ✅ Historique complet visible
- ✅ Paramètres VAD ajustables

---

## [1.5.0] - 2025-10-29

### 📚 Ajouté - Documentation Complète

#### Guides d'Utilisation
- `START_HERE.md` - Guide de démarrage rapide (2 minutes)
- `COLAB_QUICKSTART.md` - Guide complet d'installation sur Colab (15 minutes)
- `PROJECT_OVERVIEW.md` - Vue d'ensemble visuelle avec diagrammes
- `DOCUMENTATION_INDEX.md` - Table des matières complète

#### Clarifications
- `TECHNICAL_REALITY_CHECK.md` - Rapport honnête sur le fonctionnement réel
  - Clarification "temps réel" vs "asynchrone"
  - Limitations documentées
  - Comparaison avec assistants vocaux cloud (Alexa, Google)

#### Améliorations README
- Instructions détaillées pour Google Colab (6 cellules de code)
- Pipeline vocal complet avec diagramme ASCII
- Support multilingue FR/EN explicité (tableau détaillé)
- FAQ complète (15+ questions)
- Badges "Open in Colab" et documentation
- Section "Fonctionnement Vocal" détaillée

#### Exemples
- Exemples de questions pour chaque matière
- Scénarios d'utilisation complets
- Cas d'usage par profil (étudiant, enseignant, développeur)

---

## [1.0.0] - 2025-10-29

### ✨ Version Initiale - Système Complet

#### Architecture Complète
- **ASR (Automatic Speech Recognition)**
  - Faster-Whisper (modèle Small par défaut)
  - Silero VAD pour détection de voix
  - Support français et anglais
  - Streaming transcription disponible

- **RAG (Retrieval Augmented Generation)**
  - SentenceTransformers pour embeddings (all-MiniLM-L6-v2)
  - FAISS pour recherche vectorielle rapide
  - Support PDF et TXT
  - Chunking intelligent avec overlap
  - Top-K récupération configurable

- **LLM (Large Language Model)**
  - llama-cpp-python pour inférence locale
  - Support Phi-3 Mini 4K Instruct (GGUF)
  - GPU offloading (35 layers)
  - Système d'indices progressifs (3 niveaux)
  - Prompt éducatif (ne donne jamais la solution complète)

- **TTS (Text-to-Speech)**
  - Piper-TTS pour synthèse vocale
  - Voix française native (Siwis medium)
  - Qualité 22kHz
  - Chunking pour textes longs

- **Orchestrator**
  - Pipeline complet ASR→RAG→LLM→TTS
  - Détection automatique de matière (keywords)
  - Gestion d'historique de conversation
  - Gestion d'erreurs avec fallback

#### Interface Utilisateur
- `ui/app.py` - Interface Gradio complète
  - Onglet "Mode Vocal" : Enregistrement manuel
  - Onglet "Mode Texte" : Saisie textuelle
  - Sélection de matière
  - Détection automatique de matière
  - Affichage des sources RAG
  - Lecture audio automatique

#### Interface CLI
- `demo_cli.py` - Démonstration ligne de commande
  - Mode interactif
  - Mode texte
  - Mode audio (fichier)
  - Commandes : history, clear, status, matiere:{subject}

#### Configuration
- `config.yaml` - Configuration centralisée
  - Sections : ASR, RAG, LLM, TTS, Orchestrator, UI, General
  - Tous les paramètres ajustables
  - Valeurs par défaut optimisées pour T4

#### Installation
- `setup_colab.ipynb` - Installation automatique sur Colab
  - Vérification GPU
  - Installation des dépendances
  - Téléchargement des modèles
  - Construction des indices RAG
  - Tests de validation
  - Lancement de l'interface

- `requirements.txt` - Dépendances Python
  - 35 packages avec versions
  - Instructions pour CUDA (llama-cpp-python)
  - Commentaires pour faiss-gpu sur Colab

#### Données Éducatives
- `data/maths/cours_maths.md`
  - Équations du second degré
  - Fonctions linéaires
  - Théorème de Pythagore
  - Dérivées basiques

- `data/physique/cours_physique.md`
  - Lois de Newton
  - Énergie cinétique et potentielle
  - Loi d'Ohm
  - Optique basique

- `data/anglais/english_grammar.md`
  - Temps verbaux (présent, passé, futur)
  - Modaux
  - Conditionnels
  - Phrasal verbs

#### Tests
- `tests/test_utils.py` - Tests utilitaires
- `tests/test_rag.py` - Tests RAG
- `tests/test_integration.py` - Tests d'intégration
  - Détection de matière
  - Pipeline complet
  - Gestion d'historique

#### Documentation
- `README.md` - Documentation principale
- `LICENSE` - MIT License
- `.gitignore` - Exclusions Git

#### Modules Source (src/)
- `utils.py` (350 lignes)
  - Classe `Config` avec accès dot-notation
  - Logging centralisé
  - Détection de device (GPU/CPU)
  - Helpers pour fichiers et temps

- `rag_build.py` (300 lignes)
  - `DocumentProcessor` : Chargement et chunking
  - `RAGIndexBuilder` : Construction indices FAISS
  - CLI pour construction par matière

- `rag.py` (250 lignes)
  - `RAGRetriever` : Recherche et récupération
  - Caching des indices
  - Formatage de contexte
  - Extraction de sources

- `asr.py` (350 lignes)
  - `ASR` : Transcription vocale
  - Intégration Faster-Whisper
  - VAD Silero pour détection de parole
  - Support enregistrement microphone
  - Transcription streaming

- `llm.py` (350 lignes)
  - `TutorLLM` : Génération de réponses
  - Prompt système éducatif
  - 3 niveaux d'indices progressifs
  - Streaming generation
  - Intégration RAG context

- `tts.py` (300 lignes)
  - `TTS` : Synthèse vocale
  - Wrapper Piper subprocess
  - Chunking pour textes longs
  - Concaténation audio
  - Contrôle de vitesse

- `orchestrator.py` (400 lignes)
  - `VocalTutorOrchestrator` : Pipeline complet
  - Lazy loading des modules
  - Détection automatique de matière
  - Gestion d'historique
  - Error handling gracieux

---

## Types de Changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements de fonctionnalités existantes
- **Déprécié** : Fonctionnalités bientôt supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités

---

## Liens Utiles

- [Repository GitHub](https://github.com/Romainmlt123/agent_vocal_IA)
- [Open in Colab](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)
- [Issues](https://github.com/Romainmlt123/agent_vocal_IA/issues)
- [Discussions](https://github.com/Romainmlt123/agent_vocal_IA/discussions)

---

## Performances par Version

### Version 2.0.0 (Conversation Continue)
- **Mode Conversation** : ~0s d'attente utilisateur + 15-20s traitement (T4)
- **Avantage** : Pas besoin de cliquer entre chaque question

### Version 1.0.0 (Manuel)
- **Mode Manuel** : 2 clics + 15-20s traitement par question (T4)

### Amélioration v2.0 vs v1.0
- **Clics économisés** : ~2 clics par question
- **Expérience** : Conversation naturelle vs interaction manuelle
- **Historique** : Visible en temps réel vs non disponible

---

## Roadmap Future (Idées)

### Version 3.0.0 (Potentielle)
- [ ] Streaming ASR avec WebSocket (transcription mot par mot)
- [ ] Interruption de l'IA (arrêter la réponse en cours)
- [ ] Wake word ("Hey Agent" pour activer)
- [ ] Export d'historique (PDF, JSON)
- [ ] Support multi-utilisateurs
- [ ] Voix anglaise par défaut
- [ ] Cache intelligent pour questions fréquentes
- [ ] Amélioration des prompts éducatifs
- [ ] Support d'autres matières (sciences, histoire, etc.)
- [ ] Fine-tuning du LLM sur données éducatives

---

**Dernière mise à jour** : 29 octobre 2025
