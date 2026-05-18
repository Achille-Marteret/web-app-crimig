import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from sklearn.linear_model import LinearRegression

# ======================================= Configuration de la page ============================== #
st.set_page_config(
    page_title="Immigration & Criminalité en France",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================= CSS personnalisé ============================== #
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .definition-box {
        background-color: #f8f9fa;
        border-left: 4px solid #2E86AB;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #fff8f0;
        border-left: 4px solid #FFA500;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    div[data-testid="stTabs"] button {
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ======================================= Chargement des données ============================== #
@st.cache_data
@st.cache_data
def load_data():
    import os
    if os.path.exists("IRIS_FRANCE_METRO.xlsx"):
        df = pd.read_excel("IRIS_FRANCE_METRO.xlsx", engine="openpyxl")
    else:
        # Essaie virgule puis point-virgule
        try:
            df = pd.read_csv("IRIS_FRANCE_METRO.csv", sep=",", encoding="utf-8")
        except Exception:
            df = pd.read_csv("IRIS_FRANCE_METRO.csv", sep=";", encoding="utf-8")
    df['CODE_DEPT'] = df['CODDEP'].apply(lambda x: str(x).zfill(2) if str(x).isdigit() else str(x))
    return df

@st.cache_data
def load_geojson():
    with open("departements.geojson", encoding='utf-8') as f:
        return json.load(f)

df = load_data()
geojson_depts = load_geojson()
geojson_key = "code"

# ======================================= Constantes ============================== #
INDICATEURS_CRIME = {
    "taux_crime_cheques":        {"label": "Falsifications de chèques",                      "color": "#00008B"},
    "taux_crime_plaintes":       {"label": "Infractions signalées par les plaignants",        "color": "#FF0000"},
    "taux_crime_vols_vehicules": {"label": "Vols / dégradations sur véhicules",               "color": "#99ccff"},
    "taux_crime_stupefiants":    {"label": "Stupéfiants et auteurs",                          "color": "#6699cc"},
    "taux_crime_vols_victime":   {"label": "Vols sur des victimes",                           "color": "#8B0000"},
    "taux_crime_violences":      {"label": "Violences physiques et psychologiques graves",    "color": "#e37c7c"},
    "taux_crime_autres":         {"label": "Infractions diverses ('procédures')",             "color": "#FFA500"},
    "taux_crime_infractions_pub":{"label": "Infractions contre établissements publics/privés","color": "#DAA520"},
}

DEPT_NAMES = {
    '01':'Ain','02':'Aisne','03':'Allier','04':'Alpes-de-Haute-Provence','05':'Hautes-Alpes',
    '06':'Alpes-Maritimes','07':'Ardèche','08':'Ardennes','09':'Ariège','10':'Aube','11':'Aude',
    '12':'Aveyron','13':'Bouches-du-Rhône','14':'Calvados','15':'Cantal','16':'Charente',
    '17':'Charente-Maritime','18':'Cher','19':'Corrèze','2A':'Corse-du-Sud','2B':'Haute-Corse',
    '21':"Côte-d'Or",'22':"Côtes-d'Armor",'23':'Creuse','24':'Dordogne','25':'Doubs',
    '26':'Drôme','27':'Eure','28':'Eure-et-Loir','29':'Finistère','30':'Gard',
    '31':'Haute-Garonne','32':'Gers','33':'Gironde','34':'Hérault','35':'Ille-et-Vilaine',
    '36':'Indre','37':'Indre-et-Loire','38':'Isère','39':'Jura','40':'Landes',
    '41':'Loir-et-Cher','42':'Loire','43':'Haute-Loire','44':'Loire-Atlantique','45':'Loiret',
    '46':'Lot','47':'Lot-et-Garonne','48':'Lozère','49':'Maine-et-Loire','50':'Manche',
    '51':'Marne','52':'Haute-Marne','53':'Mayenne','54':'Meurthe-et-Moselle','55':'Meuse',
    '56':'Morbihan','57':'Moselle','58':'Nièvre','59':'Nord','60':'Oise','61':'Orne',
    '62':'Pas-de-Calais','63':'Puy-de-Dôme','64':'Pyrénées-Atlantiques','65':'Hautes-Pyrénées',
    '66':'Pyrénées-Orientales','67':'Bas-Rhin','68':'Haut-Rhin','69':'Rhône','70':'Haute-Saône',
    '71':'Saône-et-Loire','72':'Sarthe','73':'Savoie','74':'Haute-Savoie','75':'Paris',
    '76':'Seine-Maritime','77':'Seine-et-Marne','78':'Yvelines','79':'Deux-Sèvres','80':'Somme',
    '81':'Tarn','82':'Tarn-et-Garonne','83':'Var','84':'Vaucluse','85':'Vendée','86':'Vienne',
    '87':'Haute-Vienne','88':'Vosges','89':'Yonne','90':'Territoire de Belfort','91':'Essonne',
    '92':'Hauts-de-Seine','93':'Seine-Saint-Denis','94':'Val-de-Marne',"95":"Val-d'Oise"
}

df['NOM_DEPT'] = df['CODE_DEPT'].map(DEPT_NAMES)
years = sorted(df['ANNEES'].unique())

# ======================================= Fonctions de graphiques ============================== #

def make_crime_map(indicator, year):
    df_f = df[df['ANNEES'] == year][['CODE_DEPT', 'NOM_DEPT', indicator]].dropna()
    fig = px.choropleth(
        df_f,
        geojson=geojson_depts,
        locations='CODE_DEPT',
        featureidkey=f"properties.{geojson_key}",
        color=indicator,
        color_continuous_scale=["snow", "darkred"],
        hover_name='NOM_DEPT',
        hover_data={indicator: ':.2f', 'CODE_DEPT': False},
        labels={indicator: INDICATEURS_CRIME[indicator]['label']},
        title=f"{INDICATEURS_CRIME[indicator]['label']} — {year}"
    )
    fig.update_geos(center={"lat": 46.5, "lon": 2.5}, fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, dragmode=False, title_x=0.5, height=500)
    return fig


def make_immigration_map(selected_year):
    if selected_year == 'Toutes années':
        df_f = df[['CODE_DEPT','NOM_DEPT','TAUX_IMMIGRATION']].groupby(
            ['CODE_DEPT','NOM_DEPT']).mean().reset_index()
        title = "Taux moyen d'immigration (toutes années)"
    else:
        df_f = df[df['ANNEES'] == selected_year][['CODE_DEPT','NOM_DEPT','TAUX_IMMIGRATION']].dropna()
        title = f"Taux d'immigration — {selected_year}"
    fig = px.choropleth(
        df_f, geojson=geojson_depts,
        locations='CODE_DEPT', featureidkey=f"properties.{geojson_key}",
        color='TAUX_IMMIGRATION', color_continuous_scale=["snow","darkblue"],
        hover_name='NOM_DEPT',
        hover_data={'TAUX_IMMIGRATION':':.4f','CODE_DEPT':True},
        labels={'TAUX_IMMIGRATION':'Taux Immigration'}, title=title
    )
    fig.update_geos(center={"lat":46.5,"lon":2.5}, fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, dragmode=False, title_x=0.5, height=500)
    return fig


def make_crime_evolution(selected_indicator):
    fig = go.Figure()
    for ind, info in INDICATEURS_CRIME.items():
        df_e = df[['ANNEES', ind]].dropna().groupby('ANNEES')[ind].mean().reset_index()
        is_sel = ind == selected_indicator
        fig.add_trace(go.Scatter(
            x=df_e['ANNEES'], y=df_e[ind],
            mode='lines+markers', name=info['label'],
            line=dict(color=info['color'], width=4 if is_sel else 1.5,
                      dash='solid' if is_sel else 'dot'),
            marker=dict(size=8 if is_sel else 4),
            opacity=1.0 if is_sel else 0.7,
            hovertemplate=f"<b>{info['label']}</b><br>Année: %{{x}}<br>Taux: %{{y:.2f}}<extra></extra>"
        ))
    fig.update_layout(
        title="Évolution comparative de tous les indicateurs de criminalité",
        title_x=0.5, yaxis_title="Taux moyen", hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=40, l=60, r=40), height=420
    )
    return fig


def make_immigration_evolution(year_selected):
    df_e = df[['ANNEES','TAUX_IMMIGRATION']].dropna().groupby('ANNEES')['TAUX_IMMIGRATION'].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_e['ANNEES'], y=df_e['TAUX_IMMIGRATION'],
        mode='lines+markers', name="Taux d'immigration",
        line=dict(color='#2E86AB', width=3), marker=dict(size=6),
        hovertemplate="<b>Taux d'immigration</b><br>Année: %{x}<br>Taux: %{y:.2f}%<extra></extra>"
    ))
    if year_selected != 'Toutes années' and year_selected in df_e['ANNEES'].values:
        val = df_e[df_e['ANNEES'] == year_selected]['TAUX_IMMIGRATION'].iloc[0]
        fig.add_trace(go.Scatter(
            x=[year_selected], y=[val], mode='markers',
            name=f"Année sélectionnée ({year_selected})",
            marker=dict(size=14, color='red', symbol='diamond')
        ))
    fig.update_layout(
        title="Évolution du taux d'immigration moyen en France",
        title_x=0.5, xaxis_title="Année", yaxis_title="Taux d'immigration (%)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=40, l=60, r=40), height=420
    )
    return fig


