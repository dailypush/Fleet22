import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

# Load the JSON file
file_path = '../data/sail_tags.json'  # Update this path
df_updated = pd.read_json(file_path)

# Convert "Delivery Date" to datetime and "Fleet" to string for proper filtering
df_updated["Delivery Date"] = pd.to_datetime(df_updated["Delivery Date"], errors='coerce')
df_updated = df_updated.dropna(subset=["Delivery Date"])  # Drop rows where 'Delivery Date' is NaT
df_updated["Fleet"] = df_updated["Fleet"].astype(str)

# Filter the dataset for Fleet 22
fleet_22_hulls = df_updated[df_updated['Fleet'] == '22']

# Unique hulls within Fleet 22
unique_hulls = fleet_22_hulls['Hull'].unique()

# Output directory for the heatmaps
output_dir = './heatmaps'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# For demonstration, we'll generate heat maps for up to 5 hulls due to space and processing limitations
for hull in tqdm(unique_hulls[:12], desc="Generating Heatmaps"):
    logging.info(f"Processing Hull {hull}")
    hull_data = fleet_22_hulls[fleet_22_hulls['Hull'] == hull]
    hull_purchases_detailed = hull_data.groupby([hull_data['Delivery Date'].dt.year, 'Sail Type', 'Sailmaker']).size().unstack(level=[1,2], fill_value=0)
    hull_purchases_detailed.columns = [' '.join(col).strip() for col in hull_purchases_detailed.columns.values]
    
    # Plotting the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(hull_purchases_detailed.T, cmap="YlGnBu", annot=True, fmt="d", cbar_kws={'label': 'Number of Purchases'})
    plt.title(f'Purchases for Hull {hull} by Year, Sail Type, and Sailmaker')
    plt.xlabel('Year')
    plt.ylabel('Sail Type and Sailmaker')
    plt.tight_layout()
    
    # Save the heatmap to a PNG file
    file_name = os.path.join(output_dir, f'hull_{hull}_heatmap.png')
    plt.savefig(file_name)
    logging.info(f"Successfully saved heatmap for Hull {hull}")
    # Close the figure to free memory
    plt.close()
