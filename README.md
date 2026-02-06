# 📍 Geomapping des machines & programmes – MVP

## 🎯 Objectif du projet

Ce projet vise à développer un **outil de géolocalisation des machines** permettant de croiser, sur une carte unique, les informations issues de différents **programmes opérationnels** :

- CVA / CVAF  
- Inspections obligatoires  
- Product Improvement (PI) & Product Support
- Données machines et clients  

L’objectif principal est d’aider à la **préparation des interventions terrain**, en identifiant :
- les actions à réaliser chez un client donné
- les opportunités d’actions supplémentaires sur des machines proches géographiquement

👉 Le projet est conçu comme un **MVP évolutif**, basé **uniquement sur des imports Excel** (aucun appel API externe dans cette phase).

---

## 🧠 Principes clés (à respecter strictement)

- **Toute la logique métier est côté backend**
- **Le frontend est uniquement de l’affichage et de l’interaction**
- La **clé de jointure universelle est `serial_number`**
- Les données géographiques sont traitées via **PostGIS**
- Le projet doit rester **simple, lisible et maintenable**

---

## 🧱 Architecture globale
Excel (imports manuels)
↓
Backend FastAPI (Python)
↓
PostgreSQL + PostGIS
↓
API interne
↓
Frontend React + Leaflet


---

## 🧩 Données gérées (MVP)

### 1️⃣ Machines
- Numéro de série (`serial_number`)
- Client
- Latitude
- Longitude
- Site / zone

### 2️⃣ Programmes
- CVA / CVAF
- Inspections
- Product Improvement (PI)
- Product Support (PS)
- Remote Service

📌 Toutes les tables doivent référencer **`serial_number`**.

---

## 📥 Imports Excel

- Les données sont importées via des **fichiers Excel**
- Les imports doivent :
  - valider la présence des colonnes attendues
  - logger les erreurs ou lignes invalides
  - mettre à jour les données existantes (upsert)

⚠️ Les fichiers Excel ne doivent jamais être considérés comme fiables par défaut.

---

## 🗺️ Frontend – règles strictes

- Technologie : **React + TypeScript**
- Cartographie : **Leaflet (react-leaflet)**
- ❌ Aucune logique métier dans le frontend
- ✅ Le frontend consomme uniquement l’API backend

Fonctionnalités attendues :
- affichage des machines sur une carte
- filtres par statut / programme
- panneau de détail d’une machine (actions associées)

---

## 🧠 Logique métier (backend uniquement)

Exemples de règles métier :
- Calcul du statut global d’une machine (OK / Action / Urgent)
- Détection des actions en retard
- Recherche de machines dans un rayon géographique
- Agrégation des actions par client

---

##Frontend : Next.js (React) + Tailwind CSS (pour le design).

Composants UI : shadcn/ui (indispensable pour avoir des tableaux et des cartes magnifiques rapidement).

Cartographie : React Leaflet ou Mapbox.

Backend (API) : FastAPI (Python)

### Architecture Agent Ready
/Intervention-planner
├── /frontend (Next.js)
│   ├── /components       # Carte, Tableaux des machines, Sidebar
│   ├── /hooks            # Logique de récupération des données
│   └── /lib              # 
├── /backend (FastAPI)
│   ├── main.py           # Points d'entrée API
│   ├── processor.py      # Création de la base de donnée, gestion de l'import, logique Upsert
│   └── optimizer.py      # Algorithme de regroupement (Clustering)
└── global_rules.md       # Tes instructions pour Antigravity

### Environnement
-

---


## 📌 Règles de contribution

- Respecter la structure existante
- Ne pas introduire de logique métier côté frontend
- Commenter toute règle métier importante
- Privilégier la clarté à l’optimisation prématurée


