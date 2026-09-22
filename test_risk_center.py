from database import get_risk_center_data

df = get_risk_center_data()

print(df.to_string(index=False))