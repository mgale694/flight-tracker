import streamlit as st
import streamlit_folium as st_folium
import folium

def select_direction(options):
    """
    Streamlit component for selecting a direction.
    Returns the selected direction.
    """
    st.write("Select a direction to track flights:")
    direction = st.selectbox("Direction", options=list(options.keys()))
    return direction

def show_location_map(getLoc, translated_latlng, radius_m, radius_km):
    """
    Display a folium map with:
    - Opaque blue dot for real location
    - Opaque red dot for translated search center
    - Translucent red circle for search radius
    """
    st.subheader("Location Map")
    
    # Create a folium map centered at the real location
    m = folium.Map(location=[getLoc.latitude, getLoc.longitude], zoom_start=13)

    # Add opaque dot for real location
    folium.CircleMarker(
        location=[getLoc.latitude, getLoc.longitude],
        radius=8,
        color='#0033cc',
        fill=True,
        fill_color='#0033cc',
        fill_opacity=1.0,
        popup='Real Location'
    ).add_to(m)

    # Add opaque dot for translated location
    folium.CircleMarker(
        location=translated_latlng,
        radius=8,
        color='#e63946',
        fill=True,
        fill_color='#e63946',
        fill_opacity=1.0,
        popup='Search Center'
    ).add_to(m)

    # Add translucent circle for search radius
    folium.Circle(
        location=translated_latlng,
        radius=radius_m,
        color='#e63946',
        fill=True,
        fill_color='#e63946',
        fill_opacity=0.2,
        popup=f'Search Radius: {radius_km} km'
    ).add_to(m)

    st_folium.folium_static(m, width=700, height=500)
    st.write("Map: Blue = Real location, Red = Search center, Red translucent = Search radius")
