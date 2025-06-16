import streamlit as st
import pandas as pd
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from twilio.rest import Client
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import networkx as nx

AUTH_CREDENTIALS = {"admin": "pass"}

EMAIL_SENDER = "srushti.22211386@viit.ac.in"
EMAIL_PASSWORD = "eida xufl uhme yytb"



DATA_FILE_PATH = r"C:\Users\HP\Machine Learning Project\Complete\data\real_time_india_earthquakes_with_states.csv"
EMAIL_FILE_PATH = r"C:\Users\HP\Machine Learning Project\Complete\data\users.xlsx"
SUPPLY_INVENTORY_PATH = r"C:\Users\HP\Machine Learning Project\Complete\data\inventory.csv"
RESOURCE_CENTERS_PATH = r"C:\Users\HP\Machine Learning Project\Complete\data\resource_centers.csv"

def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    st.sidebar.title("Authority Login")
    
    if st.session_state.authenticated:
        st.sidebar.success("🔓 Logged in as Admin")
        if st.sidebar.button("Logout 🚪"):
            st.session_state.authenticated = False
            st.sidebar.warning("You have been logged out.")
            st.rerun()
        return True

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in AUTH_CREDENTIALS and AUTH_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.sidebar.success("✅ Login successful!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials. Try again.")
    
    return st.session_state.authenticated

def load_data():
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        st.success("✅ File Loaded Successfully!")
        
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert(None)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=100)
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        
        return df, start_date, end_date
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame(), None, None

def load_inventory_data():
    try:
        if os.path.exists(SUPPLY_INVENTORY_PATH):
            inventory_df = pd.read_csv(SUPPLY_INVENTORY_PATH)
        else:
            inventory_df = pd.DataFrame({
                'state': ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Himachal Pradesh'],
                'water_units': [500, 300, 400, 600, 350],
                'food_kits': [300, 200, 250, 400, 200],
                'medicine_kits': [200, 150, 180, 250, 150],
                'shelter_units': [100, 80, 90, 120, 70],
                'last_updated': [datetime.now().strftime('%Y-%m-%d')] * 5
            })
            inventory_df.to_csv(SUPPLY_INVENTORY_PATH, index=False)
        return inventory_df
    except Exception as e:
        st.error(f"❌ Error loading inventory: {e}")
        return pd.DataFrame()

def load_resource_centers():
    try:
        if os.path.exists(RESOURCE_CENTERS_PATH):
            centers_df = pd.read_csv(RESOURCE_CENTERS_PATH)
        else:
            centers_df = pd.DataFrame({
                'center_id': range(1, 11),
                'state': ['Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Himachal Pradesh', 
                          'Delhi', 'Punjab', 'Assam', 'Maharashtra', 'Himachal Pradesh'],
                'latitude': [28.7041, 31.1471, 26.2006, 19.7515, 31.1048,
                             28.5355, 30.7333, 26.7509, 18.5204, 32.2396],
                'longitude': [77.1025, 75.3412, 92.9376, 75.7139, 77.1734,
                              77.3910, 76.7794, 94.2036, 73.8567, 76.3209],
                'capacity': [500, 400, 450, 600, 350, 450, 350, 400, 550, 300],
                'vehicles': [10, 8, 7, 12, 6, 9, 7, 6, 11, 5]
            })
            centers_df.to_csv(RESOURCE_CENTERS_PATH, index=False)
        return centers_df
    except Exception as e:
        st.error(f"❌ Error loading resource centers: {e}")
        return pd.DataFrame()

def load_user_emails(region):
    try:
        emails_df = pd.read_excel(EMAIL_FILE_PATH, engine='openpyxl')
        if "email" not in emails_df.columns or "Location" not in emails_df.columns:
            st.error("❌ Excel file must contain 'email' and 'Location' columns.")
            return []
        return emails_df[emails_df["Location"].str.lower() == region.lower()]["email"].tolist()
    except Exception as e:
        st.error(f"❌ Error loading emails: {e}")
        return []

