<p align="center">
  <img src="./docs/images/logo.png" width="300">
</p>
<h1 align="center">AquaVision</h1>


# 📜 Contexte

Ce projet est une vraie aventure dans le monde des données ! Vous allez créer de A à Z votre propre application d’analyse de données. Le plus cool ? C’est VOUS qui choisissez votre sujet et vos sources de données.

L’idée est simple : vous êtes libre de laisser parler votre créativité sur le QUOI, pendant qu’on vous guide sur le COMMENT. Que vous visiez un projet purment professionnel ou qui joint le personnel, 
c’est l’occasion de développer des compétences concrètes sur un sujet qui vous tient à cœur !

---

# 📘 Objectifs pédagogiques


- Maîtriser les techniques de collecte de données à partir de différentes sources (APIs, fichiers, bases de données).
- Développer des compétences en prétraitement et nettoyage de données avec Python.
- Concevoir et implémenter un pipeline ETL.
- Gérer efficacement une base de données relationnelle.
- Créer des visualisations interactives et des tableaux de bord dynamiques.
- Explorer les possibilités d’enrichissement par l’intelligence artificielle.
- Privilégier une approche modulaire et évolutive
- Documenter régulièrement le code et les choix techniques
- Mettre en place des tests unitaires
- Utiliser le contrôle de version (git)
- Planifier des points d’étape réguliers
- Prévoir une phase de test utilisateur

---

# 📋 Missions et livrable attendus

- Scripts de collecte et d’extraction des données
- Pipeline de nettoyage et prétraitement
- Infrastructure ETL opérationnelle
- Base de données optimisée et documentée
- Tableaux de bord interactifs
- Interface utilisateur fonctionnelle et intuitive
- Documentation technique et guide utilisateur

---

# 🧠 Choix de sujet et approche en équipe

Notre projet a vu le jour grâce à Cynthia, membre de notre équipe, qui travaille dans une entreprise spécialisée dans l’étude des problématiques liées à l'eau. Désireuse de lier son domaine professionnel à notre projet d'analyse de données, 
elle a proposé de travailler sur un sujet en lien avec l'eau. Afin de rendre ce sujet accessible au plus grand nombre, nous avons décidé de nous concentrer sur un aspect concret et quotidien : la qualité de l'eau du réseau public, ainsi que son utilisation et son prix. 
Après plusieurs discussions, nous avons opté pour la création d'une application interactive. Cette application permettra aux utilisateurs de sélectionner une commune sur une carte et d'afficher instantanément les informations pertinentes concernant la qualité de l'eau dans cette région. 
En complément, nous avons envisagé une deuxième phase où nous pourrions collecter des données sur le prix de l'eau et les prélèvements.
Tout cela pourra être complété par un dashboard interactif présentant les données.

# 🛠️ Etapes de projet 

1. Récupération des données qualité de l'eau et géocoding grâce aux différentes APIs:
    - [hubeau](https://hubeau.eaufrance.fr/page/api-qualite-eau-potable)  
    - [adresses](https://adresse.data.gouv.fr/outils/api-doc/adresse)
    - [découpage administratif](https://geo.api.gouv.fr/decoupage-administratif/communes)

2. [Données sur le prix en open data](https://services.eaufrance.fr/pro/telechargement)
3. [Données sur les prélèvements](https://hubeau.eaufrance.fr/page/api-prelevements-eau)

4. Mise en place d'un script streamlit qui permet d'afficher une carte cliquable avec Folium

5. Exploration et nettoyage des données prix de l'eau:
    - [Exploration des données de prix](./docs/recherche/exploration.ipynb)
    - [Création d'une boucle de récupération des prix](./docs/recherche/boucle.ipynb)
    - [Création d'une base de données contenant les prélèvements et les prix](./docs/recherche/exploration2.ipynb)
    - [Exploration et préparation des données sur la qualité](prepa_donnees_qualite.ipynb)
    - [Exploration et préparation des données sur les prélèvements](code_df_api_hubeau.ipynb)
  
6. [Création d'un carte interactive et de fiches descriptives des communes](carte_eau_idf.py)

7. [Création d'un dashboard interactif des données nettoyées](./docs/images/dashboard_aquavision.png)


---

## 🏗️ Structure du dépôt
```
AquaVision/
├── .streamlit/                      # Fichier config.toml
├── dashboard/                       # Contient les fichiers utilisés pour réaliser le dashboard
    ├── images/                      # Toutes les images utilisées dans le dashboard
    ├── recherche/                   # Contient les noteboooks d'extraction et de traitement des données du dashboard
    ├── donnees/                     # Contient les données du dashboard assez légères pour y être intégrées
        ├── brutes/                  # Toutes les données telles qu'elles ont été récupérées 
        ├── nettoyees/               # Contient les données une fois qu'elles ont été travaillées
├── donnees_geo/                     # Contient les fichiers geojson utilisés dans le streamlit
├── export/                          # Contient les fichiers csv utilisés dans le streamlit
├── images/                          # Contient les images utilisés dans le streamlit
├── carte_eau_idf.py                 # Fichier streamlit
├── prepa_donnees_qualite.ipynb      # Transformation des données streamlit
├── code_df_api_hubeau.ipynb         # Extraction des données streamlit
├── requirements.txt                 # Fichier requirements pour le streamlit
├── LICENSE
└── README.md 


```


# 🔑 License

[**MIT**](./LICENSE)

