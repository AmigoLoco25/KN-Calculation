import streamlit as st
import pandas as pd
import requests
import math
from datetime import datetime, timedelta


# --- AUTH ---
password = st.text_input("🔐Ingrese la contraseña", type="password")
if password != st.secrets["app_password"]:
    st.stop()

# ---------- CONFIGURATION ----------
st.set_page_config(page_title="Shipping Cost Calculator", layout="wide")
st.title("📦 Shipping Cost Comparator")

# ---------- LOAD CSV ----------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, sep=';', header=1)
    df = df[[
        'Shipment Creation/Booking Date (Day)', 'ABO', 'Spend in EUR', "Volume (m3)",
        'Gross weight (kgs)', "Consignee ZIP Code", "Destination",
        "Consignee Country", "Consignee Country / UN Code", "Packages"
    ]]

    df["Gross weight (kgs)"] = (
        df["Gross weight (kgs)"].astype(str).str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False).astype(float)
    )
    df["Spend in EUR"] = (
        df["Spend in EUR"].astype(str).str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False).astype(float)
    )
    df["Volume (m3)"] = (
        df["Volume (m3)"].astype(str).str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False).astype(float)
    )
    df["Consignee Country"] = df["Consignee Country"].str.title()
    return df

# ---------- FILE INPUT ----------
file_path = "SPEND REPORT CON ABO.csv"
try:
    kn_df = load_data(file_path)
   
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()


# ---------- ALBARAN SELECTION ----------
# Convert to datetime
kn_df['Shipment Creation/Booking Date (Day)'] = pd.to_datetime(
    kn_df['Shipment Creation/Booking Date (Day)'], errors='coerce'
)

# Input search box for ABOs
raw_input = st.text_input(
    "🔍 Enter specific ABOs (optional, comma-separated):",
    placeholder="e.g., A250254, A250255",
    key="albaran_input"
)

# Determine whether user entered specific ABOs
if raw_input.strip():
    albaran_list = [ab.strip().upper() for ab in raw_input.split(",") if ab.strip()]
    valid_abos = kn_df["ABO"].unique()
    missing_abos = [ab for ab in albaran_list if ab not in valid_abos]

    if missing_abos:
        st.warning(f"Albarán(s) not found: {', '.join(missing_abos)}")

    valid_rows = kn_df[kn_df["ABO"].isin(albaran_list)]
else:
    # Default: filter to last 30 days of data
    last_month = datetime.today() - timedelta(days=60)
    valid_rows = kn_df[kn_df["Shipment Creation/Booking Date (Day)"] >= last_month]

if valid_rows.empty:
    st.info("No orders found for this period or ABO selection.")
    st.stop()

# ---------- INFO FROM CSV ----------
for _, row in valid_rows.iterrows():
    weight = row['Gross weight (kgs)']
    zipcode = row['Consignee ZIP Code']
    country = row['Consignee Country']
    country_code = row['Consignee Country / UN Code']
    city = row['Destination']
    try:
        num_packages = int(row['Packages'])
    except:
        num_packages = 0

# ---------- DISPLAY DESTINATION INFO ----------
# ---------- PRICE MATRIX & ZONE DEFINITIONS ----------
# (You already wrote the `get_zone_*` and `get_price()` functions — paste them all here!)
# For example:
def get_weight_tier(weight):
    if weight < 30:
        return "up to 30 kg"
    elif weight < 50:
        return "up to 50 kg"
    elif weight < 100:
        return "up to 100 kg"
    elif weight < 200:
        return "up to 200 kg"
    elif weight < 300:
        return "up to 300 kg"
    elif weight < 400:
        return "up to 400 kg"
    elif weight < 500:
        return "up to 500 kg"
    elif weight < 600:
        return "up to 600 kg"
    elif weight < 700:
        return "up to 700 kg"
    elif weight < 800:
        return "up to 800 kg"
    elif weight < 900:
        return "up to 900 kg"
    elif weight < 1000:
        return "up to 1000 kg"
    elif weight < 2000:
        return "up to 2000 kg"
    elif weight < 3000:
        return "up to 3000 kg"
    else:
        return "up to 3000 kg"

def get_price(weight_class, zone, matrix, weight):
    try:
        zone_index = zone - 1
        if weight_class not in ["up to 2000 kg", "up to 3000 kg"]:
            return matrix[weight_class][zone_index]
        if weight_class == "up to 2000 kg":
            remainder = weight - 1000
            return matrix["up to 1000 kg"][zone_index] + (math.ceil(remainder / 100) * matrix[weight_class][zone_index])
        if weight_class == "up to 3000 kg":
            remainder = weight - 2000
            return matrix["up to 1000 kg"][zone_index] + (math.ceil(remainder / 100) * matrix[weight_class][zone_index])
    except Exception as e:
        return None

# ---------- MATRIXES ----------# For now, here's an example stub:
france_price_matrix = {
    "up to 30 kg":  [36.98, 38.62, 40.46, 41.31, 44.02, 43.59, 45.32, 47.07, 45.32, 47.43, 47.91, 49.12],
    "up to 50 kg":  [40.75, 44.81, 45.38, 46.79, 50.30, 47.43, 51.70, 51.99, 52.48, 52.61, 53.39, 55.41],
    "up to 100 kg": [47.33, 51.95, 54.86, 57.65, 63.20, 54.17, 59.04, 61.47, 67.54, 62.72, 64.27, 68.30],
    "up to 200 kg": [58.32, 63.63, 70.62, 75.82, 84.95, 69.95, 75.54, 81.75, 92.99, 84.05, 86.93, 94.39],
    "up to 300 kg": [73.47, 79.82, 91.10, 98.89, 112.03, 90.40, 97.08, 107.24, 124.10, 110.68, 114.99, 126.20],
    "up to 400 kg": [87.47, 94.83, 110.45, 120.82, 137.98, 109.69, 117.45, 131.59, 154.07, 136.18, 141.93, 156.87],
    "up to 500 kg": [101.42, 109.84, 129.75, 142.71, 163.88, 128.94, 137.80, 155.89, 183.98, 161.63, 168.81, 187.50],
    "up to 600 kg": [108.19, 117.10, 139.97, 154.66, 178.41, 139.17, 148.55, 169.37, 201.20, 175.87, 184.01, 205.17],
    "up to 700 kg": [120.62, 130.50, 157.44, 174.58, 202.10, 156.59, 167.00, 191.54, 228.69, 199.14, 208.64, 233.31],
    "up to 800 kg": [133.48, 144.31, 175.31, 194.89, 226.21, 174.45, 185.86, 214.14, 256.59, 222.82, 233.67, 261.88],
    "up to 900 kg": [145.51, 157.33, 192.39, 214.42, 249.52, 191.48, 203.93, 235.94, 283.70, 245.71, 257.92, 289.65],
    "up to 1000 kg": [158.35, 171.12, 210.27, 234.75, 273.62, 209.32, 222.77, 258.54, 311.59, 269.39, 282.94, 318.21],
    "up to 2000 kg": [13.89, 14.99, 18.87, 21.27, 25.00, 18.81, 19.97, 23.53, 28.70, 24.59, 25.91, 29.35],
    "up to 3000 kg": [12.08, 12.91, 15.95, 17.81, 20.76, 16.92, 17.80, 20.58, 21.89, 21.41, 22.43, 25.11]
}