def send_sms_alert(phone_number, location, resource_info=None):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        if resource_info:
            message = client.messages.create(
                body=(
                    f"\nAlert: Resource needed in {location}!\n"
                    #f"Please deploy the following resources immediately:\n"
                    f"- Water Units: {resource_info['water_units']}\n"
                    f"- Food Kits: {resource_info['food_kits']}\n"
                    f"- Medicine Kits: {resource_info['medicine_kits']}\n"
                    f"- Shelter Units: {resource_info['shelter_units']}\n"
                    #f"This is an urgent request. Please confirm deployment."
                ),
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        else:
            message = client.messages.create(
                body=(
                    f"Earthquake Alert: {location} is affected. Take necessary precautions!\n"
                    #"🔹 Drop, Cover, and Hold On.\n"
                    "🔹 Move to an open area if outside.\n"
                    #"🔹 Stay away from windows and heavy objects.\n"
                    #"🔹 Keep emergency contacts and supplies ready.\n"
                    #"🔹 Follow official updates and stay safe!"
                ),
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        return message.sid
    except Exception as e:
        return f"Error: {e}"

def send_email(subject, location, recipients):
    message = (
        f"🚨 Earthquake Alert: {location} is affected. Take necessary precautions!\n\n"
        "🔹 Drop, Cover, and Hold On.\n"
        "🔹 Move to an open area if outside.\n"
        "🔹 Stay away from windows and heavy objects.\n"
        "🔹 Keep emergency contacts and supplies ready.\n"
        "🔹 Follow official updates and stay safe!\n\n"
        "Stay Safe,\nDisaster Alert System"
    )
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        for email in recipients:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_SENDER
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))
            server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Email sending failed: {e}")
        return False

def display_map(df, resource_centers=None):
    st.subheader("🌍 Earthquake Affected Areas & Resource Centers")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")
    
    heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for _, row in df.iterrows()]
    HeatMap(heat_data, min_opacity=0.3, radius=20, blur=15, max_zoom=5).add_to(m)
    
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['magnitude'] * 2,
            color="red" if row['magnitude'] >= 5 else "orange",
            fill=True,
            fill_color="darkred" if row['magnitude'] >= 7 else "red",
            fill_opacity=0.7,
            popup=f"📍 {row['location']}<br>📆 {row['datetime'].strftime('%Y-%m-%d')}<br>🌍 Magnitude: {row['magnitude']}"
        ).add_to(m)
    
    if resource_centers is not None:
        for _, center in resource_centers.iterrows():
            folium.Marker(
                location=[center['latitude'], center['longitude']],
                popup=f"Resource Center #{center['center_id']}<br>State: {center['state']}<br>Capacity: {center['capacity']}<br>Vehicles: {center['vehicles']}",
                icon=folium.Icon(color='green', icon='medkit', prefix='fa')
            ).add_to(m)
    
    folium_static(m)

def display_resource_centers_map(earthquake_data, resource_centers, state):
    st.subheader("🌍 Nearest Resource Centers")
    selected_earthquake = earthquake_data[earthquake_data['state'] == state].iloc[0]
    earthquake_location = [selected_earthquake['latitude'], selected_earthquake['longitude']]
    
    m = folium.Map(location=earthquake_location, zoom_start=7, tiles="OpenStreetMap")
    
    folium.CircleMarker(
        location=earthquake_location,
        radius=selected_earthquake['magnitude'] * 2,
        color="red",
        fill=True,
        fill_color="darkred",
        fill_opacity=0.7,
        popup=f"📍 {selected_earthquake['location']}<br>🌍 Magnitude: {selected_earthquake['magnitude']}"
    ).add_to(m)
    
    for _, center in resource_centers.iterrows():
        icon_color = 'blue' if center['state'] == state else 'green'
        folium.Marker(
            location=[center['latitude'], center['longitude']],
            popup=f"Resource Center #{center['center_id']}<br>State: {center['state']}<br>Capacity: {center['capacity']}<br>Vehicles: {center['vehicles']}",
            icon=folium.Icon(color=icon_color, icon='medkit', prefix='fa')
        ).add_to(m)
        
        folium.PolyLine(
            locations=[
                earthquake_location,
                [center['latitude'], center['longitude']]
            ],
            color='gray',
            weight=2,
            opacity=0.7,
            dash_array='5'
        ).add_to(m)
    
    folium_static(m)

