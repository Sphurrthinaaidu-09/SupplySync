from database import (
    get_total_orders,
    get_otif_percentage,
    get_products_at_risk,
    get_critical_risk_count
)


print("Total Orders:", get_total_orders())

print("OTIF %:", get_otif_percentage())

print("Products at Risk:", get_products_at_risk())

print("Critical Risks:", get_critical_risk_count())