# In[558]:


belgium_price_matrix = {
    "up to 30 kg":  [46.32, 54.73, 56.87, 59.00],
    "up to 50 kg":  [48.84, 57.25, 59.39, 61.52],
    "up to 100 kg": [54.06, 62.60, 65.69, 68.78],
    "up to 200 kg": [66.20, 74.44, 79.97, 85.50],
    "up to 300 kg": [84.15, 92.82, 101.62, 110.43],
    "up to 400 kg": [100.94, 110.03, 122.12, 134.20],
    "up to 500 kg": [117.70, 127.20, 142.57, 157.93],
    "up to 600 kg": [124.72, 133.98, 150.81, 167.64],
    "up to 700 kg": [139.77, 149.43, 169.36, 189.29],
    "up to 800 kg": [151.61, 161.42, 182.50, 203.59],
    "up to 900 kg": [165.78, 175.95, 199.87, 223.80],
    "up to 1000 kg": [180.76, 191.29, 218.06, 244.82],
    "up to 2000 kg": [15.34, 15.98, 18.30, 20.62],
    "up to 3000 kg": [14.66, 15.22, 17.47, 19.73]
}


# In[559]:


czech_price_matrix = {
    "up to 30 kg":  [39.82, 41.04, 42.15, 42.25, 43.37, 44.58],
    "up to 50 kg":  [43.26, 46.27, 45.59, 46.46, 48.60, 48.79],
    "up to 100 kg": [46.67, 49.93, 48.89, 51.56, 52.15, 53.78],
    "up to 200 kg": [63.44, 67.17, 67.54, 71.32, 71.28, 75.42],
    "up to 300 kg": [84.27, 88.74, 90.44, 95.52, 94.90, 101.69],
    "up to 400 kg": [104.02, 109.19, 112.24, 118.64, 117.41, 126.85],
    "up to 500 kg": [123.71, 129.63, 133.99, 141.71, 139.90, 151.98],
    "up to 600 kg": [134.68, 140.95, 146.32, 154.86, 152.59, 166.50],
    "up to 700 kg": [152.57, 159.51, 166.14, 175.91, 173.09, 189.49],
    "up to 800 kg": [170.85, 178.48, 186.37, 197.37, 193.99, 212.88],
    "up to 900 kg": [188.36, 196.67, 205.82, 218.06, 214.13, 235.51],
    "up to 1000 kg": [206.62, 215.61, 226.02, 239.51, 235.00, 258.90],
    "up to 2000 kg": [18.90, 19.67, 20.79, 22.05, 21.56, 23.94],
    "up to 3000 kg": [17.55, 18.13, 19.44, 19.99, 20.02, 21.88]
}


# In[560]:


denmark_price_matrix = {
    "up to 30 kg":  [48.03, 48.13, 51.07, 51.40, 53.77, 52.65, 54.10],
    "up to 50 kg":  [51.65, 53.81, 55.65, 56.19, 57.39, 58.22, 58.47],
    "up to 100 kg": [57.92, 60.39, 64.31, 65.39, 63.66, 64.68, 66.71],
    "up to 200 kg": [79.69, 82.15, 90.00, 92.01, 90.32, 90.67, 95.84],
    "up to 300 kg": [106.39, 109.01, 121.11, 124.12, 122.34, 122.07, 130.52],
    "up to 400 kg": [131.95, 134.76, 151.10, 155.11, 153.21, 152.38, 164.15],
    "up to 500 kg": [157.49, 160.49, 181.02, 186.04, 184.06, 182.66, 197.71],
    "up to 600 kg": [172.05, 175.08, 198.43, 204.12, 202.15, 200.33, 217.65],
    "up to 700 kg": [195.40, 198.62, 225.94, 232.59, 230.52, 228.19, 248.63],
    "up to 800 kg": [219.18, 222.58, 253.87, 261.45, 259.31, 256.46, 280.00],
    "up to 900 kg": [242.16, 245.77, 281.01, 289.54, 287.31, 283.97, 310.63],
    "up to 1000 kg": [265.91, 269.71, 308.92, 318.41, 316.08, 312.23, 341.99],
    "up to 2000 kg": [24.14, 24.48, 27.62, 28.15, 28.81, 28.91, 31.88],
    "up to 3000 kg": [22.44, 22.52, 25.39, 26.70, 27.66, 28.43, 30.86]
}


# In[561]:


