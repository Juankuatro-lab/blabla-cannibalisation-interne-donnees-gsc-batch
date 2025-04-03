import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Cannibalisation d'URLs",
    page_icon="🔍",
    layout="wide"
)

# Fonctions utilitaires
def create_download_link(df, filename):
    """Génère un lien de téléchargement pour un DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Télécharger {filename}</a>'
    return href

def load_data(file):
    """Charge les données à partir d'un fichier Excel ou CSV"""
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:  # Supposons que c'est un fichier Excel
        df = pd.read_excel(file)
    return df

def filter_dataframe(df, min_impressions=10):
    """Filtre le DataFrame pour éliminer les entrées avec trop peu d'impressions"""
    return df[df['impressions'] >= min_impressions]

def analyze_cannibalization(df, keyword):
    """Analyse la cannibalisation pour un mot-clé donné"""
    # Filtrer pour le mot-clé spécifique
    keyword_data = df[df['query'] == keyword].copy()
    
    if keyword_data.empty:
        return None, None
    
    # Grouper par URL et calculer le total des impressions
    url_impressions = keyword_data.groupby('page')['impressions'].sum().reset_index()
    total_impressions = url_impressions['impressions'].sum()
    
    # Calculer les pourcentages d'impressions
    url_impressions['percentage'] = (url_impressions['impressions'] / total_impressions * 100).round(2)
    url_impressions = url_impressions.sort_values('impressions', ascending=False).reset_index(drop=True)
    
    # Ajouter le rang
    url_impressions['rank'] = url_impressions.index + 1
    
    # Calculer le niveau de cannibalisation
    cannibalization_level = {
        'keyword': keyword,
        'total_urls': len(url_impressions),
        'total_impressions': total_impressions,
        'top_url_percentage': url_impressions.iloc[0]['percentage'] if not url_impressions.empty else 0,
        'cannibalization_score': 0
    }
    
    # Calculer le score de cannibalisation (plus c'est élevé, plus il y a de cannibalisation)
    if len(url_impressions) > 1:
        # Un score simple basé sur la distribution des impressions entre les URLs
        # Si une URL domine clairement (>95%), score faible
        # Si plusieurs URLs se partagent les impressions, score élevé
        top_url_pct = cannibalization_level['top_url_percentage']
        if top_url_pct > 95:
            cannibalization_level['cannibalization_score'] = 1  # Très faible
        elif top_url_pct > 80:
            cannibalization_level['cannibalization_score'] = 2  # Faible
        elif top_url_pct > 60:
            cannibalization_level['cannibalization_score'] = 3  # Modéré
        elif top_url_pct > 40:
            cannibalization_level['cannibalization_score'] = 4  # Élevé
        else:
            cannibalization_level['cannibalization_score'] = 5  # Très élevé
    
    return url_impressions, cannibalization_level

def get_all_keywords_cannibalization(df, min_impressions=10, min_urls=2):
    """Analyse la cannibalisation pour tous les mots-clés ayant plusieurs URLs"""
    # Filtrer les données pour les entrées avec au moins min_impressions
    filtered_df = filter_dataframe(df, min_impressions)
    
    # Compter le nombre d'URLs par mot-clé
    query_url_counts = filtered_df.groupby('query')['page'].nunique().reset_index()
    query_url_counts.columns = ['query', 'num_urls']
    
    # Filtrer pour ne garder que les mots-clés avec au moins min_urls URLs
    cannibalized_keywords = query_url_counts[query_url_counts['num_urls'] >= min_urls].sort_values('num_urls', ascending=False)
    
    # Calculer les statistiques pour chaque mot-clé cannibalisé
    results = []
    for keyword in cannibalized_keywords['query'].tolist():
        urls_data, stats = analyze_cannibalization(filtered_df, keyword)
        if stats:
            # Ajouter les URLs associées à ce mot-clé
            top_urls = urls_data['page'].tolist()
            stats['top_urls'] = top_urls  # Toutes les URLs
            stats['top_url'] = top_urls[0] if top_urls else ""  # URL principale
            stats['secondary_urls'] = top_urls[1:3] if len(top_urls) > 1 else []  # 2 URLs secondaires principales
            
            # Créer une chaîne avec les URLs principales pour l'affichage
            if len(top_urls) > 0:
                stats['urls_display'] = top_urls[0]
                if len(top_urls) > 1:
                    stats['urls_display'] += f" + {len(top_urls)-1} autre(s)"
            else:
                stats['urls_display'] = ""
                
            results.append(stats)
    
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('cannibalization_score', ascending=False)
        return results_df
    else:
        return pd.DataFrame()

