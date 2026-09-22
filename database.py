import psycopg2
import pandas as pd


# ============================================================
# DATABASE CONNECTION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "supplysync",
    "user": "postgres",
    "password": "SupplySync@2026",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def _read_sql(query, params=None):
    connection = get_db_connection()
    try:
        return pd.read_sql(query, connection, params=params)
    finally:
        connection.close()


def _records(query, params=None):
    return _read_sql(query, params).to_dict(orient="records")


# ============================================================
# DASHBOARD / CONTROL TOWER
# ============================================================

def get_total_orders():
    df = _read_sql("""
        SELECT COUNT(*) AS total_orders
        FROM plastic.fact_orders;
    """)
    return int(df.iloc[0]["total_orders"])


def get_otif_percentage():
    df = _read_sql("""
        WITH line_metrics AS (
            SELECT
                fol.order_line_id,
                fol.ordered_qty_kg,
                COALESCE(SUM(fd.delivered_qty), 0) AS delivered_qty,
                fo.requested_delivery_date,
                MAX(fd.delivery_date) AS actual_delivery_date
            FROM plastic.fact_order_lines fol
            JOIN plastic.fact_orders fo
                ON fo.order_id = fol.order_id
            LEFT JOIN plastic.fact_deliveries fd
                ON fd.order_line_id = fol.order_line_id
            GROUP BY
                fol.order_line_id,
                fol.ordered_qty_kg,
                fo.requested_delivery_date
        )
        SELECT COALESCE(
            ROUND(
                AVG(
                    CASE
                        WHEN delivered_qty >= ordered_qty_kg
                         AND actual_delivery_date <= requested_delivery_date
                        THEN 1.0 ELSE 0.0
                    END
                ) * 100, 2
            ), 0
        ) AS otif_percentage
        FROM line_metrics;
    """)
    return float(df.iloc[0]["otif_percentage"])


def get_products_at_risk():
    df = _read_sql("""
        SELECT COUNT(*) AS products_at_risk
        FROM plastic.risk_assessments
        WHERE risk_level IN ('Critical', 'High');
    """)
    return int(df.iloc[0]["products_at_risk"])


def get_critical_risk_count():
    df = _read_sql("""
        SELECT COUNT(*) AS critical_risks
        FROM plastic.risk_assessments
        WHERE risk_level = 'Critical';
    """)
    return int(df.iloc[0]["critical_risks"])


def get_supply_chain_health():
    df = _read_sql("""
        SELECT
            COUNT(*) FILTER (WHERE risk_level = 'Critical') AS critical,
            COUNT(*) FILTER (WHERE risk_level = 'High') AS high,
            COUNT(*) FILTER (WHERE risk_level = 'Medium') AS medium,
            COUNT(*) FILTER (WHERE risk_level = 'Low') AS low
        FROM plastic.risk_assessments;
    """)

    critical = int(df.iloc[0]["critical"])
    high = int(df.iloc[0]["high"])
    medium = int(df.iloc[0]["medium"])
    low = int(df.iloc[0]["low"])

    if critical > 0:
        overall_status = "Critical"
    elif high > 0:
        overall_status = "High Risk"
    elif medium > 0:
        overall_status = "Attention Required"
    else:
        overall_status = "Healthy"

    return {
        "overall_status": overall_status,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
    }


# ============================================================
# INVENTORY / REPLENISHMENT
# ============================================================

def get_inventory_risks():
    return _records("""
        SELECT
            fi.material_id,
            fi.product_id,
            COALESCE(m.material_name, p.product_name) AS item_name,
            COALESCE(fi.material_id, fi.product_id) AS item_id,
            fi.closing_qty_kg AS available_qty,
            dip.reorder_point_kg,
            dip.safety_stock_kg,
            dip.lead_time_days,
            ROUND(
                GREATEST(0, dip.reorder_point_kg - fi.closing_qty_kg),
                2
            ) AS inventory_shortfall,
            fi.inventory_status,
            CASE
                WHEN fi.closing_qty_kg < dip.safety_stock_kg THEN 'Critical'
                WHEN fi.closing_qty_kg < dip.reorder_point_kg THEN 'At Risk'
                ELSE 'Healthy'
            END AS risk_status
        FROM plastic.fact_inventory fi
        LEFT JOIN plastic.dim_materials m
            ON fi.material_id = m.material_id
        LEFT JOIN plastic.dim_products p
            ON fi.product_id = p.product_id
        LEFT JOIN plastic.dim_inventory_policies dip
            ON fi.warehouse_id = dip.warehouse_id
           AND fi.material_id = dip.material_id
        WHERE
            fi.material_id IS NOT NULL
            AND dip.material_id IS NOT NULL
        ORDER BY
            CASE
                WHEN fi.closing_qty_kg < dip.safety_stock_kg THEN 1
                WHEN fi.closing_qty_kg < dip.reorder_point_kg THEN 2
                ELSE 3
            END,
            inventory_shortfall DESC;
    """)