finland_price_matrix = {
    "up to 30 kg":  [64.82, 73.07, 74.60, 76.13, 76.97, 77.62, 79.60, 82.57, 87.51],
    "up to 50 kg":  [67.24, 75.49, 77.02, 78.56, 79.40, 80.04, 82.02, 84.99, 89.94],
    "up to 100 kg": [71.92, 80.26, 82.66, 85.07, 86.26, 87.16, 89.94, 94.12, 101.08],
    "up to 200 kg": [100.52, 108.48, 113.14, 117.81, 119.85, 121.42, 126.23, 133.44, 145.47],
    "up to 300 kg": [135.97, 144.22, 151.88, 159.54, 162.76, 165.21, 172.77, 184.11, 203.01],
    "up to 400 kg": [170.31, 178.85, 189.51, 200.16, 204.54, 207.89, 218.20, 233.67, 259.44],
    "up to 500 kg": [204.61, 213.44, 224.91, 240.74, 246.29, 250.54, 263.59, 283.18, 315.83],
    "up to 600 kg": [223.68, 232.23, 247.24, 262.25, 268.31, 272.95, 287.22, 308.63, 344.32],
    "up to 700 kg": [255.33, 264.15, 278.46, 299.82, 306.99, 312.47, 329.34, 354.65, 396.82],
    "up to 800 kg": [284.57, 293.49, 306.57, 331.28, 338.87, 344.67, 362.51, 389.27, 433.88],
    "up to 900 kg": [315.45, 324.63, 346.12, 367.61, 376.20, 382.77, 402.99, 433.33, 483.88],
    "up to 1000 kg": [347.12, 356.55, 380.63, 404.71, 414.32, 421.66, 444.26, 478.16, 534.66],
    "up to 2000 kg": [31.74, 32.29, 34.39, 36.49, 37.32, 37.95, 39.90, 42.83, 47.71],
    "up to 3000 kg": [29.82, 30.36, 32.40, 34.54, 35.46, 36.24, 38.55, 40.76, 45.66]
}


# In[562]:


germany_price_matrix = {
    "up to 30 kg":  [32.37, 36.42, 37.44, 33.79, 37.60, 39.06, 36.28, 38.81, 37.47, 38.48, 39.09, 40.00],
    "up to 50 kg":  [36.39, 40.08, 41.47, 38.02, 41.64, 43.29, 39.51, 43.20, 41.91, 42.48, 43.39, 44.04],
    "up to 100 kg": [42.48, 45.68, 47.35, 44.03, 47.43, 49.97, 44.91, 49.66, 47.57, 48.58, 50.19, 51.45],
    "up to 200 kg": [55.14, 61.14, 64.17, 57.74, 64.32, 68.66, 60.73, 67.88, 64.06, 66.45, 69.07, 71.75],
    "up to 300 kg": [71.58, 80.62, 85.13, 75.35, 85.34, 91.67, 80.52, 90.42, 84.69, 88.53, 92.28, 96.47],
    "up to 400 kg": [86.93, 98.96, 104.99, 91.85, 105.27, 113.59, 99.20, 111.85, 104.20, 109.53, 114.41, 120.14],
    "up to 500 kg": [102.24, 117.29, 124.81, 108.31, 125.17, 135.48, 117.85, 133.25, 123.69, 130.48, 136.49, 143.73],
    "up to 600 kg": [110.26, 127.28, 135.83, 117.09, 136.24, 147.83, 128.15, 145.29, 134.45, 142.25, 148.99, 157.27],
    "up to 700 kg": [123.99, 143.83, 153.81, 131.91, 154.29, 167.76, 145.04, 164.76, 152.13, 161.31, 169.13, 178.84],
    "up to 800 kg": [138.10, 160.78, 172.20, 147.12, 172.74, 188.09, 162.31, 184.64, 170.20, 180.77, 189.64, 200.79],
    "up to 900 kg": [151.47, 176.95, 189.82, 161.58, 190.44, 207.65, 178.83, 203.75, 187.50, 199.47, 209.39, 221.99],
    "up to 1000 kg": [165.58, 193.90, 208.19, 176.79, 208.87, 227.97, 196.10, 223.62, 205.56, 218.91, 229.90, 243.94],
    "up to 2000 kg": [14.88, 17.63, 19.03, 15.95, 19.09, 20.94, 17.89, 20.51, 18.75, 20.06, 21.12, 22.50],
    "up to 3000 kg": [13.28, 16.26, 17.52, 14.39, 17.62, 19.12, 16.60, 18.78, 17.31, 18.48, 19.26, 20.43]
}


# In[563]:


uk_price_matrix = {
    "up to 30 kg":  [46.95, 52.13, 57.83, 73.17, 83.46, 92.96, 95.59, 103.25],
    "up to 50 kg":  [49.32, 54.50, 60.20, 75.54, 85.83, 95.33, 97.96, 105.61],
    "up to 100 kg": [54.51, 59.59, 67.42, 88.25, 100.91, 113.58, 102.50, 126.24],
    "up to 200 kg": [67.45, 72.14, 80.72, 99.13, 114.35, 128.05, 114.22, 141.75],
    "up to 300 kg": [112.14, 117.65, 126.26, 147.62, 161.32, 176.54, 158.91, 190.24],
    "up to 400 kg": [135.75, 142.85, 153.74, 172.56, 189.30, 204.52, 190.66, 221.27],
    "up to 500 kg": [160.60, 167.74, 185.05, 208.87, 222.57, 236.27, 219.13, 251.49],
    "up to 600 kg": [178.21, 189.08, 191.11, 223.79, 243.91, 264.03, 240.92, 284.14],
    "up to 700 kg": [197.22, 208.10, 210.13, 242.81, 262.92, 283.04, 259.94, 303.16],
    "up to 800 kg": [240.14, 250.27, 267.99, 297.51, 321.94, 344.93, 296.77, 367.92],
    "up to 900 kg": [258.77, 268.89, 286.62, 316.14, 340.57, 363.56, 315.40, 386.55],
    "up to 1000 kg": [278.18, 288.31, 306.04, 335.56, 359.98, 382.97, 334.81, 405.96],
    "up to 2000 kg": [24.74, 25.29, 26.63, 28.65, 30.47, 32.29, 30.41, 33.97],
    "up to 3000 kg": [22.63, 22.93, 24.03, 25.34, 26.77, 28.20, 27.00, 29.56]
}


# In[564]:


poland_price_matrix = {
    "up to 30 kg":  50.50,
    "up to 50 kg":  52.93,
    "up to 100 kg": 57.33,
    "up to 200 kg": 76.54,
    "up to 300 kg": 99.35,
    "up to 400 kg": 120.99,
    "up to 500 kg": 142.60,
    "up to 600 kg": 153.33,
    "up to 700 kg": 172.97,
    "up to 800 kg": 190.68,
    "up to 900 kg": 209.61,
    "up to 1000 kg": 229.34,
    "up to 2000 kg": 20.27,
    "up to 3000 kg": 20.41
}


# In[565]:


