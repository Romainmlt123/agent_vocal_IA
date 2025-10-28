# 🚀 Démarrage Rapide sur Google Colab

## 📌 3 Minutes pour lancer votre Agent Vocal IA

### Étape 1️⃣ : Ouvrir le Notebook

Cliquez sur ce bouton → [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Romainmlt123/agent_vocal_IA/blob/main/setup_colab.ipynb)

**OU** :
1. Allez sur [colab.research.google.com](https://colab.research.google.com/)
2. Menu "Fichier" → "Ouvrir un notebook"
3. Onglet "GitHub" → Collez `https://github.com/Romainmlt123/agent_vocal_IA`
4. Sélectionnez `setup_colab.ipynb`

---

### Étape 2️⃣ : Activer le GPU

**IMPORTANT** : Sans GPU, le système sera très lent !

1. Menu "Exécution" → "Modifier le type d'exécution"
2. Sélectionnez **"T4 GPU"** ou **"A100 GPU"** (si disponible)
3. Cliquez sur "Enregistrer"

**Vérification :**
```python
!nvidia-smi
```
Vous devez voir `Tesla T4` ou `A100` dans la sortie.

---

### Étape 3️⃣ : Exécuter TOUTES les Cellules

**Option automatique (Recommandée) :**
- Menu "Exécution" → "Tout exécuter"
- ⏳ Attendez ~10 minutes (téléchargements + installation)

**Option manuelle :**
- Exécutez chaque cellule une par une (Shift + Enter)

**Les cellules vont :**
1. ✅ Vérifier le GPU
2. ✅ Cloner le projet
3. ✅ Installer les dépendances (~5 min)
4. ✅ Télécharger les modèles IA (~3 min)
5. ✅ Construire les indices RAG (~2 min)
6. ✅ Vérifier l'installation
7. ✅ **Lancer l'interface vocale**

---

### Étape 4️⃣ : Utiliser l'Interface Vocale

Après la dernière cellule, vous verrez :

```
Running on public URL: https://xxxxxxxxxxxxx.gradio.live
```

**🎉 CLIQUEZ SUR CE LIEN !**

#### Dans l'interface :

1. **Autorisez le microphone** quand le navigateur le demande 🎤
2. **Sélectionnez une matière** : Mathématiques, Physique ou Anglais
3. **Cliquez sur le bouton 🎤** dans l'onglet "Mode Vocal"
4. **Parlez naturellement** :
   - "Comment résoudre une équation du second degré ?"
   - "Explique-moi la loi de Newton"
   - "How do you use the present perfect?"
5. **Attendez la transcription** (quelques secondes)
6. **Écoutez la réponse vocale** 🔊

---

## 🎯 Exemples de Questions

### 📐 Mathématiques (Français)
- "Je ne comprends pas le théorème de Pythagore"
- "Comment factoriser x carré plus 2x moins 3 ?"
- "C'est quoi une dérivée ?"

### ⚡ Physique (Français)
- "Explique-moi la loi d'Ohm"
- "Quelle est la différence entre énergie cinétique et potentielle ?"
- "Comment calculer une force ?"

### 🇬🇧 Anglais (Français ou Anglais)
- "When do we use the past perfect tense?"
- "Quelle est la différence entre 'do' et 'make' ?"
- "Comment conjuguer 'to be' au présent ?"

---

## ⚙️ Configuration (Optionnel)

Si vous voulez modifier les paramètres, éditez `config.yaml` :

```python
# Dans une cellule Colab
!nano config.yaml
```

**Paramètres utiles :**
- `llm.temperature` : Créativité (0.7 par défaut)
- `llm.max_tokens` : Longueur des réponses (512 par défaut)
- `asr.model` : Modèle Whisper (tiny/small/medium/large)
- `rag.top_k` : Nombre de documents récupérés (3 par défaut)

---

## ❓ Problèmes Fréquents

### 🔴 "No GPU available"
**Solution :** Activez le GPU (Étape 2)

### 🔴 "Module not found: faster_whisper"
**Solution :** Réexécutez la cellule d'installation :
```python
!pip install -q -r requirements.txt
```

### 🔴 "Model file not found"
**Solution :** Réexécutez la cellule de téléchargement des modèles (Cellule 3)

### 🔴 "Microphone not working"
**Solution :** 
- Autorisez l'accès micro dans votre navigateur
- Essayez un autre navigateur (Chrome recommandé)
- Utilisez le "Mode Texte" comme alternative

### 🔴 "Connection timeout" ou lien Gradio inaccessible
**Solution :**
- Le lien est temporaire (~72h)
- Relancez la dernière cellule pour générer un nouveau lien
```python
from ui.app import launch_ui
launch_ui(share=True)
```

---

## 🔄 Relancer l'Interface

Si vous fermez l'interface ou si le lien expire :

```python
# Dans une nouvelle cellule Colab
from ui.app import launch_ui
launch_ui(share=True)
```

Un nouveau lien public sera généré.

---

## 📊 Performances Attendues

| Composant | GPU T4 | GPU A100 |
|-----------|--------|----------|
| Transcription (10s audio) | ~2s | ~1s |
| Recherche RAG | <0.5s | <0.3s |
| Génération LLM (200 tokens) | ~10-15s | ~3-5s |
| Synthèse vocale | ~1s | ~0.5s |
| **TOTAL par question** | **~15-20s** | **~5-7s** |

---

## 💾 Sauvegarder Votre Travail

Les fichiers sur Colab sont **temporaires**. Pour sauvegarder :

### Option 1 : Télécharger les fichiers
```python
# Télécharger les indices RAG
from google.colab import files
!zip -r indices.zip data/indices/
files.download('indices.zip')
```

### Option 2 : Sauvegarder sur Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')

# Copier le projet
!cp -r /content/agent_vocal_IA /content/drive/MyDrive/
```

Prochaine fois, restaurez depuis Drive :
```python
!cp -r /content/drive/MyDrive/agent_vocal_IA /content/
%cd agent_vocal_IA
```

---

## 🎓 Pédagogie : Comprendre les Indices Progressifs

L'IA **ne donne JAMAIS la solution complète** ! Elle guide avec 3 niveaux :

**Exemple : "Résoudre x² - 4 = 0"**

```
🔹 Indice 1 (Léger) :
"Observe l'équation. Peux-tu identifier un produit remarquable ?"

🔹 Indice 2 (Moyen) :
"C'est une différence de carrés : a² - b² = (a-b)(a+b)"

🔹 Indice 3 (Fort) :
"Tu peux factoriser en (x-2)(x+2) = 0. Que se passe-t-il quand un produit vaut 0 ?"
```

**L'élève doit finaliser** : x = 2 ou x = -2

---

## 📞 Support

- 📖 Documentation complète : [README.md](README.md)
- 🐛 Problèmes : [GitHub Issues](https://github.com/Romainmlt123/agent_vocal_IA/issues)
- 💬 Questions : Ouvrez une discussion sur GitHub

---

## ✅ Checklist de Démarrage

- [ ] GPU T4 ou A100 activé
- [ ] Toutes les cellules exécutées sans erreur
- [ ] Modèles téléchargés (vérifier `models/llm/` et `models/voices/`)
- [ ] Indices RAG créés (vérifier `data/indices/`)
- [ ] Interface Gradio lancée (lien public affiché)
- [ ] Microphone autorisé dans le navigateur
- [ ] Première question testée avec succès

**🎉 Si toutes les cases sont cochées, vous êtes prêt à utiliser votre Agent Vocal IA !**

---

**Temps total estimé : 10-15 minutes** ⏱️