def get_stockout_exposure():
    return _records("""
        WITH demand AS (
            SELECT
                fol.product_id,
                SUM(fol.ordered_qty_kg) AS total_demand,
                COUNT(DISTINCT fo.order_date) AS active_days
            FROM plastic.fact_order_lines fol
            JOIN plastic.fact_orders fo
                ON fo.order_id = fol.order_id
            GROUP BY fol.product_id
        ),
        inventory AS (
            SELECT
                fi.product_id,
                fi.closing_qty_kg AS available_qty
            FROM plastic.fact_inventory fi
            WHERE fi.product_id IS NOT NULL
        )
        SELECT
            i.product_id,
            p.product_name,
            i.available_qty,
            ROUND(
                COALESCE(d.total_demand / NULLIF(d.active_days, 0), 0),
                2
            ) AS avg_daily_demand,
            ROUND(
                i.available_qty /
                NULLIF(d.total_demand / NULLIF(d.active_days, 0), 0),
                2
            ) AS days_of_inventory,
            ROUND(
                GREATEST(
                    0,
                    (d.total_demand / NULLIF(d.active_days, 0)) * 7
                    - i.available_qty
                ),
                2
            ) AS stockout_exposure,
            CASE
                WHEN i.available_qty <
                     (d.total_demand / NULLIF(d.active_days, 0)) * 7
                THEN 'At Risk'
                ELSE 'Covered'
            END AS stockout_status
        FROM inventory i
        JOIN plastic.dim_products p
            ON i.product_id = p.product_id
        JOIN demand d
            ON i.product_id = d.product_id
        ORDER BY stockout_exposure DESC;
    """)


def get_replenishment_recommendations():
    return _records("""
        WITH latest_inventory AS (
            SELECT
                fi.material_id,
                fi.warehouse_id,
                fi.closing_qty_kg,
                ROW_NUMBER() OVER (
                    PARTITION BY fi.material_id, fi.warehouse_id
                    ORDER BY fi.inventory_date DESC, fi.inventory_id DESC
                ) AS rn
            FROM plastic.fact_inventory fi
            WHERE fi.material_id IS NOT NULL
        ),
        inventory_position AS (
            SELECT
                li.material_id,
                SUM(li.closing_qty_kg) AS available_qty,
                SUM(COALESCE(dip.reorder_point_kg, 0)) AS reorder_point_qty,
                SUM(
                    GREATEST(
                        0,
                        COALESCE(dip.reorder_point_kg, 0)
                        - li.closing_qty_kg
                    )
                ) AS inventory_shortfall,
                MAX(dip.lead_time_days) AS lead_time_days
            FROM latest_inventory li
            LEFT JOIN plastic.dim_inventory_policies dip
                ON li.warehouse_id = dip.warehouse_id
               AND li.material_id = dip.material_id
            WHERE li.rn = 1
            GROUP BY li.material_id
        )
        SELECT
            dr.recommendation_id,
            dr.recommendation_date,
            dr.risk_id,
            dr.reference_type,
            dr.reference_id,
            dr.recommendation_type,
            dr.priority,
            COALESCE(
                m.material_name,
                dr.reference_id
            ) AS product_name,
            ip.available_qty,
            ip.reorder_point_qty,
            ip.inventory_shortfall,
            ip.lead_time_days,
            dr.recommended_action,
            dr.recommended_qty AS recommended_order_qty,
            dr.recommended_supplier_id AS supplier_id,
            s.supplier_name,
            dr.estimated_cost,
            dr.rationale,
            dr.recommendation_status AS status,
            ra.risk_score,
            ra.risk_level
        FROM plastic.decision_recommendations dr
        LEFT JOIN plastic.dim_materials m
            ON dr.reference_type = 'Material'
           AND dr.reference_id = m.material_id
        LEFT JOIN inventory_position ip
            ON dr.reference_id = ip.material_id
           AND dr.reference_type = 'Material'
        LEFT JOIN plastic.dim_suppliers s
            ON dr.recommended_supplier_id = s.supplier_id
        LEFT JOIN plastic.risk_assessments ra
            ON dr.risk_id = ra.risk_id
        WHERE dr.recommendation_type = 'Replenishment'
        ORDER BY
            CASE dr.priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            dr.estimated_cost DESC NULLS LAST;
    """)


# ============================================================
# DEMAND / FORECASTS
# ============================================================

def get_product_demand():
    return _records("""
        SELECT
            fol.product_id,
            p.product_name,
            SUM(fol.ordered_qty_kg) AS total_demand,
            COUNT(DISTINCT fo.order_date) AS active_days,
            ROUND(
                SUM(fol.ordered_qty_kg) /
                NULLIF(COUNT(DISTINCT fo.order_date), 0),
                2
            ) AS avg_daily_demand,
            MIN(fol.ordered_qty_kg) AS min_order_qty,
            MAX(fol.ordered_qty_kg) AS max_order_qty
        FROM plastic.fact_order_lines fol
        JOIN plastic.fact_orders fo
            ON fo.order_id = fol.order_id
        JOIN plastic.dim_products p
            ON fol.product_id = p.product_id
        GROUP BY fol.product_id, p.product_name
        ORDER BY avg_daily_demand DESC;
    """)


