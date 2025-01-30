import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import requests
from shapely.geometry import shape
import pandas as pd
import branca


# Initialisation de l'état de session
if 'show_second_map' not in st.session_state:
    st.session_state.show_second_map = False

if 'show_third_map' not in st.session_state:
    st.session_state.show_third_map = False

if 'dep_clic' not in st.session_state:
    st.session_state.dep_clic = None

if 'qual_dep_last' not in st.session_state:
    st.session_state.qual_dep_last = None

if 'qual_dep_historique' not in st.session_state:
    st.session_state.qual_dep_historique = None

if 'communes' not in st.session_state:
    st.session_state.communes = None

if 'dep_select' not in st.session_state:
    st.session_state.dep_select = None

if 'commune_clic' not in st.session_state:  
    st.session_state.commune_clic = None

if 'commune_select' not in st.session_state:     
    st.session_state.commune_select = None

if 'location_IDF' not in st.session_state:
    st.session_state.location_IDF = None


# Charger les données geojson en cache
@st.cache_data
def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Fonction pour supprimer les points des geojsons
@st.cache_data
def filter_non_point_features(geojson_data):
    geojson_data['features'] = [feature for feature in geojson_data['features'] if feature['geometry']['type'] != 'Point']
    return geojson_data

# Fonction pour colorer les communes en fonction de la qualité de l'eau
@st.cache_data
def my_color_function(feature):
    if feature['properties']['Conclusion_Qualite']  == "Eau d'alimentation conforme aux exigences de qualité en vigueur pour l'ensemble des paramètres mesurés":
        return "green"
    elif feature['properties']['Conclusion_Qualite']  == "Eau d'alimentation conforme aux limites de qualité et non conforme aux références de qualité":
        return "orange"
    else:
        return "red"

# Charger les données depuis les fichiers
dep = load_geojson("donnees/dep_idf.geojson")

# Parcourir les features pour calculer le centroïde
for feature in dep['features']:
    geom = shape(feature['geometry'])
    centroid = geom.centroid
    feature['properties']['centroid'] = {
        'latitude': centroid.y,
        'longitude': centroid.x
    }

location_IDF = [dep['features'][1]['properties']['centroid']['latitude'], dep['features'][1]['properties']['centroid']['longitude']]
st.session_state.location_IDF = location_IDF
st.title("Carte interactive")