def make_temporal_analysis(dept_code):
    dept_data = df[df['CODE_DEPT'] == dept_code].copy()
    dept_name = DEPT_NAMES.get(dept_code, dept_code)
    if dept_data.empty:
        fig = go.Figure()
        fig.add_annotation(text=f"Aucune donnée pour le département {dept_code}",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    imm = dept_data[['ANNEES','TAUX_IMMIGRATION']].dropna()
    fig.add_trace(go.Scatter(
        x=imm['ANNEES'], y=imm['TAUX_IMMIGRATION'],
        mode='lines+markers', name="Taux d'immigration",
        line=dict(color='#2E86AB', width=3), marker=dict(size=6),
        hovertemplate="<b>Taux d'immigration</b><br>Année: %{x}<br>%{y:.2f}%<extra></extra>"
    ), secondary_y=False)
    colors = ["#00008B","#FF0000","#99ccff","#6699cc","#8B0000","#e37c7c","#FFA500","#DAA520"]
    for i, (ind, info) in enumerate(INDICATEURS_CRIME.items()):
        if ind in dept_data.columns:
            cdata = dept_data[['ANNEES', ind]].dropna()
            if not cdata.empty:
                fig.add_trace(go.Scatter(
                    x=cdata['ANNEES'], y=cdata[ind],
                    mode='lines+markers', name=info['label'],
                    line=dict(color=colors[i % len(colors)], width=1.5, dash='dot'),
                    marker=dict(size=4),
                    hovertemplate=f"<b>{info['label']}</b><br>Année: %{{x}}<br>%{{y:.2f}}<extra></extra>"
                ), secondary_y=True)
    fig.update_xaxes(title_text="Année")
    fig.update_yaxes(title_text="Taux d'immigration (%)", secondary_y=False)
    fig.update_yaxes(title_text="Taux de criminalité (p. 100 000 hab.)", secondary_y=True)
    fig.update_layout(
        title=f"Évolution comparative — {dept_name} ({dept_code})",
        title_x=0.5, hovermode='x unified',
        margin=dict(t=80, b=40, l=60, r=60),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        height=600
    )
    return fig


def calculate_within_transformation(df_in, y_col, x_col):
    d = df_in.copy()
    dept_means = d.groupby('CODE_DEPT')[[y_col, x_col]].mean()
    year_means = d.groupby('ANNEES')[[y_col, x_col]].mean()
    global_means = d[[y_col, x_col]].mean()
    d = d.merge(dept_means, on='CODE_DEPT', suffixes=('', '_dm'))
    d = d.merge(year_means, on='ANNEES', suffixes=('', '_ym'))
    d[f'{y_col}_w'] = d[y_col] - d[f'{y_col}_dm'] - d[f'{y_col}_ym'] + global_means[y_col]
    d[f'{x_col}_w'] = d[x_col] - d[f'{x_col}_dm'] - d[f'{x_col}_ym'] + global_means[x_col]
    return d


def make_regression_plot(crime_indicator):
    df_c = df[[crime_indicator,'TAUX_IMMIGRATION','CODE_DEPT','ANNEES']].dropna()
    if len(df_c) < 10:
        fig = go.Figure()
        fig.add_annotation(text="Données insuffisantes", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig, None, None

    # Régression simple
    X_s = df_c['TAUX_IMMIGRATION'].values.reshape(-1,1)
    y_s = df_c[crime_indicator].values
    m_simple = LinearRegression().fit(X_s, y_s)

    # Régression effets fixes (within)
    dw = calculate_within_transformation(df_c, crime_indicator, 'TAUX_IMMIGRATION')
    X_w = dw['TAUX_IMMIGRATION_w'].values.reshape(-1,1)
    y_w = dw[f'{crime_indicator}_w'].values
    m_within = LinearRegression().fit(X_w, y_w)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Régression Linéaire Simple', 'Régression à Effets Fixes (Dépt.–Année)'),
        horizontal_spacing=0.1
    )
    # Scatter simple
    fig.add_trace(go.Scatter(
        x=df_c['TAUX_IMMIGRATION'], y=df_c[crime_indicator],
        mode='markers', showlegend=False,
        marker=dict(color='darkgrey', size=4, opacity=0.5)
    ), row=1, col=1)
    xr_s = np.linspace(df_c['TAUX_IMMIGRATION'].min(), df_c['TAUX_IMMIGRATION'].max(), 100)
    fig.add_trace(go.Scatter(
        x=xr_s, y=m_simple.predict(xr_s.reshape(-1,1)),
        mode='lines', name=f'Simple (β={m_simple.coef_[0]:.4f})',
        line=dict(color='black', width=2)
    ), row=1, col=1)
    # Scatter within
    fig.add_trace(go.Scatter(
        x=dw['TAUX_IMMIGRATION_w'], y=dw[f'{crime_indicator}_w'],
        mode='markers', showlegend=False,
        marker=dict(color='#377eb8', size=4, opacity=0.5)
    ), row=1, col=2)
    xr_w = np.linspace(dw['TAUX_IMMIGRATION_w'].min(), dw['TAUX_IMMIGRATION_w'].max(), 100)
    fig.add_trace(go.Scatter(
        x=xr_w, y=m_within.predict(xr_w.reshape(-1,1)),
        mode='lines', name=f'Effets fixes (β={m_within.coef_[0]:.4f})',
        line=dict(color='#e41a1c', width=2)
    ), row=1, col=2)
    fig.update_xaxes(title_text="Taux d'immigration (%)", row=1, col=1)
    fig.update_xaxes(title_text="Taux d'immigration (centré)", row=1, col=2)
    label = INDICATEURS_CRIME[crime_indicator]['label']
    fig.update_yaxes(title_text=label, row=1, col=1)
    fig.update_yaxes(title_text=f"{label} (centré)", row=1, col=2)
    fig.update_layout(
        title=f"Comparaison des méthodes de régression — {label}",
        title_x=0.5, height=520,
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
    )
    return fig, m_simple.coef_[0], m_within.coef_[0]


# ======================================= En-tête ============================== #
st.markdown('<p class="main-title">🗺️ Criminalité et Immigration en France</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyse par départements · 2006–2021 · Mémoire de M1 ECAP – Marteret Achille</p>',
            unsafe_allow_html=True)

with st.expander("ℹ️ À propos de ce tableau de bord", expanded=False):
    st.markdown("""
Ce tableau de bord interactif propose une analyse de l'impact de l'immigration sur différents
indicateurs de criminalité dans les départements français, de **2006 à 2021**.

Il se compose de **trois onglets** :
- **Carte Criminalité** : taux de criminalité pour 100 000 habitants par département et par année.
- **Carte Immigration** : taux d'immigration par département et par année.
- **Analyse Comparative** : évolution temporelle par département ou comparaison des méthodes de régression
  (régression linéaire simple vs. régression à effets fixes département-année).

---
**Taux d'immigration** : rapport entre le nombre d'immigrés et la population totale du département.
*taux = nombre d'immigrés / population totale*

**Taux de criminalité pour 100 000 hab.** : *taux = (infractions / population totale) × 100 000*

**Définition INSEE de l'immigré** : personne née étrangère à l'étranger et résidant en France.
La qualité d'immigré est permanente : un individu continue d'appartenir à la population immigrée
même s'il devient Français par acquisition.

Sources : [INSEE](https://www.insee.fr) · [Ministère de l'Intérieur / SSMSI](https://www.interieur.gouv.fr)
    """)

st.markdown("---")

# ======================================= Onglets ============================== #
tab1, tab2, tab3 = st.tabs(["🔴 Carte de la Criminalité", "🔵 Carte de l'Immigration", "📊 Analyse Comparative"])

# ─────────────── ONGLET 1 : Criminalité ─────────────── #
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        indicator_label = st.selectbox(
            "Indicateur de criminalité",
            options=list(INDICATEURS_CRIME.keys()),
            format_func=lambda k: INDICATEURS_CRIME[k]['label'],
            index=5,  # Violences par défaut
            key="crime_ind"
        )
    with col2:
        year_crime = st.selectbox("Année", options=years, index=len(years)-1, key="year_crime")

    st.plotly_chart(make_crime_map(indicator_label, year_crime), use_container_width=True)
    st.plotly_chart(make_crime_evolution(indicator_label), use_container_width=True)


# ─────────────── ONGLET 2 : Immigration ─────────────── #
with tab2:
    year_imm = st.selectbox(
        "Année",
        options=['Toutes années'] + list(years),
        index=0,
        key="year_imm"
    )
    st.plotly_chart(make_immigration_map(year_imm), use_container_width=True)
    st.plotly_chart(make_immigration_evolution(year_imm), use_container_width=True)


# ─────────────── ONGLET 3 : Analyse Comparative ─────────────── #
with tab3:
    analysis_type = st.radio(
        "Type d'analyse",
        options=["Évolution temporelle par département", "Comparaison des méthodes de régression"],
        horizontal=True
    )

    if analysis_type == "Évolution temporelle par département":
        dept_options = {f"{code} – {name}": code for code, name in sorted(DEPT_NAMES.items())}
        dept_label = st.selectbox("Département", options=list(dept_options.keys()),
                                  index=list(dept_options.keys()).index("75 – Paris"))
        dept_code = dept_options[dept_label]
        st.plotly_chart(make_temporal_analysis(dept_code), use_container_width=True)

    else:  # Régression
        reg_indicator = st.selectbox(
            "Indicateur de criminalité",
            options=list(INDICATEURS_CRIME.keys()),
            format_func=lambda k: INDICATEURS_CRIME[k]['label'],
            index=1,
            key="reg_ind"
        )
        fig_reg, beta_simple, beta_fe = make_regression_plot(reg_indicator)
        st.plotly_chart(fig_reg, use_container_width=True)

        if beta_simple is not None:
            c1, c2 = st.columns(2)
            direction_s = "↗ positive" if beta_simple > 0 else "↘ négative"
            direction_fe = "↗ positive" if beta_fe > 0 else "↘ négative"
            c1.metric("Coefficient β — Régression simple", f"{beta_simple:.4f}",
                      delta=f"Relation {direction_s}")
            c2.metric("Coefficient β — Effets fixes", f"{beta_fe:.4f}",
                      delta=f"Relation {direction_fe}")
            st.markdown("""
<div class="result-box">
<b>Interprétation :</b> La régression à effets fixes (département + année) contrôle les hétérogénéités
non observées constantes dans le temps (qualité des institutions locales, politiques d'intégration, etc.)
ainsi que les chocs communs à tous les départements (crises macroéconomiques, politiques nationales, pandémies).
Elle produit une estimation plus fiable de l'effet causal de l'immigration sur la criminalité.
</div>
""", unsafe_allow_html=True)

# ======================================= Pied de page ============================== #
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:0.85rem;'>"
    "Mémoire M1 Économétrie & Statistiques — Parcours Économétrie Appliquée · 2024-2025 · "
    "Auteur : Marteret Achille · Encadrant : Pistolesi Nicolas"
    "</p>",
    unsafe_allow_html=True
)