# Interface utilisateur Streamlit
st.title("Analyse de Cannibalisation d'URLs")
st.markdown("""
Cet outil analyse les données GSC pour identifier et évaluer la cannibalisation entre URLs sur des mots-clés spécifiques.

**Cannibalisation**: Situation où plusieurs URLs de votre site apparaissent dans les résultats de recherche pour le même mot-clé.
""")

# Sidebar pour les contrôles
st.sidebar.header("Configuration")

# Upload de fichier
uploaded_file = st.sidebar.file_uploader("Importer un fichier GSC (Excel ou CSV)", type=['xlsx', 'csv'])

# Paramètres avancés
with st.sidebar.expander("Paramètres avancés"):
    min_impressions = st.number_input("Nombre minimal d'impressions", min_value=1, value=10)
    min_urls_for_cannibalization = st.number_input("Nombre minimal d'URLs pour considérer une cannibalisation", min_value=2, value=2)

# Initialiser le DataFrame
df = None

if uploaded_file is not None:
    # Charger les données
    df = load_data(uploaded_file)
    
    # Afficher les informations de base
    st.subheader("Aperçu des données")
    st.write(f"**Nombre total d'entrées:** {len(df)}")
    st.write(f"**Période:** {df['start_date'].min()} à {df['end_date'].max()}")
    st.write(f"**Nombre de mots-clés uniques:** {df['query'].nunique()}")
    st.write(f"**Nombre d'URLs uniques:** {df['page'].nunique()}")
    
    # Onglets pour différentes analyses
    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Analyse par mot-clé", "Export des données"])
    
    with tab1:
        st.header("Vue d'ensemble de la cannibalisation")
        
        # Filtrer pour les mots-clés avec cannibalisation
        all_cannibalization = get_all_keywords_cannibalization(df, min_impressions, min_urls_for_cannibalization)
        
        if not all_cannibalization.empty:
            # Afficher des statistiques globales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mots-clés cannibalisés", len(all_cannibalization))
            with col2:
                avg_score = all_cannibalization['cannibalization_score'].mean()
                st.metric("Score moyen de cannibalisation", f"{avg_score:.2f}/5")
            with col3:
                high_cannib = len(all_cannibalization[all_cannibalization['cannibalization_score'] >= 4])
                st.metric("Problèmes critiques", high_cannib)
            
            # Distribution des scores de cannibalisation
            st.subheader("Distribution des scores de cannibalisation")
            fig = px.histogram(all_cannibalization, x='cannibalization_score', 
                              labels={'cannibalization_score': 'Score de cannibalisation'},
                              title="Distribution des scores de cannibalisation",
                              nbins=5, color_discrete_sequence=['#ff6b6b'])
            fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
            st.plotly_chart(fig)
            
            # Top mots-clés cannibalisés
            st.subheader("Top 20 des mots-clés fortement cannibalisés")
            top_cannibalized = all_cannibalization.sort_values(['cannibalization_score', 'total_impressions'], 
                                                            ascending=[False, False]).head(20)
            
            fig = px.bar(top_cannibalized, x='keyword', y='total_impressions', 
                       color='cannibalization_score', color_continuous_scale='Reds',
                       hover_data=['total_urls', 'top_url_percentage'],
                       labels={
                           'keyword': 'Mot-clé',
                           'total_impressions': 'Impressions totales',
                           'cannibalization_score': 'Score de cannibalisation'
                       })
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
            
            # Tableau des mots-clés cannibalisés
            st.subheader("Tableau des mots-clés cannibalisés")
            display_df = all_cannibalization.copy()
            display_df['top_url_percentage'] = display_df['top_url_percentage'].round(2).astype(str) + '%'
            
            # Ajouter les colonnes d'URLs
            display_columns = ['keyword', 'total_urls', 'total_impressions', 
                              'top_url_percentage', 'cannibalization_score',
                              'top_url', 'urls_display']
            
            display_df = display_df[display_columns]
            display_df.columns = ['Mot-clé', 'Nombre d\'URLs', 'Impressions totales', 
                                '% URL principale', 'Score de cannibalisation', 
                                'URL principale', 'URLs en compétition']
            st.dataframe(display_df)
        else:
            st.info("Aucun mot-clé cannibalisé n'a été trouvé avec les critères actuels.")
    
    with tab2:
        st.header("Analyse par mot-clé spécifique")
        
        # Liste des mots-clés pour sélection
        keywords = sorted(df['query'].unique())
        selected_keyword = st.selectbox("Sélectionner un mot-clé à analyser", keywords)
        
        if selected_keyword:
            # Analyser la cannibalisation pour ce mot-clé
            urls_data, cannib_stats = analyze_cannibalization(df, selected_keyword)
            
            if urls_data is not None and not urls_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("URLs en compétition", len(urls_data))
                with col2:
                    st.metric("Impressions totales", int(cannib_stats['total_impressions']))
                with col3:
                    st.metric("% URL principale", f"{cannib_stats['top_url_percentage']:.2f}%")
                with col4:
                    score = cannib_stats['cannibalization_score']
                    score_text = {
                        0: "Aucune", 1: "Très faible", 2: "Faible", 
                        3: "Modérée", 4: "Élevée", 5: "Très élevée"
                    }.get(score, "N/A")
                    st.metric("Cannibalisation", f"{score_text} ({score}/5)")
                
                # Graphique de répartition des impressions
                st.subheader("Répartition des impressions par URL")
                
                # Tronquer les URLs pour l'affichage
                urls_data['display_url'] = urls_data['page'].apply(
                    lambda x: x.split('/')[-1] if x.endswith('/') else x.split('/')[-1]
                )
                
                fig = px.pie(urls_data, values='impressions', names='page',
                           title=f"Répartition des impressions pour le mot-clé '{selected_keyword}'",
                           hover_data=['percentage'])
                st.plotly_chart(fig)
                
                # Tableau détaillé
                st.subheader("Détails par URL")
                urls_data['percentage'] = urls_data['percentage'].astype(str) + '%'
                urls_data_display = urls_data[['rank', 'page', 'impressions', 'percentage']]
                urls_data_display.columns = ['Rang', 'URL', 'Impressions', 'Pourcentage']
                st.dataframe(urls_data_display)
                
                # Recommandations
                st.subheader("Analyse et recommandations")
                if score <= 1:
                    st.success("✅ Pas de problème de cannibalisation. Une URL domine clairement ce mot-clé.")
                elif score == 2:
                    st.info("ℹ️ Cannibalisation légère. Surveillez la situation mais pas d'action urgente requise.")
                elif score == 3:
                    st.warning("⚠️ Cannibalisation modérée. Considérez de consolider le contenu pour renforcer l'URL principale.")
                else:
                    st.error(f"🚨 Forte cannibalisation détectée! {len(urls_data)} URLs se disputent ce mot-clé.")
                    st.markdown("""
                    **Actions recommandées:**
                    1. Identifiez l'URL principale qui devrait cibler ce mot-clé
                    2. Redirigez les autres URLs ou modifiez leur contenu pour cibler des mots-clés différents
                    3. Utilisez la canonicalisation si nécessaire
                    """)
            else:
                st.info(f"Aucune donnée disponible pour le mot-clé '{selected_keyword}' avec les critères actuels.")
    
    with tab3:
        st.header("Export des données")
        
        # Option d'export pour l'analyse complète
        st.subheader("Export de l'analyse complète")
        all_cannibalization = get_all_keywords_cannibalization(df, min_impressions, min_urls_for_cannibalization)
        
        if not all_cannibalization.empty:
            # Ajouter une description du score de cannibalisation
            score_descriptions = {
                1: "Très faible", 2: "Faible", 3: "Modérée", 4: "Élevée", 5: "Très élevée"
            }
            all_cannibalization['description'] = all_cannibalization['cannibalization_score'].map(score_descriptions)
            
            # Renommer les colonnes pour l'export
            export_df = all_cannibalization.copy()
            
            # Ajouter une colonne pour les URLs secondaires (top 2 suivantes)
            export_df['URLs secondaires'] = export_df['secondary_urls'].apply(lambda x: ', '.join(x) if x else '')
            
            # Sélectionner et renommer les colonnes
            export_columns = ['keyword', 'total_urls', 'total_impressions', 
                             'top_url_percentage', 'cannibalization_score', 'description',
                             'top_url', 'URLs secondaires']
            
            export_df = export_df[export_columns]
            export_df.columns = ['Mot-clé', 'Nombre d\'URLs', 'Impressions totales', 
                               '% URL principale', 'Score (1-5)', 'Niveau de cannibalisation',
                               'URL principale', 'URLs secondaires']
            
            st.markdown(create_download_link(export_df, "analyse_cannibalisation.csv"), unsafe_allow_html=True)
            st.dataframe(export_df)
        else:
            st.info("Aucune donnée disponible pour l'export avec les critères actuels.")
        
        # Option d'export pour un mot-clé spécifique
        st.subheader("Export pour un mot-clé spécifique")
        export_keyword = st.selectbox("Sélectionner un mot-clé à exporter", sorted(df['query'].unique()), key="export_keyword")
        
        if export_keyword:
            urls_data, _ = analyze_cannibalization(df, export_keyword)
            if urls_data is not None and not urls_data.empty:
                export_detail_df = urls_data.copy()
                export_detail_df.columns = ['URL', 'Impressions', 'Pourcentage', 'Rang']
                
                st.markdown(create_download_link(export_detail_df, f"cannibalisation_{export_keyword.replace(' ', '_')}.csv"), unsafe_allow_html=True)
                st.dataframe(export_detail_df)
            else:
                st.info(f"Aucune donnée disponible pour le mot-clé '{export_keyword}' avec les critères actuels.")
