import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import branca
import plotly.express as pk
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Caching des données
@st.cache_data
def load_geojson(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:  # Ajouter encoding='utf-8'
        return json.load(f)


@st.cache_data
def filter_non_point_features(geojson):
    geojson['features'] = [f for f in geojson['features'] if f['geometry']['type'] != 'Point']
    return geojson

@st.cache_data
def my_color_function(qualite_generale):
    color_map = {
        "Conforme aux limites et aux références": "#10fb04",
        "Conforme aux limites dans le cadre d'une dérogation et conforme aux références": "#c3fb04",
        "Conforme aux limites dans le cadre d'une dérogation et non conforme aux références": "#e1fb04",
        "Conforme aux limites et non conforme aux références": "#8efb04",
        "Non conforme aux limites et conforme aux références": "#fbb804",
        "Non conforme aux limites et non conforme aux références": "#fb0f04"
    }
    return color_map.get(qualite_generale, "blue")

@st.cache_data
def color_texte_qualite(qualite):
    if qualite == "Conforme aux limites et aux références":
        color = "#10fb04"
    elif qualite == "Conforme aux limites dans le cadre d'une dérogation et conforme aux références":
        color = "#c3fb04"
    elif qualite == "Conforme aux limites dans le cadre d'une dérogation et non conforme aux références":
        color = "#e1fb04"
    elif qualite == "Conforme aux limites et non conforme aux références":
        color = "#8efb04"
    elif qualite == "Non conforme aux limites et conforme aux références":
        color = "#fbb804"
    elif qualite == "Non conforme aux limites et non conforme aux références":
        color = "#fb0f04"
    else:
        color = 'black'
    return color


@st.cache_data
def extract_coordinates(geometry):
    if geometry['type'] == 'Polygon':
        return geometry['coordinates'][0]
    elif geometry['type'] == 'MultiPolygon':
        return [coord for polygon in geometry['coordinates'] for coord in polygon[0]]
    else:
        return []


@st.cache_data
def calculate_centroid(coordinates):
    if not coordinates:
        return None
    x_sum = sum(coord[0] for coord in coordinates)
    y_sum = sum(coord[1] for coord in coordinates)
    count = len(coordinates)
    return [y_sum / count, x_sum / count]  # [latitude, longitude]


@st.cache_data
def historique_commune(df, commune):   
    # Filtrer les données pour la commune en cours
    data = df[df['code_commune'].astype(str) == str(commune)]
    
    # Vérifier si on a des données pour éviter une erreur
    if data.empty:
        return f"Aucune donnée pour la commune {commune}"
    
    # Vérifier les prélèvements "Non conformes aux limites"
    last_nc_lim = data[data['qualite_generale'].str.contains('Non conforme aux limites', na=False)]
    if not last_nc_lim.empty:
        date_nc_lim = last_nc_lim['date_prelevement'].max()
    else:
        date_nc_lim = "Jamais"

    # Vérifier les prélèvements "Non conformes aux références"
    last_nc_ref = data[data['qualite_generale'].str.contains('non conforme aux références', na=False)]
    if not last_nc_ref.empty:
        date_nc_ref = last_nc_ref['date_prelevement'].max()
    else:
        date_nc_ref = "Jamais"

    return date_nc_lim,date_nc_ref


@st.cache_data
def prix_commune(tarif_dep_2023, commune_clic):
    tarif_com_2023 = tarif_dep_2023[tarif_dep_2023['Code INSEE'] == int(commune_clic)]
    
    if pd.isna(tarif_com_2023['D102.0'].iloc[0]):
        prix_aep_com = "Non disponible"
    else:
        prix_aep_com = tarif_com_2023['D102.0'].iloc[0]
    
    if pd.isna(tarif_com_2023['D204.0'].iloc[0]):
        prix_ac_com = "Non disponible"
    else:
        prix_ac_com = tarif_com_2023['D204.0'].iloc[0]
    
    if pd.isna(tarif_com_2023['prix_total'].iloc[0]):
        prix_total_com = "Non disponible"
    else:
        prix_total_com = tarif_com_2023['prix_total'].iloc[0]  
    
    return prix_aep_com, prix_ac_com, prix_total_com


@st.cache_data
def graph_prix(dep, commune):
    tarif_dep = pd.read_csv(f'export/tarif_dep{dep}.csv', sep=";")
    tarif_com = tarif_dep[tarif_dep['Code INSEE']== int(commune)]
    # Création de la figure
    fig = go.Figure()

    # Ajouter plusieurs courbes
    fig.add_trace(go.Scatter(x=tarif_com['Année'], y=tarif_com['D102.0'], mode='lines', name='Prix Eau potable', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=tarif_com['Année'], y=tarif_com['D204.0'], mode='lines', name='Prix Assainissement', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=tarif_com['Année'], y=tarif_com['prix_total'], mode='lines', name='Prix total', line=dict(color='purple', dash='dot')))

    # Personnalisation
    fig.update_layout(
        title="Historique des prix",
        xaxis_title="Année",
        yaxis_title="Prix",
        template="plotly",  # Autres options : "plotly", "ggplot2", "seaborn", "plotly_dark", etc.
        legend=dict(title="Légende")
)
    return fig


@st.cache_data
def prelevement_com(dep,commune):
    prelevement_idf_dep = pd.read_csv(f"export/prelevement_idf{dep}.csv", sep=";")
    prelevement_com = prelevement_idf_dep[prelevement_idf_dep['Code INSEE'] == int(commune)]
    return prelevement_com



# Chargement des données
@st.cache_data
def load_all_data():
    dep = load_geojson("donnees_geo/dep_idf.geojson")
    for feature in dep['features']:
        coords = extract_coordinates(feature['geometry'])
        centroid = calculate_centroid(coords)
        if centroid:
            feature['properties']['centroid'] = {'latitude': centroid[0], 'longitude': centroid[1]}
    
    communes_data = {}
    for feature in dep['features']:
        code = feature['properties']['code']
        communes_data[code] = load_geojson(f"donnees_geo/communes_idf_{code}.geojson")
        for commune in communes_data[code]['communes']['features']:
            coords = extract_coordinates(commune['geometry'])
            centroid = calculate_centroid(coords)
            if centroid:
                commune['properties']['centroid'] = {'latitude': centroid[0], 'longitude': centroid[1]}
    
    return dep, communes_data

# Chargement initial des données
dep, communes_data = load_all_data()

# Initialisation de l'état de session
for key in ['show_second_map', 'show_third_map', 'dep_clic', 'qual_dep_last', 'qual_dep_historique', 
            'communes_idf_dep', 'dep_select', 'commune_clic', 'commune_select', 'location_IDF','show_details','prix_aep_com', 'prix_ac_com', 'prix_total_com' ]:
    if key not in st.session_state:
        st.session_state[key] = None
if "show_first_map" not in st.session_state:
    st.session_state.show_first_map = True

st.title("L'eau en Ile-de-France")

# Première carte (Région IDF)

if st.session_state.show_first_map :
    location_IDF = [dep['features'][1]['properties']['centroid']['latitude'], 
                    dep['features'][1]['properties']['centroid']['longitude']]
    m = folium.Map(location=location_IDF, zoom_start=8)

    folium.GeoJson(
        dep,
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom'],
            aliases=['Code:', 'Nom:'],
            style="background-color: white; border: 2px solid black; border-radius: 3px; box-shadow: 3px;",
            sticky=True
        ),
        style_function=lambda x: {'fillColor': 'grey', 'color': 'black', 'weight': 1, 'fillOpacity': 0.6}
    ).add_to(m)

    folium.LayerControl().add_to(m)
    output = st_folium(m, width=700, height=500)

    if output and output.get("last_object_clicked"):
        dep_clic = output.get("last_object_clicked_tooltip").split(' ')[24].strip()
        st.session_state.dep_clic = dep_clic
        st.session_state.qual_dep_historique = pd.read_csv(f'export/df_resultats_historique_departement{dep_clic}.csv', sep=';')

        st.session_state.show_first_map = False
        st.session_state.show_second_map = True  # Activation de la deuxième carte
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()


