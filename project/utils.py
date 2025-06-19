import pandas as pd
import os

# 1) Load once at import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'NBA 2k25 Attribute Weights - Sheet1.csv')

# Skip the extra header row if needed; adjust skiprows accordingly
_weights_df = pd.read_csv(CSV_PATH, skiprows=1)

# Convert weight columns to float
for col in ['25-74','75-79','80-84','85-89','90-94','95-98','99']:
    _weights_df[col] = _weights_df[col].astype(float)

def compute_overall(height_inches: int, attrs: dict) -> float:
    """
    height_inches: e.g. 87 for 7'3"
    attrs: {"Three-Point Shot": 93, "Driving Dunk": 73, …}
    """
    # 2) Map inches back to the "7'3" style string in CSV
    feet, inch = divmod(height_inches, 12)
    height_str = f"{feet}'{inch}"
    subset = _weights_df[_weights_df['Height'] == height_str]
    total = 0.0
    for name, val in attrs.items():
        # 3) Pick the correct weight column
        if val <= 74:
            col = '25-74'
        elif val <= 79:
            col = '75-79'
        elif val <= 84:
            col = '80-84'
        elif val <= 89:
            col = '85-89'
        elif val <= 94:
            col = '90-94'
        elif val <= 98:
            col = '95-98'
        else:
            col = '99'
        # 4) Look up that attribute’s weight
        row = subset[subset['Attribute'] == name]
        weight = float(row[col].iloc[0]) if not row.empty else 0.0
        total += weight
    return total
