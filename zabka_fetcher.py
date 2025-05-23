import osmnx as ox
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

def fetch_zabka_shops_wroclaw():
    """
    Fetch all Żabka shops in Wrocław, Poland from OpenStreetMap
    and save them to an Excel file with longitude, latitude, name, and address columns.
    """
    
    # Define the place (Wrocław, Poland)
    place_name = "Wrocław, Poland"
    
    print(f"Fetching boundary for {place_name}...")
    
    try:
        # Get the boundary of Wrocław
        wroclaw_boundary = ox.geocode_to_gdf(place_name)
        print("✓ Successfully fetched Wrocław boundary")
    except Exception as e:
        print(f"Error fetching boundary: {e}")
        return
    
    # Define tags to search for Żabka shops
    # We'll search for various combinations that might identify Żabka stores
    tags = {
        'shop': 'convenience',
        'name': 'Żabka'
    }
    
    print("Searching for Żabka shops...")
    
    try:
        # Fetch POIs (points of interest) - this gets both nodes and ways
        pois = ox.features_from_place(place_name, tags)
        print(f"✓ Found {len(pois)} potential matches")
        
        # Filter for entries that actually contain "Żabka" in the name
        zabka_mask = pois['name'].astype(str).str.contains('Żabka|żabka', case=False, na=False)
        zabka_shops = pois[zabka_mask].copy()
        
        print(f"✓ Filtered to {len(zabka_shops)} Żabka shops")
        
        if len(zabka_shops) == 0:
            print("No Żabka shops found. Trying alternative search...")
            
            # Try a broader search
            alternative_tags = {'name': ['Żabka', 'żabka']}
            pois_alt = ox.features_from_place(place_name, alternative_tags)
            zabka_shops = pois_alt.copy()
            print(f"✓ Alternative search found {len(zabka_shops)} results")
        
        if len(zabka_shops) == 0:
            print("Still no results. Trying shop-specific search...")
            # One more attempt with just shop tag
            shop_tags = {'shop': True}
            all_shops = ox.features_from_place(place_name, shop_tags)
            zabka_mask = all_shops['name'].astype(str).str.contains('Żabka|żabka', case=False, na=False)
            zabka_shops = all_shops[zabka_mask].copy()
            print(f"✓ Shop-specific search found {len(zabka_shops)} Żabka shops")
        
    except Exception as e:
        print(f"Error fetching POI data: {e}")
        return
    
    if len(zabka_shops) == 0:
        print("No Żabka shops found in Wrocław. This might be due to:")
        print("1. Limited data in OpenStreetMap for this area")
        print("2. Different naming conventions in the database")
        print("3. Shops tagged differently than expected")
        return
    
    # Prepare data for Excel export
    shop_data = []
    
    print("Processing shop geometries...")
    
    for idx, shop in zabka_shops.iterrows():
        try:
            # Get the geometry
            geom = shop.geometry
            
            # Calculate centroid for both points and polygons
            if geom.geom_type == 'Point':
                lon, lat = geom.x, geom.y
            elif geom.geom_type in ['Polygon', 'MultiPolygon']:
                centroid = geom.centroid
                lon, lat = centroid.x, centroid.y
            else:
                # For other geometry types, try to get centroid
                centroid = geom.centroid
                lon, lat = centroid.x, centroid.y
            
            # Extract relevant information
            name = shop.get('name', 'Żabka')
            
            # Try to get address information in Polish format (street + house number)
            street = shop.get('addr:street', '')
            house_number = shop.get('addr:housenumber', '')
            
            if street and house_number:
                address = f"{street} {house_number}"
            elif street:
                address = street
            else:
                address = 'Adres niedostępny'
            
            shop_data.append({
                'geographical_longitude': lon,
                'geographical_latitude': lat,
                'address': address,
                'name': name
            })
            
        except Exception as e:
            print(f"Error processing shop {idx}: {e}")
            continue
    
    if not shop_data:
        print("No valid shop data could be processed.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(shop_data)
    
    # Sort by longitude for consistent ordering
    df = df.sort_values('geographical_longitude').reset_index(drop=True)
    
    print(f"✓ Processed {len(df)} shops successfully")
    
    # Save to Excel
    filename = 'zabka_shops_wroclaw.xlsx'
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✓ Data saved to {filename}")
        
        # Display summary
        print(f"\nSummary:")
        print(f"Total Żabka shops found: {len(df)}")
        print(f"Longitude range: {df['geographical_longitude'].min():.6f} to {df['geographical_longitude'].max():.6f}")
        print(f"Latitude range: {df['geographical_latitude'].min():.6f} to {df['geographical_latitude'].max():.6f}")
        
        # Show first few entries
        print(f"\nFirst 5 entries:")
        print(df.head().to_string(index=False))
        
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        print("Data collected successfully but couldn't save to file.")
        return df

def main():
    """Main function to run the Żabka shop fetcher"""
    print("Żabka Shop Fetcher for Wrocław, Poland")
    print("=" * 40)
    
    # Check if required packages are available
    try:
        import osmnx
        import pandas
        import openpyxl
        print("✓ All required packages available")
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install osmnx pandas openpyxl")
        return
    
    # Run the fetcher
    result = fetch_zabka_shops_wroclaw()
    
    if result is not None:
        print("\n✓ Program completed successfully!")
    else:
        print("\n✗ Program completed with issues.")

if __name__ == "__main__":
    main()
