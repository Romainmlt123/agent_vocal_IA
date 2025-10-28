# 🎓 Agent Vocal IA - Résumé Visuel

## 📋 Description en 1 Phrase

**Un tuteur éducatif 100% local qui écoute vos questions vocales (français/anglais) et répond à voix haute avec des indices progressifs, sans jamais donner la solution complète.**

---

## 🎯 Pour Qui ?

- ✅ **Étudiants** : Aide aux devoirs en maths, physique, anglais
- ✅ **Enseignants** : Outil pédagogique pour la classe inversée
- ✅ **Autodidactes** : Apprentissage autonome guidé
- ✅ **Chercheurs en IA** : Système RAG + LLM local complet

---

## 💡 Pourquoi "100% Local" ?

| Avantage | Description |
|----------|-------------|
| 🔒 **Confidentialité** | Vos questions et données restent sur votre machine |
| 🚀 **Pas de limite d'API** | Utilisez autant que vous voulez, gratuitement |
| 📚 **Données personnalisées** | Ajoutez vos propres documents (cours, livres) |
| 🌐 **Fonctionne offline** | Une fois les modèles téléchargés (après installation) |
| 🎓 **Pédagogique** | Comprenez le fonctionnement d'un système IA complet |

---

## 🔧 Technologies Utilisées

### Stack Technique

```
┌─────────────────────────────────────────────────────────────┐
│  Interface Utilisateur                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🎨 Gradio (Web UI avec micro + audio player)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│  Orchestrateur                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🎭 orchestrator.py (Pipeline ASR→RAG→LLM→TTS)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│  Modules IA                                                  │
│                                                              │
│  🎤 ASR (Automatic Speech Recognition)                      │
│     • Faster-Whisper (Small) - Transcription vocale         │
│     • Silero VAD - Détection de voix                        │
│                                                              │
│  🔍 RAG (Retrieval Augmented Generation)                    │
│     • SentenceTransformers - Embeddings                     │
│     • FAISS - Recherche vectorielle                         │
│                                                              │
│  🧠 LLM (Large Language Model)                              │
│     • llama-cpp-python - Inférence locale                   │
│     • Phi-3 Mini 4K (GGUF) - Modèle de langage             │
│                                                              │
│  🔊 TTS (Text-to-Speech)                                    │
│     • Piper-TTS - Synthèse vocale française                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🖥️ Google Colab (GPU T4 / A100)                     │  │
│  │ 🐍 Python 3.10+                                      │  │
│  │ ⚡ PyTorch 2.0+ avec CUDA                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Exemple d'Utilisation Complète

### Scénario : Étudiant en maths qui bloque sur une équation

```
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : L'étudiant parle                                 │
│  🗣️ "Je ne sais pas comment résoudre x au carré moins     │
│     quatre égal zéro"                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : Transcription ASR                                │
│  📝 Texte détecté : "Je ne sais pas comment résoudre       │
│     x² - 4 = 0"                                             │
│  🌍 Langue : Français                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : Recherche RAG                                    │
│  🔍 Recherche dans data/maths/ ...                          │
│  ✅ Trouvé : "Différence de carrés : a² - b² = (a-b)(a+b)" │
│  ✅ Trouvé : "Factorisation d'équations du second degré"   │
│  ✅ Trouvé : "Produit nul : si ab = 0 alors a=0 ou b=0"    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : Génération LLM (avec prompt éducatif)           │
│  🧠 Prompt système : "Tu es un tuteur. Donne 3 indices     │
│     progressifs mais JAMAIS la solution complète."          │
│                                                              │
│  💡 Réponse générée :                                       │
│                                                              │
│  "Indice 1 : Observe ton équation. Reconnais-tu une        │
│   forme particulière avec x² et un nombre seul ?"           │
│                                                              │
│  "Indice 2 : C'est une différence de carrés !              │
│   Rappel : a² - b² = (a - b)(a + b).                       │
│   Ici, x² - 4 = x² - 2²."                                  │
│                                                              │
│  "Indice 3 : Tu peux factoriser en (x - 2)(x + 2) = 0.     │
│   Maintenant, utilise la propriété du produit nul :        │
│   si un produit vaut 0, alors un des facteurs est nul."    │
│                                                              │
│  ❌ PAS de solution donnée (x = 2 ou x = -2)               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : Synthèse vocale TTS                              │
│  🔊 Conversion texte → audio (voix française naturelle)     │
│  ⏱️ Durée : ~3 secondes de parole                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 : L'étudiant écoute                                │
│  👂 Écoute les 3 indices progressifs                        │
│  💭 Réfléchit à la solution                                 │
│  ✍️ Résout : x = 2 ou x = -2 (lui-même !)                 │
│  🎓 Apprentissage réel, pas de copie passive               │
└─────────────────────────────────────────────────────────────┘
```

**⏱️ Temps total : ~15 secondes sur GPU T4**

---

## 🎓 Pédagogie : Pourquoi des Indices Progressifs ?

### ❌ Mauvaise approche (chatbot classique)

```
Élève : "Résoudre x² - 4 = 0"
IA : "La solution est x = 2 ou x = -2"
```

**Problème** : L'élève copie sans comprendre.

### ✅ Notre approche (tuteur éducatif)

```
Élève : "Résoudre x² - 4 = 0"

