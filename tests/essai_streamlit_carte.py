import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import requests
from shapely.geometry import shape

# Initialisation de l'état de session
if 'show_second_map' not in st.session_state:
    st.session_state.show_second_map = False

if 'show_third_map' not in st.session_state:
    st.session_state.show_third_map = False

# Charger les données geojson en cache
@st.cache_data
def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Fonction pour supprimer les points des geojsons
def filter_non_point_features(geojson_data):
    geojson_data['features'] = [feature for feature in geojson_data['features'] if feature['geometry']['type'] != 'Point']
    return geojson_data

# Charger les données depuis les fichiers
dep = load_geojson("donnees/dep.geojson")

# Parcourir les features pour calculer le centroïde
for feature in dep['features']:
    geom = shape(feature['geometry'])
    centroid = geom.centroid
    feature['properties']['centroid'] = {
        'latitude': centroid.y,
        'longitude': centroid.x
    }

st.title("Carte interactive")

if not st.session_state.show_second_map and not st.session_state.show_third_map:
    # Affichage de la première carte
    m = folium.Map(location=[46.232192999999995, 2.209666999999996], zoom_start=5)

    folium.GeoJson(
        dep,
        tooltip=folium.GeoJsonTooltip(
            fields=['code', 'nom'],
            aliases=['Code:', 'Nom:'],
            style=("""
                background-color: white;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """),
            sticky=True
        ),
        style_function=lambda x: {
            'color': 'transparent',
            'weight': 0,
            'fillOpacity': 0,
        }
    ).add_to(m)

    folium.LayerControl().add_to(m)
    output = st_folium(m, width=700, height=500)

    # récupération des infos du clic
    if output and output.get("last_object_clicked"):
        dep_clic = output.get("last_object_clicked_tooltip").split(' ')[24].strip()
        st.session_state.dep_clic = dep_clic
        st.session_state.show_second_map = True
        st.rerun()

elif st.session_state.show_second_map and not st.session_state.show_third_map:
    # Affichage de la deuxième carte
    dep_clic = st.session_state.dep_clic
    st.write(f"Département sélectionné : {dep_clic}")

    link_communes = f'https://geo.api.gouv.fr/departements/{dep_clic}/communes?format=geojson&geometry=contour&fields=code,nom,contour,centre,codeDepartement,departement,codeRegion,region'
    communes_api = requests.get(link_communes).json()
    communes = filter_non_point_features(communes_api)
    st.session_state.communes = communes

    # Parcourir les features pour calculer le centroïde
    for feature in communes['features']:
        geom = shape(feature['geometry'])
        centroid = geom.centroid
        feature['properties']['centroid'] = {
            'latitude': centroid.y,
            'longitude': centroid.x
        }

    # Sélection du département
    dep_select = None
    centroid_select = None

    for feature in dep['features']:
        if str(feature['properties']['code']) == dep_clic:
            dep_select = feature
            st.session_state.dep_select = dep_select
            centroid_select = feature['properties']['centroid']
            break

    if centroid_select:
        location_centroid_dep_select = [centroid_select['latitude'], centroid_select['longitude']]

        # Génération de la nouvelle carte m2
        m2 = folium.Map(location=location_centroid_dep_select, zoom_start=9)

        # Ajouter le département sélectionné
        folium.GeoJson(
            dep_select,
            style_function=lambda x: {
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0,
            }
        ).add_to(m2)

        # Ajouter les communes
        folium.GeoJson(
            communes,
            tooltip=folium.GeoJsonTooltip(
                fields=['code', 'nom'],
                aliases=['Code:', 'Nom:'],
                style=("""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """),
                sticky=True
            ),
            style_function=lambda x: {
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0,
            }
        ).add_to(m2)

        
        folium.LayerControl().add_to(m2)
        output2 = st_folium(m2, width=700, height=500)

    # récupération des infos du clic
        if output2 and output2.get("last_object_clicked"):
            commune_clic = output2.get("last_object_clicked_tooltip").split(' ')[24].strip()
            st.session_state.commune_clic = commune_clic
            st.session_state.show_second_map = False
            st.session_state.show_third_map = True
            st.rerun()
else :
            
    # Affichage de la troisième carte
    commune_clic = st.session_state.commune_clic   
    communes = st.session_state.communes
    st.write(f"Commune sélectionnée : {commune_clic}")
    dep_select = st.session_state.dep_select

    for feature in communes['features']:
        if str(feature['properties']['code']) == commune_clic:
            commune_select = feature
            centroid_commune_select = feature['properties']['centroid']
            break

    if centroid_commune_select:
        location_centroid_commune_select = [centroid_commune_select['latitude'], centroid_commune_select['longitude']]
        m3 = folium.Map(location=location_centroid_commune_select, zoom_start=12)  
        # Ajouter le département sélectionné
        folium.GeoJson(
            dep_select,
            style_function=lambda x: {
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0,
            }
        ).add_to(m3)

        # Ajouter les communes
        folium.GeoJson(
            communes,
            tooltip=folium.GeoJsonTooltip(
                fields=['code', 'nom'],
                aliases=['Code:', 'Nom:'],
                style=("""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """),
                sticky=True
            ),
            style_function=lambda x: {
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0,
            }
        ).add_to(m3) 


    
    st_folium(m3, width=700, height=500)


    # Bouton pour revenir à la première carte
    if st.button("Retour à la carte de France"):
        st.session_state.show_second_map = False
        st.rerun()