def get_forecast_results():
    return _records("""
        SELECT
            fr.forecast_id,
            fr.forecast_date,
            fr.forecast_period_start,
            fr.forecast_period_end,
            fr.product_id,
            p.product_name,
            fr.material_id,
            m.material_name,
            fr.forecast_qty,
            fr.forecast_unit,
            fr.confidence_pct,
            fr.forecast_method,
            fr.planning_signal
        FROM plastic.forecast_results fr
        LEFT JOIN plastic.dim_products p
            ON fr.product_id = p.product_id
        LEFT JOIN plastic.dim_materials m
            ON fr.material_id = m.material_id
        ORDER BY fr.forecast_qty DESC;
    """)


# ============================================================
# PROCUREMENT / SUPPLIERS
# ============================================================

def get_supplier_performance():
    return _records("""
        WITH supplier_metrics AS (
            SELECT
                po.supplier_id,
                COUNT(DISTINCT po.po_id) AS total_purchase_orders,
                COUNT(DISTINCT r.receipt_id) AS total_receipts,
                COALESCE(SUM(pol.ordered_qty_kg), 0) AS ordered_qty_kg,
                COALESCE(SUM(r.received_qty_kg), 0) AS received_qty_kg,
                COALESCE(SUM(r.accepted_qty_kg), 0) AS accepted_qty_kg,
                COALESCE(SUM(r.rejected_qty_kg), 0) AS rejected_qty_kg,
                COALESCE(
                    AVG(
                        CASE
                            WHEN r.receipt_date <= po.expected_delivery_date
                            THEN 100 ELSE 0
                        END
                    ), 0
                ) AS on_time_rate
            FROM plastic.purchase_orders po
            JOIN plastic.purchase_order_lines pol
                ON po.po_id = pol.po_id
            LEFT JOIN plastic.fact_material_receipts r
                ON pol.po_line_id = r.po_line_id
            GROUP BY po.supplier_id
        )
        SELECT
            s.supplier_id,
            s.supplier_name,
            s.supplier_category,
            s.city,
            s.region,
            sm.total_purchase_orders,
            sm.total_receipts,
            sm.ordered_qty_kg,
            sm.received_qty_kg,
            sm.accepted_qty_kg,
            sm.rejected_qty_kg,
            ROUND(
                sm.received_qty_kg / NULLIF(sm.ordered_qty_kg, 0) * 100,
                2
            ) AS fill_rate,
            ROUND(
                (
                    sm.accepted_qty_kg
                    / NULLIF(sm.ordered_qty_kg, 0)
                ) * sm.on_time_rate,
                2
            ) AS otif_rate
        FROM plastic.dim_suppliers s
        LEFT JOIN supplier_metrics sm
            ON s.supplier_id = sm.supplier_id
        WHERE s.is_active = TRUE
        ORDER BY fill_rate ASC NULLS LAST;
    """)


def get_supplier_comparison():
    return _records("""
        SELECT
            sm.supplier_id,
            s.supplier_name,
            s.supplier_category,
            s.city,
            s.region,
            sm.material_id,
            m.material_name,
            sm.supplier_material_grade,
            sm.typical_price_per_kg,
            sm.usable_yield_pct,
            sm.is_preferred,
            sm.is_active
        FROM plastic.supplier_material sm
        JOIN plastic.dim_suppliers s
            ON s.supplier_id = sm.supplier_id
        JOIN plastic.dim_materials m
            ON m.material_id = sm.material_id
        WHERE sm.is_active = TRUE
        ORDER BY
            sm.material_id,
            sm.typical_price_per_kg ASC,
            sm.usable_yield_pct DESC;
    """)


def get_supplier_risk_summary():
    return _records("""
        WITH receipt_metrics AS (
            SELECT
                supplier_id,
                COUNT(*) AS total_receipts,
                SUM(received_qty_kg) AS received_qty,
                SUM(accepted_qty_kg) AS accepted_qty,
                SUM(rejected_qty_kg) AS rejected_qty
            FROM plastic.fact_material_receipts
            GROUP BY supplier_id
        ),
        delivery_metrics AS (
            SELECT
                po.supplier_id,
                COUNT(*) FILTER (
                    WHERE r.receipt_date > po.expected_delivery_date
                ) AS delayed_receipts
            FROM plastic.purchase_orders po
            JOIN plastic.purchase_order_lines pol
                ON po.po_id = pol.po_id
            JOIN plastic.fact_material_receipts r
                ON pol.po_line_id = r.po_line_id
            GROUP BY po.supplier_id
        )
        SELECT
            s.supplier_id,
            s.supplier_name,
            s.supplier_category,
            COALESCE(rm.total_receipts, 0) AS total_receipts,
            COALESCE(rm.received_qty, 0) AS total_received_qty,
            COALESCE(rm.accepted_qty, 0) AS total_accepted_qty,
            COALESCE(rm.rejected_qty, 0) AS total_rejected_qty,
            ROUND(
                rm.accepted_qty / NULLIF(rm.received_qty, 0) * 100,
                2
            ) AS acceptance_rate,
            COALESCE(dm.delayed_receipts, 0) AS delayed_receipts,
            CASE
                WHEN COALESCE(dm.delayed_receipts, 0) > 0
                 AND COALESCE(rm.rejected_qty, 0) > 0 THEN 'High'
                WHEN COALESCE(dm.delayed_receipts, 0) > 0
                  OR COALESCE(rm.rejected_qty, 0) > 0 THEN 'Medium'
                ELSE 'Low'
            END AS supplier_risk_level
        FROM plastic.dim_suppliers s
        LEFT JOIN receipt_metrics rm
            ON s.supplier_id = rm.supplier_id
        LEFT JOIN delivery_metrics dm
            ON s.supplier_id = dm.supplier_id
        WHERE s.is_active = TRUE
        ORDER BY
            CASE
                WHEN COALESCE(dm.delayed_receipts, 0) > 0
                 AND COALESCE(rm.rejected_qty, 0) > 0 THEN 1
                WHEN COALESCE(dm.delayed_receipts, 0) > 0
                  OR COALESCE(rm.rejected_qty, 0) > 0 THEN 2
                ELSE 3
            END,
            total_rejected_qty DESC;
    """)