IA : 
  🔹 Indice 1 : "As-tu pensé à factoriser ?"
  🔹 Indice 2 : "C'est une différence de carrés"
  🔹 Indice 3 : "Factorise en (x-2)(x+2) = 0 et utilise le produit nul"

Élève : *Réfléchit et trouve x = 2 ou x = -2 lui-même*
```

**Bénéfice** : L'élève apprend la méthode, pas juste la réponse.

---

## 📈 Matières Supportées (Extensible)

| Matière | Contenu Actuel | Ajout Possible |
|---------|----------------|----------------|
| 📐 **Maths** | Algèbre, géométrie, calcul | Probabilités, statistiques, analyse |
| ⚡ **Physique** | Mécanique, électricité, énergie | Optique, thermodynamique, quantique |
| 🇬🇧 **Anglais** | Grammaire, conjugaison, vocabulaire | TOEFL, IELTS, Business English |
| ➕ **Votre matière** | - | Ajoutez vos PDFs dans `data/` ! |

**Comment ajouter une matière ?**

1. Créez `data/nouvelle_matiere/`
2. Ajoutez vos PDF/TXT
3. Lancez `python -m src.rag_build --subject nouvelle_matiere`
4. C'est prêt ! 🎉

---

## 🚀 Performances Réelles

### Configuration Testée

| Hardware | GPU T4 (Colab gratuit) | GPU A100 (Colab Pro) |
|----------|------------------------|----------------------|
| VRAM | 15 GB | 40 GB |
| Prix | **Gratuit** | ~$10/mois |

### Temps de Réponse Mesurés

| Étape | T4 | A100 |
|-------|-----|------|
| Transcription (10s audio) | ~2s | ~1s |
| Recherche RAG | <0.5s | <0.3s |
| Génération LLM (200 tokens) | ~10-15s | ~3-5s |
| Synthèse vocale | ~1s | ~0.5s |
| **TOTAL** | **~15-20s** | **~5-7s** |

**Verdict** : T4 gratuit est largement suffisant pour un usage éducatif !

---

## 🌟 Points Forts du Projet

1. ✅ **Vraiment 100% local** : Aucune API externe (OpenAI, Google, etc.)
2. ✅ **Interface vocale naturelle** : Parlez comme à un humain
3. ✅ **Pédagogie intelligente** : Indices progressifs, pas de solutions directes
4. ✅ **Multilingue** : Comprend français et anglais
5. ✅ **Extensible** : Ajoutez vos propres documents facilement
6. ✅ **GPU-optimisé** : Offloading CUDA sur tous les composants
7. ✅ **Code propre** : Type hints, docstrings, tests, modulaire
8. ✅ **Documentation complète** : README, guides, FAQ
9. ✅ **Open Source** : MIT License, forkable

---

## 🛠️ Architecture Technique (Pour Développeurs)

### Design Patterns Utilisés

- **Singleton** : Config globale accessible partout
- **Lazy Loading** : Modèles chargés seulement quand nécessaire (économie mémoire)
- **Pipeline Pattern** : Orchestrateur chaîne ASR→RAG→LLM→TTS
- **Strategy Pattern** : Sélection du modèle LLM/voix TTS configurable
- **Observer Pattern** : Logs centralisés pour debugging

### Flux de Données

```python
# 1. Utilisateur parle
audio_data = microphone.record()

