import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# ✅ Ustawienie alternatywnego serwera Overpass
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"

# ✅ Nazwa miasta i pliku
city = "Wrocław, Poland"
output_file = "zabka_wroclaw.png"

# ✅ Pobranie granic miasta
gdf_boundary = ox.geocode_to_gdf(city)

# ✅ Pobranie grafu drogowego i wybór tylko najważniejszych ulic
graph = ox.graph_from_place(city, network_type='drive')
edges = ox.graph_to_gdfs(graph, nodes=False)

important_highways = ['motorway', 'trunk', 'primary', 'secondary','tertiary']
edges_major = edges[edges['highway'].apply(
    lambda x: any(hw in x if isinstance(x, list) else [x] for hw in important_highways)
)]

# ✅ Pobranie rzek
rivers = ox.features_from_place(city, tags={'waterway': 'river'})

# ✅ Pobranie sklepów Żabka (punkty i wielokąty)
tags = {"shop": "convenience", "name": "Żabka"}
zabka_raw = ox.features_from_place(city, tags=tags)

# Podział na punkty i wielokąty
zabka_points = zabka_raw[zabka_raw.geometry.type == 'Point'].copy()
zabka_polygons = zabka_raw[zabka_raw.geometry.type == 'Polygon'].copy()

# Centroidy wielokątów
zabka_polygons['geometry'] = zabka_polygons.centroid

# Połączenie w jedną warstwę punktową
zabka_combined = gpd.GeoDataFrame(
    pd.concat([zabka_points, zabka_polygons], ignore_index=True),
    crs=zabka_raw.crs
)

# ✅ Rysowanie mapy
fig, ax = plt.subplots(figsize=(12, 12), facecolor='black')
gdf_boundary.plot(ax=ax, facecolor='black', edgecolor='none')

edges_major.plot(ax=ax, linewidth=0.8, edgecolor='gray')     # Ulice
rivers.plot(ax=ax, color='blue', linewidth=1)                # Rzeki
zabka_combined.plot(ax=ax, markersize=10, color='lime', label='Żabka', alpha=0.9)  # Sklepy

# Styl
ax.set_facecolor('black')
ax.set_title("Sklepy Żabka we Wrocławiu", fontsize=18, color='white', pad=20)
ax.legend(facecolor='black', edgecolor='white', labelcolor='white', loc='lower left')
ax.set_axis_off()

# ✅ Zapis do pliku
plt.tight_layout()
plt.savefig(output_file, dpi=300, facecolor='black', bbox_inches='tight')
plt.close()

print(f"✅ Mapa zapisana do pliku: {output_file}")
