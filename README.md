# 🫀 ECG Classification Platform

Application web permettant de classifier des signaux ECG en **Normal** ou **Infarctus** à l’aide de modèles de Deep Learning (MLP, CNN, LSTM), déployés via une architecture conteneurisée avec Docker.

---

## 🚀 Lancer le projet

### Sous Linux / macOS

chmod +x go.sh
./go.sh

### Alternative

docker compose up --build

---

## 🌐 Accès

http://localhost:8081

---

## ✨ Fonctionnalités

* Sélection du modèle : MLP / CNN / LSTM
* Classification d’un signal ECG (96 points)
* Prédiction : Normal vs Infarctus
* Score de confiance associé
* Visualisation du signal ECG
* Import de fichiers .csv / .tsv pour analyse batch
* Interface web moderne

---

## 🧪 Utilisation

### Saisie manuelle

Entrer 96 valeurs séparées par des virgules, puis lancer la classification.

### Import de fichier

Importer un fichier .csv ou .tsv, puis analyser les données.

---

## 🏗️ Architecture

* Backend : Spring Boot
* Service IA : Python (TensorFlow / Keras)
* Communication : API REST
* Orchestration : Docker Compose

Architecture en microservices :

* 1 conteneur Java (interface + API)
* 1 conteneur Python (inférence des modèles)

---

## 🧠 Modèles utilisés

* MLP (Multi-Layer Perceptron)
* CNN 1D
* LSTM

Comparaison des modèles réalisée sur le dataset ECG200.

---

## 🐳 Déploiement

Projet entièrement conteneurisé :

* reproductible
* portable
* lancement en une commande

---

## 📌 Résultat

Le système retourne :

* une classe prédite (Normal / Infarctus)
* une probabilité associée

---

## 🛠️ Stack technique

* Java (Spring Boot)
* Python (TensorFlow, Keras, scikit-learn)
* Docker / Docker Compose
* HTML / CSS / JavaScript

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre d’un projet Deep Learning.
