# Immigration & Criminalité en France — Dashboard Streamlit

Tableau de bord interactif du mémoire de M1 ECAP — Marteret Achille (2024-2025).

## Structure du projet

```
.
├── app.py                    ← Application Streamlit
├── requirements.txt          ← Dépendances Python
├── departements.geojson      ← Contours des départements français
├── IRIS_FRANCE_METRO.csv     ← Données panel (immigration + criminalité 2006-2021)
└── README.md
```

> ⚠️ **Important** : les fichiers `departements.geojson` et `IRIS_FRANCE_METRO.csv`
> doivent être à la **racine du dépôt** (même dossier que `app.py`).

## Déploiement sur Streamlit Cloud (gratuit)

### 1. Créer un dépôt GitHub

```bash
git init
git add app.py requirements.txt departements.geojson IRIS_FRANCE_METRO.csv README.md
git commit -m "Initial commit"
git remote add origin https://github.com/<ton-user>/<ton-repo>.git
git push -u origin main
```

### 2. Déployer sur Streamlit Cloud

1. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte-toi avec GitHub.
2. Clique **"New app"**.
3. Sélectionne ton dépôt, la branche `main`, et le fichier `app.py`.
4. Clique **"Deploy"** — c'est tout !

L'URL publique sera de la forme :
`https://<ton-user>-<ton-repo>-app-xxxxx.streamlit.app`

## Lancement en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Données

- **Taux d'immigration** : estimations du recensement INSEE, échelle départementale.
- **Criminalité** : base « État 4001 » du Ministère de l'Intérieur / SSMSI (2014+).
- Période couverte : **2006–2021**.

## Méthode économétrique

Modèle en données de panel avec **effets fixes département et année** et erreurs standards
clusterisées. Équation estimée :

```
Y_dt = α + β·X_dt + γ_d + δ_t + ε_dt
```

## Référence principale

Alonso-Borrego, C., Garoupa, N., & Vázquez, P. (2012). Does immigration cause crime?
Evidence from Spain. *American Law and Economics Review*, 14(1), 165–191.