# Deuxième carte (Département)
elif st.session_state.show_second_map :
    dep_clic = st.session_state.dep_clic
    st.write(f"Département sélectionné : {dep_clic}")

    tarif_dep_2023 = pd.read_csv(f'export/tarif_dep{dep_clic}_2023.csv', sep=';')
    tarif_dep_2023["prix_total"] = pd.to_numeric(tarif_dep_2023["prix_total"], errors="coerce")
    # st.write(tarif_dep_2023)
    st.session_state.tarif_dep_2023 = tarif_dep_2023

    communes_idf_dep = communes_data[dep_clic]['communes']
    st.session_state.communes_idf_dep = communes_idf_dep

    dep_select = next(feature for feature in dep['features'] if feature['properties']['code'] == dep_clic)
    st.session_state.dep_select = dep_select
    location_centroid_dep_select = [dep_select['properties']['centroid']['latitude'], 
                                    dep_select['properties']['centroid']['longitude']]

    m2 = folium.Map(location=location_centroid_dep_select, zoom_start=10)

    folium.GeoJson(
        dep_select,
        style_function=lambda x: {'color': 'black', 'weight': 2, 'fillOpacity': 0}
    ).add_to(m2)

    folium.GeoJson(
        communes_idf_dep,
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom'],
            aliases=['Code INSEE:', 'Nom:'],
            style="background-color: white; border: 2px solid black; border-radius: 3px; box-shadow: 3px;",
            sticky=True
        ),
        style_function=lambda x: {
            'fillColor': my_color_function(x['properties'].get('qualite_generale')),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.8,
        }
    ).add_to(m2)



    folium.LayerControl().add_to(m2)
    output2 = st_folium(m2, width=700, height=500)

    if output2 and output2.get("last_object_clicked"):
        commune_clic = output2.get("last_object_clicked_tooltip").split(' ')[25].strip()
        st.session_state.commune_clic = commune_clic
        st.session_state.show_second_map = False
        st.session_state.show_third_map = True
        st.session_state.show_details = False
        st.rerun()

    if st.button("Retour à la carte de la région Ile-de-France"):
        st.session_state.show_first_map = True
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()