def get_cost_analysis():
    return _records("""
        SELECT
            sm.material_id,
            m.material_name,
            sm.supplier_id,
            s.supplier_name,
            sm.typical_price_per_kg,
            sm.usable_yield_pct,
            CASE
                WHEN sm.usable_yield_pct > 0
                THEN ROUND(
                    (sm.typical_price_per_kg / (sm.usable_yield_pct / 100.0))::numeric,
                    2
                )
                ELSE NULL
            END AS yield_adjusted_cost,
            sm.is_preferred
        FROM plastic.supplier_material sm
        JOIN plastic.dim_materials m
            ON m.material_id = sm.material_id
        JOIN plastic.dim_suppliers s
            ON s.supplier_id = sm.supplier_id
        WHERE sm.is_active = TRUE
        ORDER BY yield_adjusted_cost DESC NULLS LAST;
    """)


# ============================================================
# ORDERS / CUSTOMER SERVICE / OTIF
# ============================================================

def get_otif_performance():
    return _records("""
        WITH line_metrics AS (
            SELECT
                fo.order_id,
                fo.customer_id,
                fol.order_line_id,
                fol.ordered_qty_kg,
                COALESCE(SUM(fd.delivered_qty), 0) AS delivered_qty,
                fo.requested_delivery_date,
                MAX(fd.delivery_date) AS actual_delivery_date
            FROM plastic.fact_orders fo
            JOIN plastic.fact_order_lines fol
                ON fo.order_id = fol.order_id
            LEFT JOIN plastic.fact_deliveries fd
                ON fol.order_line_id = fd.order_line_id
            GROUP BY
                fo.order_id,
                fo.customer_id,
                fol.order_line_id,
                fol.ordered_qty_kg,
                fo.requested_delivery_date
        ),
        customer_metrics AS (
            SELECT
                customer_id,
                COUNT(DISTINCT order_id) AS total_orders,
                AVG(
                    CASE WHEN actual_delivery_date <= requested_delivery_date
                         THEN 1.0 ELSE 0.0 END
                ) AS on_time_rate,
                AVG(
                    CASE WHEN delivered_qty >= ordered_qty_kg
                         THEN 1.0 ELSE 0.0 END
                ) AS in_full_rate,
                AVG(
                    CASE WHEN delivered_qty >= ordered_qty_kg
                           AND actual_delivery_date <= requested_delivery_date
                         THEN 1.0 ELSE 0.0 END
                ) AS otif_rate
            FROM line_metrics
            GROUP BY customer_id
        )
        SELECT
            cm.customer_id,
            c.customer_name,
            c.customer_type,
            cm.total_orders,
            ROUND(cm.on_time_rate * 100, 2) AS on_time_rate,
            ROUND(cm.in_full_rate * 100, 2) AS in_full_rate,
            ROUND(cm.otif_rate * 100, 2) AS otif_rate,
            95.0 AS on_time_target,
            95.0 AS in_full_target,
            90.0 AS otif_target,
            ROUND(cm.otif_rate * 100 - 90.0, 2) AS otif_gap
        FROM customer_metrics cm
        JOIN plastic.dim_customers c
            ON cm.customer_id = c.customer_id
        ORDER BY otif_gap ASC;
    """)


def get_order_performance():
    return _records("""
        WITH metrics AS (
            SELECT
                fo.order_id,
                fo.customer_id,
                fo.order_date,
                fo.requested_delivery_date,
                fo.order_status,
                SUM(fol.ordered_qty_kg) AS ordered_qty,
                COALESCE(SUM(fd.delivered_qty), 0) AS delivered_qty,
                MAX(fd.delivery_date) AS actual_delivery_date
            FROM plastic.fact_orders fo
            JOIN plastic.fact_order_lines fol
                ON fo.order_id = fol.order_id
            LEFT JOIN plastic.fact_deliveries fd
                ON fol.order_line_id = fd.order_line_id
            GROUP BY
                fo.order_id,
                fo.customer_id,
                fo.order_date,
                fo.requested_delivery_date,
                fo.order_status
        )
        SELECT
            m.order_id,
            c.customer_name,
            m.order_date,
            m.requested_delivery_date,
            m.actual_delivery_date,
            m.ordered_qty,
            m.delivered_qty,
            ROUND(
                m.delivered_qty / NULLIF(m.ordered_qty, 0) * 100,
                2
            ) AS fulfillment_rate,
            CASE
                WHEN m.delivered_qty >= m.ordered_qty
                 AND m.actual_delivery_date <= m.requested_delivery_date
                    THEN 'OTIF'
                WHEN m.actual_delivery_date <= m.requested_delivery_date
                    THEN 'On Time - Short'
                WHEN m.delivered_qty >= m.ordered_qty
                    THEN 'Late - Full'
                ELSE 'Late - Short'
            END AS service_status,
            m.order_status
        FROM metrics m
        JOIN plastic.dim_customers c
            ON m.customer_id = c.customer_id
        ORDER BY
            CASE
                WHEN m.delivered_qty < m.ordered_qty
                  AND m.actual_delivery_date > m.requested_delivery_date THEN 1
                WHEN m.delivered_qty < m.ordered_qty THEN 2
                WHEN m.actual_delivery_date > m.requested_delivery_date THEN 3
                ELSE 4
            END,
            m.order_date;
    """)