def predict_resource_needs(state, magnitude, population=None):
    if population is None:
        population_data = {
            'Delhi': 20000000,
            'Punjab': 30000000,
            'Assam': 35000000,
            'Maharashtra': 123000000,
            'Himachal Pradesh': 7000000,
            'Sikkim': 700000,
            'Rajasthan': 77000000,
            'Arunachal Pradesh': 1500000,
            'Jammu and Kashmir': 12500000,
            'Ladakh': 300000,
            'Manipur': 3000000,
            'Odisha': 45000000,
            'Tripura': 4000000
        }
        population = population_data.get(state, 10000000)
    
    severity_factor = 1.0
    if magnitude < 4.0:
        severity_factor = 0.2
    elif magnitude < 5.0:
        severity_factor = 0.5
    elif magnitude < 6.0:
        severity_factor = 1.0
    elif magnitude < 7.0:
        severity_factor = 2.0
    else:
        severity_factor = 3.0
    
    affected_percentage = min(30, magnitude * 2) / 100
    affected_population = population * affected_percentage
    
    water_needed = int(affected_population * 3 * severity_factor)
    food_needed = int(affected_population * 0.7 * severity_factor)
    medicine_needed = int(affected_population * 0.2 * severity_factor)
    shelter_needed = int(affected_population * 0.1 * severity_factor)
    
    return {
        'water_units': water_needed,
        'food_kits': food_needed,
        'medicine_kits': medicine_needed,
        'shelter_units': shelter_needed
    }

def calculate_resource_gap(inventory_df, state, needed_resources):
    state_inventory = inventory_df[inventory_df['state'] == state]
    if state_inventory.empty:
        return needed_resources
    
    gaps = {}
    for resource in ['water_units', 'food_kits', 'medicine_kits', 'shelter_units']:
        current = state_inventory.iloc[0][resource]
        needed = needed_resources[resource]
        gaps[resource] = max(0, needed - current)
    
    return gaps

def find_optimal_routes(resource_centers, affected_state, earthquake_location):
    centers_in_state = resource_centers[resource_centers['state'] == affected_state]
    if centers_in_state.empty:
        centers_in_state = resource_centers.iloc[:3]
    
    G = nx.Graph()
    
    for _, center in centers_in_state.iterrows():
        center_coords = (center['latitude'], center['longitude'])
        earthquake_coords = (earthquake_location[0], earthquake_location[1])
        
        distance = np.sqrt((center_coords[0] - earthquake_coords[0])**2 + 
                          (center_coords[1] - earthquake_coords[1])**2)
        
        G.add_node(f"Center_{center['center_id']}", 
                  pos=(center['latitude'], center['longitude']),
                  vehicles=center['vehicles'],
                  capacity=center['capacity'])
        
        G.add_node("Earthquake", pos=earthquake_coords)
        
        G.add_edge(f"Center_{center['center_id']}", "Earthquake", weight=distance)
    
    optimal_routes = []
    for node in G.nodes():
        if node != "Earthquake" and "Center_" in node:
            try:
                path = nx.shortest_path(G, source=node, target="Earthquake", weight='weight')
                distance = nx.shortest_path_length(G, source=node, target="Earthquake", weight='weight')
                vehicles = G.nodes[node]['vehicles']
                capacity = G.nodes[node]['capacity']
                
                optimal_routes.append({
                    'center': node,
                    'distance': distance,
                    'path': path,
                    'vehicles': vehicles,
                    'capacity': capacity
                })
            except nx.NetworkXNoPath:
                continue
    
    return sorted(optimal_routes, key=lambda x: x['distance'])

