import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import branca

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

def extract_coordinates(geometry):
    if geometry['type'] == 'Polygon':
        return geometry['coordinates'][0]
    elif geometry['type'] == 'MultiPolygon':
        return [coord for polygon in geometry['coordinates'] for coord in polygon[0]]
    else:
        return []

def calculate_centroid(coordinates):
    if not coordinates:
        return None
    x_sum = sum(coord[0] for coord in coordinates)
    y_sum = sum(coord[1] for coord in coordinates)
    count = len(coordinates)
    return [y_sum / count, x_sum / count]  # [latitude, longitude]

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
        for commune in communes_data[code]['features']:
            coords = extract_coordinates(commune['geometry'])
            centroid = calculate_centroid(coords)
            if centroid:
                commune['properties']['centroid'] = {'latitude': centroid[0], 'longitude': centroid[1]}
    
    return dep, communes_data

# Chargement initial des données
dep, communes_data = load_all_data()

# Initialisation de l'état de session
for key in ['show_second_map', 'show_third_map', 'dep_clic', 'qual_dep_last', 'qual_dep_historique', 
            'communes_idf_dep', 'dep_select', 'commune_clic', 'commune_select', 'location_IDF']:
    if key not in st.session_state:
        st.session_state[key] = None

st.title("Carte interactive")

# Première carte (France)
if not st.session_state.show_second_map and not st.session_state.show_third_map:
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
        st.session_state.show_second_map = True
        st.rerun()


# Deuxième carte (Département)
elif st.session_state.show_second_map and not st.session_state.show_third_map:
    dep_clic = st.session_state.dep_clic
    st.write(f"Département sélectionné : {dep_clic}")

    communes_idf_dep = communes_data[dep_clic]
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
        st.rerun()

    if st.button("Retour à la carte de France"):
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.rerun()

# Troisième carte (Commune)
else:
    commune_clic = st.session_state.commune_clic   
    communes_idf_dep = st.session_state.communes_idf_dep
    st.write(f"Commune sélectionnée : {commune_clic}")

    commune_select = next(feature for feature in communes_idf_dep['features'] if feature['properties']['code'] == commune_clic)
    location_centroid_commune_select = [commune_select['properties']['centroid']['latitude'], 
                                        commune_select['properties']['centroid']['longitude']]

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

    html = f"""
    <h1> Nom commune : {commune_select['properties']['nom']}</h1>
    <p> Code commune : {commune_select['properties']['code']}</p><br>
    <h2>Qualité globale</h2>
    <p> {commune_select['properties'].get('qualite_generale', 'Non disponible')}</p>
    <h2>Commentaire</h2>
    <p> {commune_select['properties'].get('com_qualite', 'Non disponible')}</p>
    <h2>Conformité aux limites de qualité</h2>
    <p style="font-size:14px">Si les limites sont dépassées, il y a un risque pour la santé humaine</p>
    <p style="font-size:18px"> Conformité bactériologique : {commune_select['properties'].get('conformite_limites_bact_prelevement', 'Non disponible')}</p>
    <p style="font-size:18px"> Conformité chimique : {commune_select['properties'].get('conformite_limites_pc_prelevement', 'Non disponible')}</p>
    <h2>Conformité aux références de qualité</h2>
    <p style="font-size:14px">Si les références sont dépassées, il y a aucun risque pour la santé humaine mais cela met un évidence un disfonctionnement et peut entrainer des désagréments</p>
    <p style="font-size:18px"> Conformité bactériologique: {commune_select['properties'].get('conformite_references_bact_prelevement', 'Non disponible')}</p>
    <p style="font-size:18px"> Conformité chimique : {commune_select['properties'].get('conformite_references_pc_prelevement', 'Non disponible')}</p>
    """

    iframe = branca.element.IFrame(html=html, width=600, height=300)
    popup = folium.Popup(iframe, max_width=600)

    folium.Marker(location=location_centroid_commune_select, popup=popup, icon=folium.Icon(color='purple', icon="info-sign")).add_to(m3)

    folium.LayerControl().add_to(m3)

    output3 = st_folium(m3, width=700, height=500)

    if output3 and output3.get("last_object_clicked_tooltip"):
        commune_clic = output3.get("last_object_clicked_tooltip").split(' ')[25].strip()
        st.session_state.commune_clic = commune_clic
        st.session_state.show_second_map = False
        st.session_state.show_third_map = True
        st.rerun()

    if st.button("Retour à la carte de France"):
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.rerun()

    if st.button("Retour à la carte du département"):
        st.session_state.show_second_map = True
        st.session_state.show_third_map = False
        st.rerun()