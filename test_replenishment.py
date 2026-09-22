from database import get_replenishment_recommendations

data = get_replenishment_recommendations()

for row in data:
    print(row)