if not st.session_state.show_second_map and not st.session_state.show_third_map:
    location_IDF = st.session_state.location_IDF
    # Affichage de la première carte
    m = folium.Map(location=location_IDF, zoom_start=10)

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
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0,
        }
    ).add_to(m)

    folium.LayerControl().add_to(m)
    output = st_folium(m, width=700, height=500)

    # récupération des infos du clic
    if output and output.get("last_object_clicked"):
        dep_clic = output.get("last_object_clicked_tooltip").split(' ')[24].strip()
        st.session_state.dep_clic = dep_clic
        
        #Import données qualité eau du départemant
        dep_clic = st.session_state.dep_clic
        qual_dep_last = pd.read_csv(f'export/df_resultats_last_departement{dep_clic}.csv', sep=';')
        qual_dep_historique = pd.read_csv(f'export/df_resultats_historique_departement{dep_clic}.csv', sep=';')

    
        #stockage des infos dans l'état de session
        st.session_state.qual_dep_last = qual_dep_last
        st.session_state.qual_dep_historique = qual_dep_historique
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

    # Ajouter la qualité au GeoJSON
    qual_dep_last = st.session_state.qual_dep_last
    qual_dep_historique = st.session_state.qual_dep_historique
    for feature in communes['features']:
        communes_code = feature['properties']['code']
        if communes_code == str(qual_dep_last['code_commune'].iloc[0]):
            feature['properties']['Conclusion_Qualite'] = qual_dep_last['conclusion_conformite_prelevement'].iloc[0].strip().replace('.','')	
            feature['properties']['conformite_limites_bact_prelevement'] = qual_dep_last['conformite_limites_bact_prelevement'].iloc[0].strip().replace('.','')
            feature['properties']['conformite_limites_pc_prelevement'] = qual_dep_last['conformite_limites_pc_prelevement'].iloc[0].strip().replace('.','')
            feature['properties']['conformite_references_bact_prelevement'] = qual_dep_last['conformite_references_bact_prelevement'].iloc[0].strip().replace('.','')
            feature['properties']['conformite_references_pc_prelevement'] = qual_dep_last['conformite_references_pc_prelevement'].iloc[0].strip().replace('.','')


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
                'weight': 2,
                'fillOpacity': 0,
            }
        ).add_to(m2)

        # Ajouter les communes
        folium.GeoJson(
            communes,
            tooltip=folium.GeoJsonTooltip(
                fields=['code', 'nom'],
                aliases=['Code INSEE:', 'Nom:'],
                style=("""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """),
                sticky=True
            ),
            style_function=lambda x: {
                'fillColor': my_color_function(x),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.8,
            }
        ).add_to(m2)

        
        folium.LayerControl().add_to(m2)
        output2 = st_folium(m2, width=700, height=500)
        st.write(output2.get("last_object_clicked_tooltip"))

    # récupération des infos du clic
        if output2 and output2.get("last_object_clicked"):
            
            commune_clic = output2.get("last_object_clicked_tooltip").split(' ')[25].strip()
            
            st.session_state.commune_clic = commune_clic
            st.session_state.show_second_map = False
            st.session_state.show_third_map = True
            st.rerun()

        # Bouton pour revenir à la première carte
    if st.button("Retour à la carte de France"):
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.rerun()
else :
            
    # Affichage de la troisième carte
    commune_clic = st.session_state.commune_clic   
    communes = st.session_state.communes
    st.write(f"Commune sélectionnée : {commune_clic}")
    # dep_select = st.session_state.dep_select

    for feature in communes['features']:
        if str(feature['properties']['code']) == commune_clic:
            commune_select = feature
            centroid_commune_select = feature['properties']['centroid']
            break

    if centroid_commune_select:
        location_centroid_commune_select = [centroid_commune_select['latitude'], centroid_commune_select['longitude']]
        m3 = folium.Map(location=location_centroid_commune_select, zoom_start=11)  
        # # Ajouter le département sélectionné
        # folium.GeoJson(
        #     dep_select,
        #     style_function=lambda x: {
        #         'color': 'black',
        #         'weight': 1,
        #         'fillOpacity': 0,
        #     }
        # ).add_to(m3)

        # Ajouter les communes
        folium.GeoJson(
            communes,
            tooltip=folium.GeoJsonTooltip(
                fields=['code', 'nom'],
                aliases=['Code INSEE:', 'Nom:'],
                style=("""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """),
                sticky=True
            ),
            style_function=lambda x: {
                'fillColor': my_color_function(x),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.8,
            }
        ).add_to(m3) 

        for feature in communes['features']:
            centroid = feature['properties']['centroid']
            location = [centroid['latitude'], centroid['longitude']]
            nom_commune = feature['properties']['nom']
            code_commune = feature['properties']['code']
            
            if feature['properties'].get('Conclusion_Qualite') is not None:
                qualite_commune_last =feature['properties']['Conclusion_Qualite']
            else :
                qualite_commune_last = 'Pas de données'
            
            if feature['properties'].get('conformite_limites_bact_prelevement') is not None:
                conformite_limites_bact_prelevement =feature['properties']['conformite_limites_bact_prelevement']
            else :
                conformite_limites_bact_prelevement = 'Pas de données'
            
            if feature['properties'].get('conformite_limites_pc_prelevement') is not None:
                conformite_limites_pc_prelevement =feature['properties']['conformite_limites_pc_prelevement']
            else :
                conformite_limites_pc_prelevement = 'Pas de données'
            
            if feature['properties'].get('conformite_references_bact_prelevement') is not None:
                conformite_references_bact_prelevement =feature['properties']['conformite_references_bact_prelevement']
            else :
                conformite_references_bact_prelevement = 'Pas de données'
            
            if feature['properties'].get('conformite_references_pc_prelevement') is not None:
                conformite_references_pc_prelevement =feature['properties']['conformite_references_pc_prelevement']
            else : 
                conformite_references_pc_prelevement = 'Pas de données'

        html = f"""
        <h1> Nom commune : {nom_commune}</h1>
        <p> Code commune : {code_commune}</p><br>
        <h2>Qualité globale</h2>
        <p> {qualite_commune_last}</p>
        <h2>Conformité aux limites de qualité</h2>
        <p style="font-size:14px">Si les limites sont dépassées, il y a un risque pour la santé humaine</p>
        <p style="font-size:18px"> Conformité bactériologique : {conformite_limites_bact_prelevement}</p>
        <p style="font-size:18px"> Conformité chimique : {conformite_limites_pc_prelevement}</p>
        <h2>Conformité aux références de qualité</h2>
        <p style="font-size:14px">Si les références sont dépassées, il y a aucun risque pour la santé humaine mais cela met un évidence un disfonctionnement et peut entrainer des désagréments</p>
        <p style="font-size:18px"> Conformité bactériologique: {conformite_references_bact_prelevement}</p>
        <p style="font-size:18px"> Conformité chimique : {conformite_references_pc_prelevement}</p>
        
        
        """
        

        iframe = branca.element.IFrame(html=html, width=600, height=300)
        popup = folium.Popup(iframe, max_width=600)


        folium.Marker(location=location, popup=popup, icon=folium.Icon(color='purple', icon="info-sign")).add_to(m3)

        folium.LayerControl().add_to(m3)

    
    st_folium(m3, width=700, height=500)


    # Bouton pour revenir à la première carte
    if st.button("Retour à la carte de France"):
        st.session_state.show_second_map = False
        st.session_state.show_third_map = False
        st.rerun()
    # Bouton pour revenir à la deuxième carte
    if st.button("Retour à la carte du département"):
        st.session_state.show_second_map = True
        st.session_state.show_third_map = False
        st.rerun()
