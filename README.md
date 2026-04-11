# Lancer le projet

docker compose up --build

# Ouvrir la page pour tester les modèles

http://localhost:8081

# Tester les modèles

Deux possibilités :

1) Saisie manuelle

- Entrer 96 valeurs séparées par des virgules
- Cliquer sur "Lancer la classification"

Exemple :

0.12,0.15,0.14,0.13,0.16,0.18,0.20,0.22,0.25,0.28,0.30,0.27,
0.24,0.20,0.18,0.15,0.12,0.10,0.08,0.06,0.05,0.04,0.03,0.02,
0.01,0.00,-0.01,-0.02,-0.03,-0.04,-0.05,-0.06,-0.05,-0.04,-0.03,-0.02,
0.00,0.02,0.05,0.10,0.18,0.30,0.45,0.60,0.75,0.90,1.00,0.85,
0.70,0.50,0.30,0.15,0.08,0.05,0.03,0.02,0.01,0.00,-0.01,-0.02,
-0.03,-0.02,-0.01,0.00,0.02,0.04,0.06,0.08,0.10,0.12,0.14,0.16,
0.18,0.20,0.22,0.24,0.26,0.28,0.30,0.28,0.26,0.24,0.22,0.20,
0.18,0.16,0.14,0.12,0.10,0.08,0.06,0.05,0.04,0.03,0.02,0.01

2) Import de fichier

- Importer un fichier .csv ou .tsv
- Cliquer sur "Analyser le fichier importé"

# Fonctionnalités

- Choix du modèle (MLP, CNN, LSTM)
- Analyse d’un signal ECG (96 valeurs)
- Prédiction (Normal / Infarctus)
- Score de confiance
- Analyse d’un fichier complet

# Architecture

- Backend : Spring Boot
- Service IA : Python (TensorFlow / Keras)
- Communication : API REST
- Déploiement : Docker Compose