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
elle a proposé de travailler sur un sujet en lien avec l'eau. Afin de rendre ce sujet accessible au plus grand nombre, nous avons décidé de nous concentrer sur un aspect concret et quotidien : la qualité de l'eau du réseau public. 
Après plusieurs discussions, nous avons opté pour la création d'une application interactive. Cette application permettra aux utilisateurs de sélectionner une commune sur une carte et d'afficher instantanément les informations pertinentes concernant la qualité 
de l'eau dans cette région. En complément, nous avons envisagé une deuxième phase où nous pourrions collecter des données sur le prix de l'eau courante et, éventuellement, utiliser des modèles de machine learning pour prédire son évolution à l'année suivante.

## 🛠️ Méthodologie  

1. Récupération des données qualité de l'eau et géocoding grâce aux différentes APIs:
  - [hubeau](https://hubeau.eaufrance.fr/page/api-qualite-eau-potable)  
  - [adresses](https://adresse.data.gouv.fr/outils/api-doc/adresse)
  - [découpage administratif](https://geo.api.gouv.fr/decoupage-administratif/communes)
2. [Données sur le prix en open data](https://services.eaufrance.fr/pro/telechargement)
3. Mise en place d'un script streamlit qui permet d'afficher une carte cliquable avec Folium
4. Exploration et nettoyage des données prix de l'eau

---

## 🏗️ Structure du dépôt
```
AquaVision/
├── docs/                   # Contient les documents non livrables et images
│   ├── images/             # Toutes les images utilisées dans les livrables
│   ├── recherche/          # Contient les documents non livrables

```


# 🔑 License

[**MIT**](./LICENSE)