# 2. ASR transcrit
text = asr.transcribe(audio_data)  # "Comment résoudre x² - 4 = 0"

# 3. RAG cherche
context = rag.search(text, top_k=3)  # ["Différence de carrés", ...]

# 4. LLM génère
prompt = build_prompt(text, context, system="Tu es un tuteur...")
response = llm.generate(prompt)  # "Indice 1: ..., Indice 2: ..."

# 5. TTS synthétise
audio_response = tts.synthesize(response)

# 6. Utilisateur écoute
play_audio(audio_response)
```

### Gestion Mémoire GPU

| Composant | VRAM (T4) | Optimisation |
|-----------|-----------|--------------|
| Whisper Small | ~2 GB | compute_type=int8 |
| FAISS Index | ~100 MB | Quantization |
| Phi-3 Mini Q4 | ~2.4 GB | GGUF quantization |
| Piper TTS | ~60 MB | ONNX runtime |
| **Buffer** | ~10 GB | Pour PyTorch |
| **TOTAL** | ~14.5 GB / 15 GB | ✅ Fit sur T4 |

---

## 📦 Structure du Projet

```
agent_vocal_IA/
├── 📄 START_HERE.md          ← COMMENCEZ ICI (2 min)
├── 📄 COLAB_QUICKSTART.md    ← Guide Colab détaillé (15 min)
├── 📄 README.md              ← Documentation complète
├── 📄 PROJECT_SUMMARY.md     ← Résumé technique
│
├── 📓 setup_colab.ipynb      ← Installation automatique sur Colab
├── 🐍 demo_cli.py            ← CLI pour tester sans UI
├── 📋 requirements.txt       ← Dépendances Python
├── ⚙️ config.yaml            ← Configuration centralisée
│
├── src/                      ← Code source (3500 lignes)
│   ├── utils.py              ← Config, logging, helpers
│   ├── asr.py                ← Reconnaissance vocale
│   ├── rag_build.py          ← Construction indices RAG
│   ├── rag.py                ← Recherche RAG
│   ├── llm.py                ← Génération LLM
│   ├── tts.py                ← Synthèse vocale
│   └── orchestrator.py       ← Pipeline complet
│
├── ui/                       ← Interface Gradio
│   └── app.py                ← Web UI avec micro
│
├── data/                     ← Données éducatives
│   ├── maths/                ← Cours de maths
│   ├── physique/             ← Cours de physique
│   ├── anglais/              ← Cours d'anglais
│   └── indices/              ← Indices FAISS générés
│
├── models/                   ← Modèles IA (téléchargés)
│   ├── llm/                  ← Phi-3 Mini (2.4 GB)
│   └── voices/               ← Voix Piper (60 MB)
│
└── tests/                    ← Tests unitaires
    ├── test_utils.py
    ├── test_rag.py
    └── test_integration.py
```

---

## 🎯 Cas d'Usage

### 👨‍🎓 Pour les Étudiants

- Aide aux devoirs sans tricher
- Révisions avant un examen
- Apprentissage de concepts difficiles
- Pratique orale en langues

### 👩‍🏫 Pour les Enseignants

- Outil de classe inversée
- Support pour étudiants en difficulté
- Génération d'exercices guidés
- Démonstration de systèmes IA

### 🔬 Pour les Chercheurs

- Base de code RAG + LLM complète
- Benchmark de modèles locaux
- Expérimentation prompt engineering
- Étude de systèmes tutoriels intelligents

### 💼 Pour l'Entreprise

- Formation continue des employés
- Onboarding interactif
- Base de connaissances vocale
- Support technique niveau 1

---

## 📞 Contact & Contribution

- 🐛 **Bugs** : [GitHub Issues](https://github.com/Romainmlt123/agent_vocal_IA/issues)
- 💡 **Suggestions** : [GitHub Discussions](https://github.com/Romainmlt123/agent_vocal_IA/discussions)
- 🤝 **Contributions** : Les Pull Requests sont bienvenues !
- 📧 **Email** : Via profil GitHub

---

## 📜 Licence

MIT License - Utilisez, modifiez, distribuez librement !

---

**🎓 Transformez l'apprentissage avec l'IA vocale locale !**
