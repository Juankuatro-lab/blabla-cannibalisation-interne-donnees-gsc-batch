# Outil d'Analyse de Cannibalisation d'URLs

Un outil Python basé sur Streamlit pour évaluer le niveau de cannibalisation entre plusieurs URLs sur un mot-clé à partir des données de Google Search Console.

## Description

Cet outil permet d'analyser les données d'impressions de Google Search Console pour identifier les cas où plusieurs URLs du même site sont en compétition pour le même mot-clé dans les résultats de recherche, ce qui est connu sous le nom de "cannibalisation".

L'application permet de :
- Charger un fichier CSV ou Excel contenant les données GSC
- Analyser la cannibalisation à l'échelle du site
- Examiner en détail la cannibalisation pour des mots-clés spécifiques
- Exporter les résultats pour une analyse plus approfondie

## Fonctionnalités

- **Vue d'ensemble** : Statistiques globales sur la cannibalisation à l'échelle du site
- **Analyse par mot-clé** : Exploration détaillée de la répartition des impressions entre différentes URLs pour un mot-clé spécifique
- **Score de cannibalisation** : Évaluation de la gravité de la cannibalisation sur une échelle de 1 à 5
- **Visualisations** : Graphiques interactifs pour faciliter l'analyse
- **Recommandations** : Suggestions automatiques basées sur le niveau de cannibalisation détecté
- **Export des données** : Téléchargement des résultats au format CSV

## Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/votre-utilisateur/analyse-cannibalisation-urls.git
cd analyse-cannibalisation-urls
```

2. Installez les dépendances requises :
```bash
pip install -r requirements.txt
```

3. Lancez l'application Streamlit :
```bash
streamlit run app.py
```

## Format des données d'entrée

L'outil attend un fichier CSV ou Excel avec au minimum les colonnes suivantes :
- `page` : L'URL de la page (chemin d'accès de la ressource)
- `query` : Le mot-clé recherché
- `impressions` : Le nombre d'affichages de l'URL pour ce mot-clé

Les autres colonnes comme `clicks`, `ctr` et `position` sont optionnelles mais peuvent être présentes dans le fichier.

## Utilisation

1. Importez votre fichier de données GSC (format Excel ou CSV)
2. Ajustez les paramètres dans la barre latérale selon vos besoins
3. Naviguez entre les onglets pour explorer différentes vues de l'analyse
4. Pour une analyse détaillée d'un mot-clé spécifique, sélectionnez-le dans l'onglet "Analyse par mot-clé"
5. Exportez les résultats via l'onglet "Export des données"

## Comprendre le score de cannibalisation

Le score de cannibalisation est calculé sur une échelle de 1 à 5 :

- **1 (Très faible)** : Une URL domine clairement (>95% des impressions)
- **2 (Faible)** : L'URL principale représente entre 80% et 95% des impressions
- **3 (Modérée)** : L'URL principale représente entre 60% et 80% des impressions
- **4 (Élevée)** : L'URL principale représente entre 40% et 60% des impressions
- **5 (Très élevée)** : Aucune URL ne domine clairement (<40% pour l'URL principale)

Plus le score est élevé, plus la cannibalisation est importante et nécessite une action corrective.

## Dépendances

- Python 3.7+
- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn
- NumPy

## Fichier requirements.txt

```
streamlit>=1.15.0
pandas>=1.3.0
plotly>=5.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
numpy>=1.20.0
openpyxl>=3.0.0
```

## Contribution

Les contributions à ce projet sont les bienvenues. N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