# ============================================================
# RISK CENTER / DECISION INTELLIGENCE
# ============================================================

def get_supply_risks():
    return _records("""
        SELECT
            ra.risk_id,
            ra.assessment_date,
            ra.risk_type,
            ra.reference_type,
            ra.reference_id,
            COALESCE(
                p.product_name,
                m.material_name,
                s.supplier_name,
                ra.reference_id
            ) AS item_name,
            ra.risk_score,
            ra.risk_level,
            ra.risk_reason,
            ra.recommended_action,
            dr.recommendation_type,
            dr.priority AS recommendation_priority,
            dr.recommended_action AS decision_action,
            dr.recommended_qty,
            dr.recommended_supplier_id,
            rs.supplier_name AS recommended_supplier_name,
            dr.estimated_cost,
            dr.rationale,
            dr.recommendation_status
        FROM plastic.risk_assessments ra
        LEFT JOIN plastic.dim_products p
            ON ra.reference_type = 'Product'
           AND ra.reference_id = p.product_id
        LEFT JOIN plastic.dim_materials m
            ON ra.reference_type = 'Material'
           AND ra.reference_id = m.material_id
        LEFT JOIN plastic.dim_suppliers s
            ON ra.reference_type = 'Supplier'
           AND ra.reference_id = s.supplier_id
        LEFT JOIN plastic.decision_recommendations dr
            ON ra.risk_id = dr.risk_id
        LEFT JOIN plastic.dim_suppliers rs
            ON dr.recommended_supplier_id = rs.supplier_id
        ORDER BY ra.risk_score DESC, ra.risk_id;
    """)


def get_critical_risks():
    return _read_sql("""
        SELECT
            ra.risk_id,
            ra.assessment_date,
            ra.risk_type,
            ra.reference_type,
            ra.reference_id,
            COALESCE(
                p.product_name,
                m.material_name,
                s.supplier_name,
                ra.reference_id
            ) AS item_name,
            ra.risk_score,
            ra.risk_level,
            ra.risk_reason,
            ra.recommended_action,
            dr.recommendation_type,
            dr.priority,
            dr.recommended_action AS decision_action,
            dr.recommended_qty,
            dr.estimated_cost,
            dr.recommendation_status
        FROM plastic.risk_assessments ra
        LEFT JOIN plastic.dim_products p
            ON ra.reference_type = 'Product'
           AND ra.reference_id = p.product_id
        LEFT JOIN plastic.dim_materials m
            ON ra.reference_type = 'Material'
           AND ra.reference_id = m.material_id
        LEFT JOIN plastic.dim_suppliers s
            ON ra.reference_type = 'Supplier'
           AND ra.reference_id = s.supplier_id
        LEFT JOIN plastic.decision_recommendations dr
            ON ra.risk_id = dr.risk_id
        WHERE ra.risk_level = 'Critical'
        ORDER BY ra.risk_score DESC;
    """)


def get_risk_center_data():
    return _read_sql("""
        SELECT
            ra.risk_id,
            ra.assessment_date,
            ra.risk_type,
            ra.reference_type,
            ra.reference_id,
            COALESCE(
                p.product_name,
                m.material_name,
                ra.reference_id
            ) AS product_name,
            COALESCE(
                p.product_name,
                m.material_name,
                s.supplier_name,
                ra.reference_id
            ) AS item_name,
            COALESCE(
                rs.supplier_name,
                s.supplier_name
            ) AS supplier_name,
            ra.risk_score,
            ra.risk_level,
            ra.risk_reason,
            ra.recommended_action,
            dr.recommendation_type,
            dr.priority,
            dr.recommended_action AS decision_action,
            dr.recommended_qty,
            dr.recommended_supplier_id,
            rs.supplier_name AS recommended_supplier_name,
            dr.estimated_cost,
            dr.rationale,
            dr.recommendation_status
        FROM plastic.risk_assessments ra
        LEFT JOIN plastic.dim_products p
            ON ra.reference_type = 'Product'
           AND ra.reference_id = p.product_id
        LEFT JOIN plastic.dim_materials m
            ON ra.reference_type = 'Material'
           AND ra.reference_id = m.material_id
        LEFT JOIN plastic.dim_suppliers s
            ON ra.reference_type = 'Supplier'
           AND ra.reference_id = s.supplier_id
        LEFT JOIN plastic.decision_recommendations dr
            ON ra.risk_id = dr.risk_id
        LEFT JOIN plastic.dim_suppliers rs
            ON dr.recommended_supplier_id = rs.supplier_id
        ORDER BY
            CASE ra.risk_level
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            ra.risk_score DESC;
    """)