else:
    # Afficher des instructions si aucun fichier n'est chargé
    st.info("Veuillez importer un fichier GSC (Excel ou CSV) pour commencer l'analyse.")
    
    # Image d'exemple ou explication supplémentaire
    st.markdown("""
    ### Comment utiliser cet outil
    
    1. Importez votre fichier d'extraction GSC (format Excel ou CSV)
    2. Ajustez les paramètres selon vos besoins
    3. Explorez les onglets pour analyser la cannibalisation
    4. Exportez les résultats pour une analyse plus approfondie
    
    ### Comprendre la cannibalisation
    
    La cannibalisation se produit lorsque plusieurs pages de votre site se positionnent sur le même mot-clé, 
    ce qui peut diluer votre autorité et nuire à votre positionnement global. L'outil calcule un score de 
    cannibalisation de 1 à 5 :
    
    - **1** : Très faible (une URL domine à >95%)
    - **2** : Faible (URL principale entre 80-95%)
    - **3** : Modérée (URL principale entre 60-80%)
    - **4** : Élevée (URL principale entre 40-60%)
    - **5** : Très élevée (aucune URL ne domine clairement)
    """)

# Ajouter des notes de bas de page
st.markdown("---")
st.markdown("Développé pour l'analyse SEO avancée | Données sources : Google Search Console")