# Troisième carte (Commune)
elif not st.session_state.show_first_map and not st.session_state.show_second_map and st.session_state.show_third_map:
    commune_clic = st.session_state.commune_clic   
    communes_idf_dep = st.session_state.communes_idf_dep
    st.write(f"Commune sélectionnée : {commune_clic}")

    commune_select = next(feature for feature in communes_idf_dep['features'] if feature['properties']['code'] == commune_clic)
    st.session_state.commune_select = commune_select
    location_centroid_commune_select = [commune_select['properties']['centroid']['latitude'], 
                                        commune_select['properties']['centroid']['longitude']]


    tarif_dep_2023 = st.session_state.tarif_dep_2023
    tarif_com_2023 = tarif_dep_2023[tarif_dep_2023['Code INSEE']==int(commune_clic)]
    # st.write(tarif_com_2023 )
    # st.write(tarif_com_2023['D204.0'].iloc[0])
    prix_aep_com, prix_ac_com, prix_total_com = prix_commune(tarif_dep_2023,commune_clic)
    st.session_state.prix_aep_com = prix_aep_com
    st.session_state.prix_ac_com = prix_ac_com
    st.session_state.prix_total_com = prix_total_com




    # Affiche le contenu HTML

    # st.write(prix_aep_com, prix_ac_com, prix_total_com)
    
    # tarif_com_2023 = tarif_dep_2023[tarif_dep_2023['Code INSEE']==int(commune_clic)]
    
    # if tarif_com_2023['D102.0'].iloc[0] == 'nan' :
    #     prix_aep_com = "Non disponible"
    # else:
    #     prix_aep_com = tarif_com_2023['D102.0'].iloc[0]
    
    # if tarif_com_2023['D204.0'].iloc[0] == 'nan' :
    #     prix_ac_com = "Non disponible"
    # else:
    #     prix_cp_com = tarif_com_2023['D204.0'].iloc[0]
    
    # if tarif_com_2023['prix_total'].iloc[0] == 'nan' :
    #     prix_total_com = "Non disponible"
    # else:
    #     prix_total_com = tarif_com_2023['prix_total'].iloc[0]   
    
    # st.write(tarif_com_2023)
    
    
    m3 = folium.Map(location=location_centroid_commune_select, zoom_start=11)  

    folium.GeoJson(
        communes_idf_dep,
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom'],
            aliases=['Code INSEE:', 'Nom:'],
            style="background-color: white; border: 2px solid black; border-radius: 3px; box-shadow: 3px;",
            sticky=True
        ),
        style_function=lambda x: {
            'fillColor': my_color_function(x['properties'].get('qualite_generale')),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.8,
        }
    ).add_to(m3)
    # qualite = commune_select['properties'].get('qualite_generale', 'Non disponible')
    couleur = color_texte_qualite(commune_select['properties'].get('qualite_generale', 'Non disponible'))
    # st.write(couleur)
    # st.write(commune_select['properties'].get('qualite_generale', 'Non disponible'))
    # st.write(qualite)
    html = f"""
    <h1> Nom commune : {commune_select['properties']['nom']}</h1>
    <p> Code commune : {commune_select['properties']['code']}</p><br>
    <h2>Qualité globale</h2>
    <p style="font-size:18px; color: {couleur}";> {commune_select['properties'].get('qualite_generale', 'Non disponible')}</p>
    <p> Date du prélèvement : {commune_select['properties'].get('date_prelevement', 'Non disponible')[:10]}</p>
    <h2>Commentaire</h2>
    <p> {commune_select['properties'].get('com_qualite', 'Non disponible')}</p>
    <h2>Conformité aux limites de qualité</h2>
    <p style="font-size:14px">Si les limites sont dépassées, il y a un risque pour la santé humaine</p>
    <p style="font-size:18px"> Confor   mité bactériologique : {commune_select['properties'].get('conformite_limites_bact_prelevement', 'Non disponible')}</p>
    <p style="font-size:18px"> Conformité chimique : {commune_select['properties'].get('conformite_limites_pc_prelevement', 'Non disponible')}</p>
    <h2>Conformité aux références de qualité</h2>
    <p style="font-size:14px">Si les références sont dépassées, il y a aucun risque pour la santé humaine mais cela met un évidence un disfonctionnement et peut entrainer des désagréments</p>
    <p style="font-size:18px"> Conformité bactériologique: {commune_select['properties'].get('conformite_references_bact_prelevement', 'Non disponible')}</p>
    <p style="font-size:18px"> Conformité chimique : {commune_select['properties'].get('conformite_references_pc_prelevement', 'Non disponible')}</p>

    <h2>Prix de l'eau</h2>
    <p>Prix Eau potable : {prix_aep_com}</p>
    <p>Prix Assainissement : {prix_ac_com}</p>
    <p>Prix Total : {prix_total_com} (hors taxes et redevances)</p>

   
    """

    iframe = branca.element.IFrame(html=html, width=600, height=300)
    popup = folium.Popup(iframe, max_width=600)



    folium.Marker(location=location_centroid_commune_select, popup=popup, icon=folium.Icon(color='purple', icon="info-sign")).add_to(m3)

    folium.LayerControl().add_to(m3)

    output3 = st_folium(m3, width=700, height=500)

    if output3 and output3.get("last_object_clicked_tooltip"):
        commune_clic = output3.get("last_object_clicked_tooltip").split(' ')[25].strip()
        st.session_state.commune_clic = commune_clic
        # st.session_state.show_details = False  # Activer l'affichage des détails
        st.session_state.show_first_map = False
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.session_state.show_details = True
        st.rerun()

    if st.button("Voir les détails de la commune"):
        st.session_state.show_first_map = False
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.session_state.show_details = True
        st.rerun()

    if st.button("Retour à la carte de la région Ile-de-France"):
        st.session_state.show_first_map = False
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()

    if st.button("Retour à la carte du département"):
        st.session_state.show_first_map = False
        st.session_state.show_second_map = True
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()