def get_decision_recommendations():
    return _records("""
        SELECT
            dr.recommendation_id,
            dr.recommendation_date,
            dr.risk_id,
            dr.recommendation_type,
            dr.reference_type,
            dr.reference_id,
            dr.priority,
            dr.recommended_action,
            dr.recommended_qty,
            dr.recommended_supplier_id,
            s.supplier_name,
            dr.estimated_cost,
            dr.rationale,
            dr.recommendation_status,
            ra.risk_score,
            ra.risk_level,
            ra.risk_reason
        FROM plastic.decision_recommendations dr
        LEFT JOIN plastic.dim_suppliers s
            ON dr.recommended_supplier_id = s.supplier_id
        LEFT JOIN plastic.risk_assessments ra
            ON dr.risk_id = ra.risk_id
        ORDER BY
            CASE dr.priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            dr.recommendation_id;
    """)

def get_production_performance():
    query = """
        SELECT
            p.production_id,
            p.production_date,
            p.batch_id,
            p.process_stage,
            p.input_material_id,
            m.material_name AS input_material_name,
            p.input_qty_kg,
            p.output_product_id,
            pr.product_name AS output_product_name,
            p.output_qty_kg,
            p.process_loss_kg,
            p.yield_pct,
            p.machine_hours,
            p.energy_kwh,
            p.production_status,
            p.rejection_qty_kg,
            p.rejection_reason
        FROM plastic.fact_production p
        JOIN plastic.dim_materials m
            ON p.input_material_id = m.material_id
        JOIN plastic.dim_products pr
            ON p.output_product_id = pr.product_id
        ORDER BY
            p.production_date,
            p.production_id;
    """

    return _records(query)

# ============================================================
# DATA INGESTION — PLASTIC SUPPLY CHAIN
# ============================================================

PLASTIC_UPLOAD_TABLES = [
    "dim_suppliers",
    "dim_materials",
    "dim_products",
    "dim_customers",
    "dim_warehouses",
    "supplier_material",
    "purchase_orders",
    "purchase_order_lines",
    "fact_material_receipts",
    "fact_material_quality",
    "fact_production",
    "fact_inventory",
    "dim_inventory_policies",
    "fact_orders",
    "fact_order_lines",
    "fact_deliveries",
    "risk_assessments",
    "decision_recommendations",
    "forecast_results",
    "dim_date",
]