def update_inventory(inventory_df, state, resources_used):
    state_idx = inventory_df[inventory_df['state'] == state].index
    if len(state_idx) > 0:
        for resource, amount in resources_used.items():
            if resource in inventory_df.columns:
                current = inventory_df.at[state_idx[0], resource]
                inventory_df.at[state_idx[0], resource] = max(0, current - amount)
        
        inventory_df.at[state_idx[0], 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
        inventory_df.to_csv(SUPPLY_INVENTORY_PATH, index=False)
    
    return inventory_df

def main():
    st.title("🌍 Disaster Alert System")
    st.subheader("📊 Real-time Earthquake Data")
    
    if not authenticate():
        st.warning("⚠ Please log in to access the system.")
        return
    
    tab1, tab2, tab3 = st.tabs(["📡 Monitoring", "🏬 Inventory Management", "🚚 Resource Allocation"])
    
    df, start_date, end_date = load_data()
    inventory_df = load_inventory_data()
    resource_centers_df = load_resource_centers()
    
    with tab1:
        if df is not None and not df.empty:
            st.write(f"### 📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            st.subheader("📌 Earthquake Data Table")
            st.dataframe(df)
            display_map(df, resource_centers_df)
            
            affected_area = st.selectbox("📍 Select an affected area to send an alert:", df['state'].unique())
            recipient_emails = load_user_emails(affected_area)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📩 Send Email Alert") and recipient_emails:
                    send_email(f"🚨 Earthquake Alert: {affected_area} 🚨", affected_area, recipient_emails)
                    st.success(f"📩 Email alert sent to {len(recipient_emails)} users in {affected_area}!")
            
            with col2:
                if st.button("📲 Send SMS Alert"):
                    phone_numbers = {
                        'Delhi': ['+917796571177', '+918485078849'],
                        'Punjab': ['+917058622905'],
                        'Assam': ['+917796571177'],
                    }
                    
                    if affected_area in phone_numbers:
                        for phone in phone_numbers[affected_area]:
                            send_sms_alert(phone, affected_area)
                        st.success(f"📩 SMS alert sent to users in {affected_area}!")
                    else:
                        st.warning('No users found in the selected state.')
    
    with tab2:
        st.subheader("🏬 Pre-positioned Supply Inventory")
        
        if not inventory_df.empty:
            st.dataframe(inventory_df)
            
            st.subheader("🔄 Update Inventory")
            update_state = st.selectbox("Select state to update inventory:", inventory_df['state'].unique())
            
            col1, col2 = st.columns(2)
            with col1:
                water = st.number_input("Water Units:", min_value=0, value=int(inventory_df[inventory_df['state'] == update_state]['water_units'].values[0]))
                food = st.number_input("Food Kits:", min_value=0, value=int(inventory_df[inventory_df['state'] == update_state]['food_kits'].values[0]))
            
            with col2:
                medicine = st.number_input("Medicine Kits:", min_value=0, value=int(inventory_df[inventory_df['state'] == update_state]['medicine_kits'].values[0]))
                shelter = st.number_input("Shelter Units:", min_value=0, value=int(inventory_df[inventory_df['state'] == update_state]['shelter_units'].values[0]))
            
            if st.button("💾 Save Inventory Updates"):
                idx = inventory_df[inventory_df['state'] == update_state].index[0]
                inventory_df.at[idx, 'water_units'] = water
                inventory_df.at[idx, 'food_kits'] = food
                inventory_df.at[idx, 'medicine_kits'] = medicine
                inventory_df.at[idx, 'shelter_units'] = shelter
                inventory_df.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
                inventory_df.to_csv(SUPPLY_INVENTORY_PATH, index=False)
                st.success("✅ Inventory updated successfully!")
    
    with tab3:
        st.subheader("🚚 AI-Driven Resource Allocation")
        
        if not df.empty and not inventory_df.empty:
            disaster_state = st.selectbox("Select affected state for resource allocation:", df['state'].unique())
            
            selected_earthquake = df[df['state'] == disaster_state].iloc[0]
            magnitude = selected_earthquake['magnitude']
            earthquake_location = (selected_earthquake['latitude'], selected_earthquake['longitude'])
            
            display_resource_centers_map(df, resource_centers_df, disaster_state)
            
            predicted_needs = predict_resource_needs(disaster_state, magnitude)
            resource_gaps = calculate_resource_gap(inventory_df, disaster_state, predicted_needs)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🧮 AI-Predicted Resource Needs")
                needs_df = pd.DataFrame({
                    'Resource': ['Water Units', 'Food Kits', 'Medicine Kits', 'Shelter Units'],
                    'Predicted Need': [
                        predicted_needs['water_units'], 
                        predicted_needs['food_kits'],
                        predicted_needs['medicine_kits'],
                        predicted_needs['shelter_units']
                    ]
                })
                st.dataframe(needs_df)
            
            with col2:
                st.subheader("⚠️ Resource Gaps")
                gaps_df = pd.DataFrame({
                    'Resource': ['Water Units', 'Food Kits', 'Medicine Kits', 'Shelter Units'],
                    'Shortfall': [
                        resource_gaps['water_units'], 
                        resource_gaps['food_kits'],
                        resource_gaps['medicine_kits'],
                        resource_gaps['shelter_units']
                    ]
                })
                st.dataframe(gaps_df)
            
            st.subheader("🗺️ Optimal Resource Routing")
            
            optimal_routes = find_optimal_routes(resource_centers_df, disaster_state, earthquake_location)
            
            if optimal_routes:
                routes_df = pd.DataFrame({
                    'Resource Center': [route['center'] for route in optimal_routes],
                    'Distance': [f"{route['distance']:.2f}" for route in optimal_routes],
                    'Available Vehicles': [route['vehicles'] for route in optimal_routes],
                    'Capacity': [route['capacity'] for route in optimal_routes]
                })
                st.dataframe(routes_df)
                
                best_route = optimal_routes[0]
                st.success(f"✅ Optimal route found: {best_route['center']} → Affected Area (Distance: {best_route['distance']:.2f})")
                
                if st.button("🚀 Deploy Resources"):
                    resources_to_deploy = {
                        'water_units': min(predicted_needs['water_units'], inventory_df[inventory_df['state'] == disaster_state]['water_units'].values[0]),
                        'food_kits': min(predicted_needs['food_kits'], inventory_df[inventory_df['state'] == disaster_state]['food_kits'].values[0]),
                        'medicine_kits': min(predicted_needs['medicine_kits'], inventory_df[inventory_df['state'] == disaster_state]['medicine_kits'].values[0]),
                        'shelter_units': min(predicted_needs['shelter_units'], inventory_df[inventory_df['state'] == disaster_state]['shelter_units'].values[0])
                    }
                    
                    inventory_df = update_inventory(inventory_df, disaster_state, resources_to_deploy)
                    
                    center_id = int(best_route['center'].split('_')[1])
                    center_state = resource_centers_df[resource_centers_df['center_id'] == center_id]['state'].values[0]
                    
                    phone_numbers = {
                        'Delhi': ['+918485078849'],
                        'Punjab': ['+917058622905'],
                        'Assam': ['+917796571177']
                    }
                    
                    if center_state in phone_numbers:
                        for phone in phone_numbers[center_state]:
                            send_sms_alert(phone, disaster_state, resources_to_deploy)
                        st.success(f"📩 Deployment instructions sent to Resource Center in {center_state}!")
                    else:
                        st.warning('No phone number found for the selected resource center.')
                    
                    st.success(f"✅ Resources deployed to {disaster_state}:")
                    deployed_df = pd.DataFrame({
                        'Resource': ['Water Units', 'Food Kits', 'Medicine Kits', 'Shelter Units'],
                        'Deployed Amount': [
                            resources_to_deploy['water_units'],
                            resources_to_deploy['food_kits'],
                            resources_to_deploy['medicine_kits'],
                            resources_to_deploy['shelter_units']
                        ]
                    })
                    st.dataframe(deployed_df)
            else:
                st.error("❌ No viable routes found for resource deployment.")

if __name__ == "__main__":
    main()