ireland_price_matrix = {
    "up to 30 kg":  [59.67, 68.51, 69.92, 71.32, 72.23],
    "up to 50 kg":  [62.15, 70.99, 72.40, 73.80, 74.70],
    "up to 100 kg": [66.84, 75.76, 78.08, 80.39, 81.66],
    "up to 200 kg": [89.60, 98.09, 102.75, 107.42, 109.61],
    "up to 300 kg": [118.81, 127.57, 135.35, 143.12, 146.56],
    "up to 400 kg": [146.88, 155.92, 166.80, 177.68, 182.37],
    "up to 500 kg": [174.91, 184.23, 198.21, 212.20, 218.14],
    "up to 600 kg": [189.77, 198.76, 214.16, 229.56, 236.06],
    "up to 700 kg": [215.48, 224.73, 243.06, 261.40, 269.08],
    "up to 800 kg": [238.91, 248.25, 267.69, 287.12, 295.24],
    "up to 900 kg": [263.87, 273.46, 295.58, 317.70, 326.90],
    "up to 1000 kg": [289.63, 299.45, 324.26, 349.07, 359.36],
    "up to 2000 kg": [26.21, 26.81, 29.04, 32.26, 32.38],
    "up to 3000 kg": [25.30, 25.32, 27.52, 30.91, 31.41]
}


# In[566]:


netherlands_price_matrix = {
    "up to 30 kg":  [42.39, 49.17, 50.93, 52.68],
    "up to 50 kg":  [44.95, 51.74, 53.49, 55.25],
    "up to 100 kg": [49.92, 56.80, 59.33, 61.87],
    "up to 200 kg": [62.69, 69.32, 73.84, 78.37],
    "up to 300 kg": [80.77, 87.73, 90.89, 102.13],
    "up to 400 kg": [97.68, 104.96, 114.84, 124.71],
    "up to 500 kg": [114.55, 122.15, 134.70, 147.25],
    "up to 600 kg": [122.09, 129.51, 143.25, 156.99],
    "up to 700 kg": [137.24, 144.96, 161.23, 177.49],
    "up to 800 kg": [149.81, 157.64, 174.86, 192.07],
    "up to 900 kg": [164.15, 172.27, 191.80, 211.33],
    "up to 1000 kg": [179.32, 187.72, 209.56, 231.41],
    "up to 2000 kg": [16.42, 16.54, 19.66, 20.88],
    "up to 3000 kg": [14.86, 15.30, 17.61, 18.98]
}


# In[567]:


austria_price_matrix = {
    "up to 30 kg":  [44.93, 46.37, 46.22, 47.66, 47.79, 47.93, 48.10, 49.37, 48.48, 49.07, 50.78, 51.10],
    "up to 50 kg":  [48.48, 51.99, 49.77, 53.27, 52.23, 51.48, 52.74, 54.98, 53.37, 53.51, 55.23, 55.73],
    "up to 100 kg": [54.55, 58.56, 55.83, 59.84, 60.55, 57.55, 61.57, 61.55, 62.84, 61.83, 63.54, 64.57],
    "up to 200 kg": [74.61, 79.20, 76.99, 81.58, 84.29, 80.17, 86.17, 84.76, 88.53, 86.67, 89.84, 91.72],
    "up to 300 kg": [99.35, 104.84, 102.92, 108.40, 113.17, 107.68, 115.98, 113.17, 119.52, 116.73, 121.49, 124.31],
    "up to 400 kg": [122.96, 129.32, 127.71, 134.07, 140.92, 134.06, 144.68, 140.43, 149.41, 145.67, 152.02, 155.79],
    "up to 500 kg": [146.53, 153.79, 152.47, 159.73, 168.61, 160.41, 173.33, 167.67, 179.22, 174.55, 182.49, 187.21],
    "up to 600 kg": [159.85, 167.54, 166.57, 174.27, 184.62, 175.57, 189.96, 183.27, 196.62, 191.34, 200.34, 205.68],
    "up to 700 kg": [181.38, 189.89, 189.23, 197.74, 210.03, 199.72, 216.25, 208.24, 224.04, 217.88, 228.37, 234.60],
    "up to 800 kg": [203.31, 212.66, 212.28, 221.63, 235.84, 224.27, 242.96, 233.62, 251.85, 244.81, 256.81, 263.92],
    "up to 900 kg": [224.43, 234.62, 234.52, 244.71, 260.88, 248.02, 268.89, 258.21, 278.91, 270.97, 284.47, 292.48],
    "up to 1000 kg": [246.35, 257.37, 257.56, 268.59, 286.70, 272.56, 295.60, 283.58, 306.71, 297.92, 312.91, 321.81],
    "up to 2000 kg": [22.61, 23.55, 23.70, 24.64, 26.47, 25.16, 27.35, 26.11, 28.43, 27.57, 29.03, 29.90],
    "up to 3000 kg": [21.01, 21.72, 22.10, 22.81, 24.00, 23.56, 24.68, 24.27, 25.53, 25.10, 26.56, 27.23]
}


# In[568]:


switzerland_price_matrix = {
    "up to 30 kg":  [59.77, 59.03, 62.22, 62.66, 64.71, 65.14, 65.24, 65.67],
    "up to 50 kg":  [64.05, 63.22, 70.13, 70.57, 70.55, 70.99, 71.42, 71.86],
    "up to 100 kg": [72.06, 71.08, 78.97, 79.41, 82.45, 82.88, 84.20, 84.64],
    "up to 200 kg": [94.70, 93.64, 102.66, 103.46, 111.48, 112.29, 114.75, 115.56],
    "up to 300 kg": [123.30, 122.06, 132.81, 134.02, 147.24, 148.44, 152.14, 153.35],
    "up to 400 kg": [150.81, 149.43, 161.83, 163.44, 181.93, 183.54, 188.47, 190.08],
    "up to 500 kg": [178.27, 176.75, 190.85, 192.86, 216.57, 218.58, 224.73, 226.74],
    "up to 600 kg": [193.50, 191.94, 206.85, 209.13, 236.45, 238.72, 245.71, 247.99],
    "up to 700 kg": [218.72, 217.04, 233.51, 236.16, 268.40, 271.06, 279.21, 281.87],
    "up to 800 kg": [244.36, 242.54, 260.57, 263.61, 300.78, 303.81, 313.11, 316.15],
    "up to 900 kg": [269.18, 267.25, 286.88, 290.29, 332.40, 335.81, 341.17, 349.70],
    "up to 1000 kg": [294.77, 292.72, 313.91, 317.71, 364.75, 368.55, 369.93, 383.97],
    "up to 2000 kg": [26.76, 26.60, 28.40, 28.77, 33.47, 33.84, 34.15, 35.35],
    "up to 3000 kg": [24.21, 24.10, 25.46, 25.83, 29.43, 29.80, 30.59, 30.97]
}