def _get_table_metadata(table_name):
    """
    Return insertable columns for a table in the plastic schema.

    Generated columns and identity/auto-generated columns are excluded
    because PostgreSQL should generate them automatically.
    """
    connection = get_db_connection()

    query = """
        SELECT
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            is_identity,
            identity_generation,
            is_generated,
            generation_expression
        FROM information_schema.columns
        WHERE table_schema = 'plastic'
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    try:
        df = pd.read_sql(query, connection, params=(table_name,))
    finally:
        connection.close()

    if df.empty:
        raise ValueError(
            f"Table plastic.{table_name} does not exist."
        )

    # Do not allow generated columns to be inserted.
    df = df[
        (df["is_generated"] == "NEVER")
        & (df["generation_expression"].isna())
    ].copy()

    # Identity columns are generated by PostgreSQL.
    df = df[df["is_identity"] != "YES"].copy()

    return df


def _get_primary_key_columns(table_name):
    """
    Return primary-key columns for plastic.<table_name>.
    """
    connection = get_db_connection()

    query = """
        SELECT
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
         AND tc.table_name = kcu.table_name
        WHERE tc.table_schema = 'plastic'
          AND tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position;
    """

    try:
        df = pd.read_sql(query, connection, params=(table_name,))
    finally:
        connection.close()

    return df["column_name"].tolist()


def get_supported_upload_schemas():
    """
    Return the currently supported plastic-schema upload contracts.

    Tables are read dynamically from PostgreSQL so the ingestion layer
    stays aligned with the actual database schema.
    """
    schemas = {}

    for table_name in PLASTIC_UPLOAD_TABLES:
        metadata = _get_table_metadata(table_name)

        required_columns = set(
            metadata[
            (metadata["is_nullable"] == "NO")
            & (metadata["column_default"].isna())
            ]["column_name"].tolist()
        )

        insertable_columns = set(
            metadata["column_name"].tolist()
        )

        schemas[table_name] = {
            "required": required_columns,
            "columns": insertable_columns,
        }

    return schemas


def detect_plastic_dataset(columns):
    """
    Identify which plastic table best matches an uploaded CSV.
    """
    uploaded_columns = {
        str(column).strip()
        for column in columns
    }

    schemas = get_supported_upload_schemas()

    matches = []

    for table_name, contract in schemas.items():
        required = contract["required"]
        allowed = contract["columns"]

        if required.issubset(uploaded_columns):
            unknown_columns = uploaded_columns - allowed

            if not unknown_columns:
                matches.append(table_name)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        # Prefer the table with the largest required schema.
        return max(
            matches,
            key=lambda name: len(schemas[name]["required"])
        )

    return None


def validate_plastic_upload(table_name, df):
    """
    Validate an uploaded dataframe against plastic.<table_name>.
    """
    if table_name not in PLASTIC_UPLOAD_TABLES:
        raise ValueError(
            f"Dataset '{table_name}' is not enabled for SupplySync ingestion."
        )

    if df is None or df.empty:
        raise ValueError("The uploaded CSV contains no records.")

    metadata = _get_table_metadata(table_name)

    allowed_columns = set(metadata["column_name"].tolist())

    required_columns = set(
        metadata[
            (metadata["is_nullable"] == "NO")
            & (metadata["column_default"].isna())
        ]["column_name"].tolist()
    )
    uploaded_columns = {
        str(column).strip()
        for column in df.columns
    }

    missing_columns = required_columns - uploaded_columns
    unknown_columns = uploaded_columns - allowed_columns

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if unknown_columns:
        raise ValueError(
            "Unknown columns for "
            f"plastic.{table_name}: "
            + ", ".join(sorted(unknown_columns))
        )

    # Remove accidental whitespace from column names.
    cleaned_df = df.copy()
    cleaned_df.columns = [
        str(column).strip()
        for column in cleaned_df.columns
    ]

    # Empty strings should behave like NULL.
    cleaned_df = cleaned_df.replace(
        r"^\s*$",
        None,
        regex=True
    )

    # Remove exact duplicate rows inside the uploaded file.
    duplicate_rows = int(cleaned_df.duplicated().sum())

    cleaned_df = cleaned_df.drop_duplicates(
        keep="last"
    ).reset_index(drop=True)

    # Check required columns for missing values.
    invalid_required = []

    for column in required_columns:
        if column not in cleaned_df.columns:
            continue

        if cleaned_df[column].isna().any():
            invalid_required.append(column)

    if invalid_required:
        raise ValueError(
            "Required columns contain missing values: "
            + ", ".join(sorted(invalid_required))
        )

    return {
    "valid": True,
    "errors": [],
    "warnings": [],
    "data": cleaned_df,
    "received": len(df),
    "validated": len(cleaned_df),
    "duplicate_rows_in_file": duplicate_rows,
    }


def _python_value(value):
    """
    Convert pandas values into PostgreSQL-safe Python values.
    """
    if pd.isna(value):
        return None

    # Convert pandas Timestamp to Python datetime.
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    # Convert pandas integer/float/numpy scalar values.
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def _rows_are_identical(existing_row, incoming_row, columns):
    """
    Compare two database rows while treating NULL/NaN as equivalent.
    """
    for column in columns:
        existing_value = existing_row.get(column)
        incoming_value = incoming_row.get(column)

        if pd.isna(existing_value) and pd.isna(incoming_value):
            continue

        if existing_value != incoming_value:
            return False

    return True


def load_plastic_table_data(table_name, df):
    """
    Safely load a validated dataframe into plastic.<table_name>.

    Duplicate protection:
    1. Exact duplicate rows inside the uploaded file are removed.
    2. Existing identical database rows are skipped.
    3. Existing rows with the same primary key are updated only for
       controlled master/configuration tables.
    4. Historical fact rows are not silently overwritten.
    """
    validation = validate_plastic_upload(table_name, df)

    clean_df = validation["data"]

    metadata = _get_table_metadata(table_name)
    insertable_columns = metadata["column_name"].tolist()

    # Keep only columns that PostgreSQL accepts.
    upload_columns = [
        column
        for column in clean_df.columns
        if column in insertable_columns
    ]

    if not upload_columns:
        raise ValueError(
            f"No insertable columns were found for plastic.{table_name}."
        )

    pk_columns = _get_primary_key_columns(table_name)

    # Tables where an existing record may safely be updated.
    update_existing_tables = {
        "dim_suppliers",
        "dim_materials",
        "dim_products",
        "dim_customers",
        "dim_warehouses",
        "supplier_material",
        "purchase_orders",
        "purchase_order_lines",
        "dim_inventory_policies",
        "forecast_results",
    }

    connection = get_db_connection()

    inserted = 0
    updated = 0
    skipped = 0

    try:
        cursor = connection.cursor()

        quoted_columns = ", ".join(
            f'"{column}"'
            for column in upload_columns
        )

        placeholders = ", ".join(
            ["%s"] * len(upload_columns)
        )

        insert_sql = f"""
            INSERT INTO plastic.{table_name}
            ({quoted_columns})
            VALUES ({placeholders})
        """

        for _, row in clean_df.iterrows():

            incoming = {
                column: _python_value(row[column])
                for column in upload_columns
            }

            existing = None

            # --------------------------------------------------------
            # Check by primary key when the CSV contains the PK.
            # --------------------------------------------------------
            if pk_columns and all(
                column in incoming
                for column in pk_columns
            ):
                where_clause = " AND ".join(
                    f'"{column}" = %s'
                    for column in pk_columns
                )

                lookup_sql = f"""
                    SELECT {quoted_columns}
                    FROM plastic.{table_name}
                    WHERE {where_clause}
                    LIMIT 1
                """

                cursor.execute(
                    lookup_sql,
                    tuple(
                        incoming[column]
                        for column in pk_columns
                    )
                )

                result = cursor.fetchone()

                if result:
                    existing = dict(
                        zip(upload_columns, result)
                    )

            # --------------------------------------------------------
            # If no PK match exists, protect against exact duplicate.
            # --------------------------------------------------------
            if existing is None:

                comparison_conditions = []
                comparison_values = []

                for column in upload_columns:
                    value = incoming[column]

                    if value is None:
                        comparison_conditions.append(
                            f'"{column}" IS NULL'
                        )
                    else:
                        comparison_conditions.append(
                            f'"{column}" = %s'
                        )
                        comparison_values.append(value)

                duplicate_sql = f"""
                    SELECT {quoted_columns}
                    FROM plastic.{table_name}
                    WHERE {" AND ".join(comparison_conditions)}
                    LIMIT 1
                """

                cursor.execute(
                    duplicate_sql,
                    tuple(comparison_values)
                )

                result = cursor.fetchone()

                if result:
                    existing = dict(
                        zip(upload_columns, result)
                    )

            # --------------------------------------------------------
            # Existing record handling.
            # --------------------------------------------------------
            if existing is not None:

                if _rows_are_identical(
                    existing,
                    incoming,
                    upload_columns
                ):
                    skipped += 1
                    continue

                # Update only controlled master/configuration tables.
                if (
                    table_name in update_existing_tables
                    and pk_columns
                    and all(
                        column in incoming
                        for column in pk_columns
                    )
                ):
                    update_columns = [
                        column
                        for column in upload_columns
                        if column not in pk_columns
                    ]

                    if update_columns:
                        set_clause = ", ".join(
                            f'"{column}" = %s'
                            for column in update_columns
                        )

                        where_clause = " AND ".join(
                            f'"{column}" = %s'
                            for column in pk_columns
                        )

                        update_sql = f"""
                            UPDATE plastic.{table_name}
                            SET {set_clause}
                            WHERE {where_clause}
                        """

                        cursor.execute(
                            update_sql,
                            tuple(
                                incoming[column]
                                for column in update_columns
                            )
                            + tuple(
                                incoming[column]
                                for column in pk_columns
                            )
                        )

                        updated += 1
                        continue

                # Historical/transactional records are protected.
                skipped += 1
                continue

            # --------------------------------------------------------
            # New record.
            # --------------------------------------------------------
            cursor.execute(
                insert_sql,
                tuple(
                    incoming[column]
                    for column in upload_columns
                )
            )

            inserted += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "dataset": table_name,
        "received": validation["received"],
        "validated": validation["validated"],
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "duplicate_rows_in_file": validation[
            "duplicate_rows_in_file"
        ],
    }


def load_fact_order_line_data(df):
    """
    Compatibility wrapper for the current Streamlit app.

    The old public.fact_order_line ingestion is intentionally replaced
    by plastic.fact_order_lines.
    """
    return load_plastic_table_data(
        "fact_order_lines",
        df
    )


def load_fact_aggregate_data(df):
    """
    Compatibility wrapper retained so existing imports do not break.

    The old public.fact_aggregate dataset no longer belongs to the
    plastic SupplySync architecture.
    """
    raise ValueError(
        "Legacy fact_aggregate ingestion is no longer supported. "
        "Use a plastic SupplySync dataset such as fact_orders."
    )


def log_ingestion(
    dataset,
    received_rows,
    validated_rows,
    inserted_rows,
    updated_rows,
    skipped_rows,
    status="SUCCESS",
):
    """
    Record a SupplySync ingestion event.
    """
    connection = get_db_connection()

    query = """
        INSERT INTO plastic.ingestion_log (
            dataset,
            received_rows,
            validated_rows,
            inserted_rows,
            updated_rows,
            skipped_rows,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    try:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                dataset,
                int(received_rows),
                int(validated_rows),
                int(inserted_rows),
                int(updated_rows),
                int(skipped_rows),
                status,
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_latest_ingestion():
    """
    Return the most recent successful ingestion event.
    """
    connection = get_db_connection()

    query = """
        SELECT
            id,
            dataset,
            uploaded_at,
            received_rows,
            validated_rows,
            inserted_rows,
            updated_rows,
            skipped_rows,
            status
        FROM plastic.ingestion_log
        WHERE status = 'SUCCESS'
        ORDER BY uploaded_at DESC, id DESC
        LIMIT 1;
    """

    try:
        cursor = connection.cursor()

        cursor.execute(query)

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "id",
            "dataset",
            "uploaded_at",
            "received_rows",
            "validated_rows",
            "inserted_rows",
            "updated_rows",
            "skipped_rows",
            "status",
        ]

        return dict(zip(columns, row))

    finally:
        connection.close()

def get_ingestion_history(limit=20):
    """
    Return recent SupplySync ingestion events.
    """
    connection = get_db_connection()

    query = """
        SELECT
            id,
            dataset,
            uploaded_at,
            received_rows,
            validated_rows,
            inserted_rows,
            updated_rows,
            skipped_rows,
            status
        FROM plastic.ingestion_log
        ORDER BY uploaded_at DESC, id DESC
        LIMIT %s;
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query, (int(limit),))

        rows = cursor.fetchall()

        columns = [
            "id",
            "dataset",
            "uploaded_at",
            "received_rows",
            "validated_rows",
            "inserted_rows",
            "updated_rows",
            "skipped_rows",
            "status",
        ]

        return [dict(zip(columns, row)) for row in rows]

    finally:
        connection.close()