elif st.session_state.show_details:
    dep_clic = st.session_state.dep_clic
    commune_clic = st.session_state.commune_clic
    st.write(f"## Détails de la commune : {commune_clic}")

    # Récupérer les données de la commune sélectionnée
    commune_select =  st.session_state.commune_select
    qual_dep_historique = st.session_state.qual_dep_historique
    date_nc_lim, date_nc_ref = historique_commune(qual_dep_historique, commune_clic)
    prix_aep_com = st.session_state.prix_aep_com
    prix_ac_com = st.session_state.prix_ac_com
    prix_total_com = st.session_state.prix_total_com


    graph = graph_prix(dep_clic, commune_clic)

    prelevement = prelevement_com(dep_clic, commune_clic)

    # st.write(commune_select)

    # Afficher les informations en Streamlit
    st.write(f"### 🏡 {commune_select['properties']['nom']}")
    st.write(f"📍 **Code INSEE:** {commune_select['properties']['code']}")
    
    qualite = commune_select['properties'].get('qualite_generale', 'Non disponible')
    couleur = color_texte_qualite(qualite)
    
    st.markdown(f"<h3 style='color: {couleur}'>💧 Qualité de l'eau : {qualite} 🚰</h3>", unsafe_allow_html=True)
    st.write(f"📅 **Dernier prélèvement :** {commune_select['properties'].get('date_prelevement', 'Non disponible')[:10]}")
    st.write(f"📝 **Commentaire :** {commune_select['properties'].get('com_qualite', 'Non disponible')}")

    # Afficher les historiques
    st.write(f"🚫 **Dernier prélèvement non conforme aux limites :** {date_nc_lim[:10]}")
    st.write(f"❗ **Dernier prélèvement non conforme aux références :** {date_nc_ref[:10]}")

    # Afficher les prix
    st.markdown(f"<h3 >💰 Prix de l'eau</h3>", unsafe_allow_html=True)
    st.write(f"💰 **Prix Eau potable :** {prix_aep_com} €")
    st.write(f"💰 **Prix Assainissement :** {prix_ac_com} €")
    st.write(f"💰 **Prix Total :** {prix_total_com} € (hors taxes et redevances)")
    st.plotly_chart(graph)


    # Afficher les prélèvements
    st.markdown(f"<h3 >💰 Prélèvement en eau sur la commune</h3>", unsafe_allow_html=True)
    st.write(prelevement)


    # Ajouter un bouton de retour à la carte
    if st.button("🔙 Retour à la carte des communes"):
        st.session_state.show_first_map = False
        st.session_state.show_second_map = False
        st.session_state.show_third_map = True
        st.session_state.show_details = False
        st.rerun()

    if st.button("Retour à la carte de la région Ile-de-France"):
        st.session_state.show_first_map = True
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()

    if st.button("Retour à la carte du département"):
        st.session_state.show_first_map = False
        st.session_state.show_second_map = True
        st.session_state.show_third_map = False
        st.session_state.show_details = False
        st.rerun()