# In[569]:


estonia_price_matrix = {
    "up to 30 kg":  [62.62, 71.36, 71.96, 72.56],
    "up to 50 kg":  [65.05, 73.79, 74.39, 74.99],
    "up to 100 kg": [69.45, 78.29, 79.69, 81.09],
    "up to 200 kg": [99.22, 107.66, 111.20, 114.74],
    "up to 300 kg": [135.47, 144.24, 150.54, 156.83],
    "up to 400 kg": [170.60, 179.69, 188.75, 197.81],
    "up to 500 kg": [205.70, 215.11, 226.92, 238.74],
    "up to 600 kg": [336.38, 345.49, 358.60, 371.70],
    "up to 700 kg": [341.10, 350.52, 366.23, 381.94],
    "up to 800 kg": [344.00, 353.53, 370.22, 386.90],
    "up to 900 kg": [348.04, 357.86, 376.93, 396.00],
    "up to 1000 kg": [352.87, 362.96, 384.42, 405.88],
    "up to 2000 kg": [35.51, 36.10, 38.00, 39.90],
    "up to 3000 kg": [31.63, 32.21, 35.08, 37.95]
}


# In[570]:


croatia_price_matrix = {
    "up to 30 kg":  [55.27, 62.63, 62.96, 63.29, 63.98, 64.50, 66.12],
    "up to 50 kg":  [57.76, 65.12, 65.45, 65.78, 66.47, 66.99, 68.61],
    "up to 100 kg": [62.02, 69.46, 70.44, 71.41, 72.38, 73.12, 75.39],
    "up to 200 kg": [88.58, 95.69, 98.38, 101.07, 102.73, 104.01, 107.93],
    "up to 300 kg": [120.95, 128.33, 133.22, 138.10, 140.72, 142.72, 148.89],
    "up to 400 kg": [152.18, 159.83, 166.91, 173.99, 177.56, 180.29, 188.70],
    "up to 500 kg": [183.37, 191.28, 200.56, 209.84, 214.36, 217.82, 228.47],
    "up to 600 kg": [201.08, 208.74, 219.06, 229.37, 234.32, 238.10, 249.74],
    "up to 700 kg": [229.77, 237.69, 250.07, 262.46, 268.31, 272.78, 286.53],
    "up to 800 kg": [257.06, 265.08, 278.24, 291.41, 297.59, 302.32, 316.87],
    "up to 900 kg": [285.12, 293.37, 308.43, 323.50, 330.50, 335.86, 352.35],
    "up to 1000 kg": [313.97, 322.46, 339.42, 356.39, 364.22, 370.21, 388.63],
    "up to 2000 kg": [28.94, 29.44, 30.94, 32.45, 33.13, 33.64, 35.24],
    "up to 3000 kg": [21.53, 22.01, 24.29, 26.57, 27.58, 28.35, 30.40]
}


# ---------- GET ZONE ----------


def get_zone_france(zipcode):
    prefix = str(zipcode)[:2]
    if prefix in ['69']:
        return 1
    elif prefix in ['38', '42']:
        return 2
    elif prefix in ['01', '03', '04', '05', '07', '13', '21', '25', '26', '30', '34','39', '43', '48', '58', '63', '71', '73', '74', '84']:
        return 3
    elif prefix in ['06', '11', '12', '15', '19', '23', '24', '46', '66', '68','70', '81', '83', '90']:
        return 4
    elif prefix in ['16', '17', '22', '56', '67', '85', '09', '31', '32', '33','47', '65', '82']:
        return 5
    elif prefix in ['75', '91', '92', '94']:
        return 6
    elif prefix in ['77', '78', '93', '95']:
        return 7
    elif prefix in ['02', '10', '27', '28', '41', '45', '51', '60', '76', '80', '89']:
        return 8
    elif prefix in ['40', '64']:
        return 9
    elif prefix in ['08', '14', '18', '36', '37', '52', '53', '55', '59', '61', '62', '72']:
        return 10
    elif prefix in ['35', '44', '49', '50', '54', '57', '79', '86', '87', '88']:
        return 11
    elif prefix in ['29']:
        return 12
    else:
        return None


# In[572]:


def get_zone_belgium(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None
    # ZONA 1
    if (10 <= prefix <= 13 or
        16 <= prefix <= 19 or
        21 <= prefix <= 22 or
        25 <= prefix <= 26 or
        prefix == 28 or
        30 <= prefix <= 31):
        return 1
    # ZONA 2
    elif (14 <= prefix <= 15 or
          prefix == 20 or
          23 <= prefix <= 24 or
          prefix == 29 or
          32 <= prefix <= 39 or
          42 <= prefix <= 46 or
          50 <= prefix <= 53 or
          60 <= prefix <= 62 or
          70 <= prefix <= 72 or
          90 <= prefix <= 99):
        return 2
    # ZONA 3
    elif (40 <= prefix <= 41 or
          47 <= prefix <= 49 or
          55 <= prefix <= 56 or
          64 <= prefix <= 66 or
          68 <= prefix <= 69 or
          prefix == 73 or
          75 <= prefix <= 89):
        return 3
    # ZONA 4
    elif prefix == 67:
        return 4
        
    return None


# In[573]:


def get_zone_czech(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None

    if prefix in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 25, 27}:
        return 1
    elif prefix in {26, 28, 29, 30, 31, 32, 33, 41, 43, 44, 47}:
        return 2
    elif prefix in {60, 61, 62, 63, 64, 66}:
        return 3
    elif prefix in {34, 35, 36, 37, 38, 39, 40, 46, 50, 51, 53, 54, 55, 58}:
        return 4
    elif prefix in {56, 57, 59, 67, 68, 69, 77}:
        return 5
    elif prefix in {70, 71, 72, 73, 74, 75, 76, 78, 79}:
        return 6

    return None


# In[574]:


def get_zone_denmark(zipcode):
    try:
        prefix = int(str(zipcode).strip()[:2])
    except:
        return None

    if prefix in {60, 70, 72, 73, 87}:
        return 1
    elif prefix in {
        51, 52, 54, 55, 56, 61, 65, 66, 67, 68, 69, 71, 74, 80, 81, 82, 83, 86, 88
    }:
        return 2
    elif prefix in {
        49, 50, 53, 57, 58, 59, 62, 63, 64, 75, 76, 77, 78, 79, 84, 85, 89, 90, 91, 92, 95, 96
    }:
        return 3
    elif prefix in {93, 94, 97, 98, 99}:
        return 4
    elif prefix in {
        10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 34, 35, 36, 40, 43
    }:
        return 5
    elif prefix in {30, 31, 32, 33, 41, 42, 44, 45, 46, 47}:
        return 6
    elif prefix == 48:
        return 7

    return None


# In[575]:


def get_zone_finland(zipcode):
    try:
        prefix = int(str(zipcode).strip()[:2])
    except:
        return None

    if prefix in {0, 2, 8, 9}:  # "00", "02", "08", "09"
        return 1
    elif prefix in {3, 7, 10, 11, 12, 13, 14}:  # "03", "07", "10"–"14"
        return 2
    elif prefix in {15, 16, 17, 18, 19, 20, 21, 24, 25, 30, 31, 32, 33, 36, 37, 45, 46, 47, 48, 49}:
        return 3
    elif prefix in {23, 26, 27, 28, 29, 34, 35, 38, 39, 40, 41, 42, 50, 51, 52, 53, 54, 55, 56}:
        return 4
    elif prefix in {43, 44, 57, 58, 59, 60, 61, 62, 63, 64, 76, 77, 78, 79}:
        return 5
    elif prefix in {65, 66, 68, 69, 70, 71, 72, 73, 74, 80, 82, 83}:
        return 6
    elif prefix in {22, 67, 75, 81, 84, 85, 86, 87, 88, 89, 90, 91, 92}:
        return 7
    elif prefix in {93, 94, 95, 96, 97, 98}:
        return 8
    elif prefix == 99:
        return 9

    return None


# In[576]:


def get_zone_germany(zipcode):
    try:
        prefix = int(str(zipcode).strip()[:2])
    except:
        return None

    if prefix in {70, 71, 72, 73, 74, 75, 76, 86, 88, 89, 97}:
        return 1
    elif prefix in {44, 45, 51, 55, 56, 57, 58, 60, 61, 65, 78}:
        return 2
    elif prefix in {40, 42, 47, 48, 52, 53, 54, 59, 77, 79, 85}:
        return 3
    elif prefix in {32, 33, 49, 63, 64, 66, 67, 68, 69}:
        return 4
    elif prefix in {34, 41, 46, 50, 80, 81, 82, 84, 87, 90, 91, 92, 93}:
        return 5
    elif prefix in {7, 36, 37, 83}:
        return 6
    elif prefix in {9, 30, 31, 35, 96}:
        return 7
    elif prefix in {26, 27, 28, 99}:
        return 8
    elif prefix in {1, 4, 6, 8, 29, 38, 95, 98}:
        return 9
    elif prefix in {2, 3, 20, 21, 22, 39, 94}:
        return 10
    elif prefix in {10, 12, 13, 14, 15, 23, 25}:
        return 11
    elif prefix in {16, 17, 18, 19, 24}:
        return 12

    return None


# In[577]:


def get_zone_uk(zipcode):
    # Make sure it's upper case and trimmed
    code = str(zipcode).strip().upper()[:2]

    zone_1 = {'BR', 'CM', 'DA', 'DE', 'E', 'EC', 'IG', 'KT', 'LE', 'ME', 'N', 'NG', 'NW', 'RM', 'S', 'SE', 'SM', 'SS'}
    zone_2 = {'AL', 'B', 'CO', 'CR', 'CT', 'CV', 'CW', 'DY', 'EN', 'GU', 'HA', 'HP', 'LU', 'NN', 'PE', 'RG', 'RH', 'SG',
              'SK', 'SL', 'ST', 'SW', 'TF', 'TN', 'TW', 'UB', 'W', 'WC', 'WD', 'WS', 'WV'}
    zone_3 = {'BA', 'BB', 'BD', 'BL', 'BN', 'BS', 'CB', 'CH', 'DN', 'GL', 'HD', 'HR', 'HU', 'HX', 'IP', 'L', 'LD', 'LN',
              'LS', 'M', 'MK', 'NR', 'OL', 'OX', 'PO', 'PR', 'SN', 'SO', 'SP', 'SY', 'WA', 'WF', 'WN', 'WR', 'YO'}
    zone_4 = {'BH', 'CF', 'DH', 'DL', 'DT', 'FY', 'HG', 'NP', 'SR', 'TS'}
    zone_5 = {'LL', 'NE', 'TA'}
    zone_6 = {'EX', 'LA', 'SA', 'TQ'}
    zone_7 = {'BT', 'CA', 'DG', 'EH', 'FK', 'G', 'KA', 'KY', 'ML', 'PL', 'TD', 'TR'}
    zone_8 = {'AB', 'DD', 'IV', 'PA', 'PH'}

    if code in zone_1:
        return 1
    elif code in zone_2:
        return 2
    elif code in zone_3:
        return 3
    elif code in zone_4:
        return 4
    elif code in zone_5:
        return 5
    elif code in zone_6:
        return 6
    elif code in zone_7:
        return 7
    elif code in zone_8:
        return 8
    else:
        return None


# In[578]:


#Poland only has one zone


# In[579]:


def get_zone_ireland(county):
    county = str(county).strip().lower()

    zone_1 = {'dublin', 'meath', 'wicklow'}
    zone_2 = {'kildare', 'louth', 'meath', 'wicklow'}
    zone_3 = {'carlow', 'cavan', 'kilkenny', 'laoighis', 'longford', 'monaghan', 'offaly',
              'roscommon', 'tipperary', 'westmeath', 'wexford'}
    zone_4 = {'clare', 'donegal', 'galway', 'leitrim', 'limerick', 'sligo', 'waterford'}
    zone_5 = {'cork', 'kerry', 'mayo'}

    if county in zone_1:
        return 1
    elif county in zone_2:
        return 2
    elif county in zone_3:
        return 3
    elif county in zone_4:
        return 4
    elif county in zone_5:
        return 5
    else:
        return None


# In[580]:


def get_zone_netherlands(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None

    if (65 <= prefix <= 70) or prefix == 73:
        return 1
    elif (
        prefix in [12, 13, 34, 35, 36, 37, 38, 39, 40, 41, 52, 53, 54, 58, 71, 72, 74, 80, 81, 82]
    ):
        return 2
    elif (
        prefix in [10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                   42, 46, 47, 48, 49, 50, 51, 55, 56, 57, 59, 60, 61, 62, 63, 64, 75, 76, 77, 78, 79,
                   83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
    ):
        return 3
    elif prefix in [43, 44, 45, 99]:
        return 4
    else:
        return None


# In[581]:


def get_zone_austria(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None

    if prefix in [50, 51, 52, 53, 54]:
        return 1
    elif prefix in [46, 48, 49, 55, 56, 57, 58]:
        return 2
    elif prefix in [10, 11, 12, 13, 21, 22, 23, 34]:
        return 3
    elif prefix in [20, 24, 25, 27, 30, 31, 35, 37, 70, 71, 72]:
        return 4
    elif prefix in [33, 40, 41, 42, 43, 44, 45, 47, 60, 61, 62, 63, 88, 89, 95, 97, 98]:
        return 5
    elif prefix in [80, 84, 85]:
        return 6
    elif prefix in [64, 65, 66, 96, 99]:
        return 7
    elif prefix in [75, 76, 81, 82, 83]:
        return 8
    elif prefix in [67, 68, 69]:
        return 9
    elif prefix in [26, 28, 32, 36, 38, 39, 73, 74, 86]:
        return 10
    elif prefix in [29, 87, 90, 91, 92, 93, 94]:
        return 11
    elif prefix == 14:
        return 12
    else:
        return None


# In[582]:


def get_zone_switzerland(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None

    if prefix in [28, 29, 40, 41, 42, 43, 44, 46, 50, 52]:
        return 1
    elif prefix in [51, 53, 54, 55, 56, 80, 81, 82, 83, 84, 86, 89]:
        return 2
    elif prefix in [25, 27, 30, 33, 34, 45, 47, 48, 49, 57, 61, 62]:
        return 3
    elif prefix in [60, 63, 64, 85, 87, 88, 90, 91, 92, 93, 95, 96]:
        return 4
    elif prefix in [10, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 26, 31, 32, 35, 36, 37, 38, 73, 94, 97]:
        return 5
    elif prefix in [65, 67, 70, 71, 72, 74]:
        return 6
    elif prefix in [11, 12, 19, 39, 66, 68, 69, 75, 76]:
        return 7
    elif prefix == 77:
        return 8
    else:
        return None


# In[583]:


def get_zone_estonia(zipcode):
    try:
        zip_int = int(zipcode)
    except:
        return None

    if (
        10000 <= zip_int <= 13999 or
        zip_int == 15000 or
        74000 <= zip_int <= 76999
    ):
        return 1
    elif (
        zip_int == 45000 or
        72000 <= zip_int <= 73999 or
        78000 <= zip_int <= 79999
    ):
        return 2
    elif (
        29000 <= zip_int <= 32999 or
        40000 <= zip_int <= 44999 or
        zip_int == 46000 or
        48000 <= zip_int <= 51999 or
        60000 <= zip_int <= 61999 or
        69000 <= zip_int <= 71999 or
        zip_int == 80000 or
        85000 <= zip_int <= 88999 or
        90000 <= zip_int <= 92999 or
        94000 <= zip_int <= 94999
    ):
        return 3
    elif (
        20000 <= zip_int <= 21999 or
        62000 <= zip_int <= 68999 or
        93000 <= zip_int <= 93999
    ):
        return 4
    else:
        return None


# In[584]:


def get_zone_croatia(zipcode):
    try:
        prefix = int(str(zipcode)[:2])
    except:
        return None

    if prefix == 10:
        return 1
    elif prefix in [42, 44, 47, 49]:
        return 2
    elif prefix in [33, 34, 40, 43, 48, 51, 53]:
        return 3
    elif prefix in [23, 31, 32, 35, 52]:
        return 4
    elif prefix == 22:
        return 5
    elif prefix == 21:
        return 6
    elif prefix == 20:
        return 7
    else:
        return None


# In[585]:


def get_weight_tier(weight):
    if weight < 30:
        return "up to 30 kg"
    elif weight < 50:
        return "up to 50 kg"
    elif weight < 100:
        return "up to 100 kg"
    elif weight < 200:
        return "up to 200 kg"
    elif weight < 300:
        return "up to 300 kg"
    elif weight < 400:
        return "up to 400 kg"
    elif weight < 500:
        return "up to 500 kg"
    elif weight < 600:
        return "up to 600 kg"
    elif weight < 700:
        return "up to 700 kg"
    elif weight < 800:
        return "up to 800 kg"
    elif weight < 900:
        return "up to 900 kg"
    elif weight < 1000:
        return "up to 1000 kg"
    elif weight < 2000:
        return "up to 2000 kg"
    elif weight < 3000:
        return "up to 3000 kg"
    else:
        return "up to 3000 kg"

# ---------- DISTRIBUTORS ----------
def distributor_price_uk(num_pallets):
    standard_prices = {
        1: 246,
        2: 427,
        3: 572,
        4: 750,
        5: 897,
        6: 1052
    }
    

    if num_pallets <= 6:
        return standard_prices.get(num_pallets, None)  # None if not in 1-6
    elif 7 <= num_pallets <= 14:
        return num_pallets * 130
    elif num_pallets >= 15:
        return num_pallets * 109
    else:
        return None


# In[587]:


def distributor_price_ireland(num_pallets):
    standard_prices = {
                1: 210,
                2: 370,
                3: 540,
                4: 716,
                5: 895,
                6: 1070
            }
    
    if num_pallets <= 6:
        return standard_prices.get(num_pallets, None)  # None if not in 1-6
    elif 7 <= num_pallets <= 14:
        return num_pallets * 100
    elif num_pallets >= 15:
        return num_pallets * 80
    else:
        return None


# In[588]:


def distributor_price_norway(num_pallets):
    standard_prices = {
        1: 376,
        2: 650,
        3: 897,
        4: 1164,
        5: 1431,
        6: 1621
    }

    # Dedicated truck pricing
    if num_pallets <= 6:
        return standard_prices.get(num_pallets, None)
    elif 7 <= num_pallets <= 14:
        return num_pallets * 100
    elif num_pallets >= 15:
        return num_pallets * 80
    else:
        return None


# In[589]:


def distributor_price_portugal(num_pallets):
    standard_prices = {
            1: 113,
            2: 178,
            3: 231,
            4: 298,
            5: 358,
            6: 410
        }
    # Dedicated truck pricing
    if num_pallets <= 6:
        return standard_prices.get(num_pallets, None)
    elif 7 <= num_pallets <= 14:
        return num_pallets * 100
    elif num_pallets >= 15:
        return num_pallets * 80
    else:
        return None


# In[590]:


def distributor_price_germany(num_pallets):
    standard_prices = {
            1: 185,
            2: 324,
            3: 460,
            4: 592,
            5: 690,
            6: 810
        }

    # Dedicated truck pricing
    if num_pallets <= 6:
        return standard_prices.get(num_pallets, None)
    elif 7 <= num_pallets <= 14:
        return num_pallets * 100
    elif num_pallets >= 15:
        return num_pallets * 80
    else:
        return None



def get_distributor_price(country, pallets):
    price = None

    if country == "GB":
        price = distributor_price_uk(pallets)
    elif country == "IE":
        price = distributor_price_ireland(pallets)
    elif country == "NO":
        price = distributor_price_norway(pallets)
    elif country == "PT":
        price = distributor_price_portugal(pallets)
    elif country == "DE":
        price = distributor_price_germany(pallets)

    return price if price is not None else None



results = []

for _, row in valid_rows.iterrows():
    weight = row['Gross weight (kgs)']
    zipcode = row['Consignee ZIP Code']
    country = row['Consignee Country']
    country_code = row['Consignee Country / UN Code']
    city = row['Destination']
    num_packages = row['Packages']
    albaran = row["ABO"]

    weight_class = get_weight_tier(weight)
    zone = None

    ##REMOVE THIS LINE TO REMOVE DISTRIBUTOR PRICING. SET PRICE TO NONE 
    price = get_distributor_price(country_code, num_packages)
    #price = None
    
    # Secondary price logic (if distributor price not found)
    if price is None:
        if country_code == "FR":
            zone = get_zone_france(zipcode)
            price = get_price(weight_class, zone, france_price_matrix, weight)
        elif country_code == "BE":
            zone = get_zone_belgium(zipcode)
            price = get_price(weight_class, zone, belgium_price_matrix, weight)
        elif country_code == "CZ":
            zone = get_zone_czech(zipcode)
            price = get_price(weight_class, zone, czech_price_matrix, weight)
        elif country_code == "DK":
            zone = get_zone_denmark(zipcode)
            price = get_price(weight_class, zone, denmark_price_matrix, weight)
        elif country_code == "FI":
            zone = get_zone_finland(zipcode)
            price = get_price(weight_class, zone, finland_price_matrix, weight)
        elif country_code == "DE":
            zone = get_zone_germany(zipcode)
            price = get_price(weight_class, zone, germany_price_matrix, weight)
        elif country_code == "GB":
            zone = get_zone_uk(zipcode)
            price = get_price(weight_class, zone, uk_price_matrix, weight)
        elif country_code == "PL":
            zone = get_zone_poland(zipcode)
            price = get_price(weight_class, zone, poland_price_matrix, weight)
        elif country_code == "IE":
            zone = get_zone_ireland(zipcode)
            price = get_price(weight_class, zone, ireland_price_matrix, weight)
        elif country_code == "NL":
            zone = get_zone_netherlands(zipcode)
            price = get_price(weight_class, zone, netherlands_price_matrix, weight)
        elif country_code == "AT":
            zone = get_zone_austria(zipcode)
            price = get_price(weight_class, zone, austria_price_matrix, weight)
        elif country_code == "CH":
            zone = get_zone_switzerland(zipcode)
            price = get_price(weight_class, zone, switzerland_price_matrix, weight)
        elif country_code == "EE":
            zone = get_zone_estonia(zipcode)
            price = get_price(weight_class, zone, estonia_price_matrix, weight)
        elif country_code == "HR":
            zone = get_zone_croatia(zipcode)
            price = get_price(weight_class, zone, croatia_price_matrix, weight)

    # ✅ Append once (after price calculation is complete)
    if zone is None:
        zone = "N/A (Distributor)"
    
    results.append({
        "ABO": albaran,
        "Volume (m3)": row["Volume (m3)"],
        "Gross weight (kgs)": weight,
        "Packages": num_packages,
        "Destination": f"""{city}, {country}, {zipcode}""",
        "Zone" : zone,
        "KN Invoice Price (€)": row["Spend in EUR"],
        "Calculated Price (€)": price if price else "Rates not available"
    })

# ---------- FINAL RESULT TABLE ----------
final_df = pd.DataFrame(results)

def format_currency(x):
    try:
        return f"€{x:,.2f}"
    except:
        return "N/A"

final_df["KN Invoice Price (€)"] = final_df["KN Invoice Price (€)"].apply(format_currency)
final_df["Calculated Price (€)"] = final_df["Calculated Price (€)"].apply(
    lambda x: format_currency(x) if isinstance(x, (int, float)) else x
)

final_df["Volume (m3)"] = final_df["Volume (m3)"].map(lambda x: f"{x:.3f}")
final_df["Gross weight (kgs)"] = final_df["Gross weight (kgs)"].map(lambda x: f"{x:.3f}")
final_df["Packages"] = final_df["Packages"].map(lambda x: f"{int(x)}")

# Bold final columns

# Highlight headers
def highlight_headers(s):
    return ['font-weight: bold' if col in ["KN Invoice Price (€)", "Calculated Price (€)"] else '' for col in s.index]

# Show result
st.subheader("Cost Comparison")
styled_df = final_df.style.apply(highlight_headers, axis=1)
st.dataframe(styled_df, use_container_width=False, height=35 * len(final_df) + 37)

csv = final_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="kn_albaran_cost_comparison.csv",
    mime="text/csv",
)
