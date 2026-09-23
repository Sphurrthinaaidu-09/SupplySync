# 📦 SupplySync

### AI-Powered Supply Chain Analytics & Decision-Support Platform

An end-to-end Supply Chain Intelligence platform designed to transform operational supply-chain data into actionable insights across inventory, suppliers, procurement, production, demand, delivery, risk, and replenishment.

SupplySync combines **Python, Streamlit, PostgreSQL, Power Automate, automated data synchronization, analytical decision engines, and Gemini AI** to provide a centralized environment for monitoring supply-chain performance and supporting operational decisions.

<p align="center">
  <a href="https://supplysync-7bomfjjmfjzaakmedo4c86.streamlit.app">
    🚀 <strong>Live Demo</strong>
  </a>
</p>

---

<p align="center">

<img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge" alt="Python">

<img src="https://img.shields.io/badge/Streamlit-Framework-red?style=for-the-badge" alt="Streamlit">

<img src="https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge" alt="PostgreSQL">

<img src="https://img.shields.io/badge/Gen%20AI-Gemini-orange?style=for-the-badge" alt="Generative AI">

<img src="https://img.shields.io/badge/Power%20Automate-Workflow%20Automation-5C2D91?style=for-the-badge" alt="Power Automate">

<img src="https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge" alt="Pandas">

<img src="https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge" alt="Plotly">

</p>

---

## 🚀 Project Overview

Modern supply chains generate large amounts of operational data across suppliers, materials, inventory, purchase orders, production, customer orders, deliveries, and quality records.

However, having data available does not automatically make it easy to understand:

- Which risks require immediate attention?
- Which materials require replenishment?
- Which suppliers are creating operational exposure?
- Where are inventory shortages developing?
- Which products are experiencing demand pressure?
- Where are delivery-performance issues occurring?
- What actions should supply-chain teams consider?

**SupplySync converts these operational datasets into a centralized supply-chain intelligence platform.**

The application combines:

- Operational data ingestion
- PostgreSQL data management
- Supply-chain analytics
- Risk detection
- Replenishment intelligence
- Supplier analysis
- Interactive dashboards
- Automated CSV synchronization
- AI-powered natural-language analysis

---

# 🎯 Business Problem

Supply-chain operations often depend on multiple datasets and manually maintained reports.

As the number of suppliers, materials, products, warehouses, orders, and transactions increases, manually identifying operational problems becomes increasingly difficult.

Common challenges include:

- Fragmented supply-chain information
- Inventory shortages
- Supplier performance issues
- Delivery delays
- Procurement exposure
- Quality-related risks
- Demand uncertainty
- Difficulty prioritizing operational risks
- Time-consuming manual analysis

SupplySync addresses these challenges by bringing the operational data into a unified analytical environment.

---

# 💡 Solution

SupplySync provides a centralized decision-support platform where operational data can be transformed into:

```text
Raw Supply-Chain Data
        ↓
Data Validation
        ↓
PostgreSQL Data Layer
        ↓
Analytical Engines
        ↓
Risk & Recommendation Intelligence
        ↓
Streamlit Dashboard
        ↓
Gemini AI Decision Support
```

The objective is not simply to display data.

The objective is to help users move from:

**Data → Insight → Risk → Recommendation → Decision**

---

# ⚙️ System Workflow

## Step 1: Supply-Chain Data Ingestion

SupplySync works with structured operational datasets representing different areas of the supply chain.

Major dataset categories include:

- Suppliers
- Materials
- Products
- Customers
- Warehouses
- Inventory
- Purchase Orders
- Material Receipts
- Material Quality
- Production
- Orders
- Deliveries
- Forecasts
- Risk Assessments
- Decision Recommendations

---

## Step 2: Data Validation & Transformation

Before data is loaded into PostgreSQL, SupplySync performs validation and transformation.

The ingestion pipeline handles:

- Dataset identification
- Required-column validation
- Unknown-column detection
- Duplicate detection
- Data transformation
- Referential integrity considerations
- Controlled updates
- Historical record protection

This creates a more reliable analytical foundation for the dashboard and AI layer.

---

# 🔄 Automated Data Synchronization

SupplySync includes an automated data synchronization workflow combining Python-based monitoring with workflow automation.

```text
CSV Dataset
     │
     ▼
CSV Watcher
     │
     ▼
Dataset Detection
     │
     ▼
Validation & Transformation
     │
     ▼
PostgreSQL
     │
     ▼
Ingestion Logging
     │
     ▼
Streamlit Analytics
```

The system monitors the configured dataset directory for new or modified CSV files.

When a relevant file changes:

1. The watcher detects the change.
2. The dataset is identified.
3. The data is validated.
4. Required transformations are applied.
5. PostgreSQL is updated.
6. The ingestion event is recorded.

This allows the data layer to stay synchronized without requiring manual database uploads every time a source CSV changes.

---

# 🗄️ Database Architecture

SupplySync uses **PostgreSQL** as its primary data layer.

The application uses a dedicated:

```text
plastic
```

schema.

The database is organized into several functional areas.

### Dimension Tables

```text
dim_suppliers
dim_materials
dim_products
dim_customers
dim_warehouses
dim_inventory_policies
dim_date
```

### Procurement

```text
supplier_material
purchase_orders
purchase_order_lines
```

### Inventory & Materials

```text
fact_inventory
fact_material_receipts
fact_material_quality
```

### Production

```text
fact_production
```

### Orders & Delivery

```text
fact_orders
fact_order_lines
fact_deliveries
```

### Intelligence

```text
forecast_results
risk_assessments
decision_recommendations
```

### Monitoring

```text
ingestion_log
```

---

# 📊 Executive Dashboard

The Executive Dashboard provides a high-level view of the current supply-chain environment.

It brings together important operational indicators and helps users quickly understand:

- Overall supply-chain health
- Order performance
- Delivery performance
- Critical risks
- Inventory exposure
- Operational recommendations

The dashboard is designed to provide an executive-level starting point before users move into deeper analytical modules.

---

# ⚠️ Risk Center

The Risk Center provides centralized visibility into supply-chain risks.

Risk assessments include information such as:

- Risk type
- Risk score
- Risk level
- Reference entity
- Risk reason
- Recommended action
- Supplier/material context

SupplySync supports risk analysis across areas such as:

- Supplier
- Inventory
- Quality
- Delivery
- Production

The Risk Center helps users identify which areas of the supply chain require further investigation.

---

# 📦 Replenishment Intelligence

The Replenishment module transforms inventory exposure into procurement-oriented recommendations.

The analytical layer considers information such as:

- Current stock
- Reorder levels
- Inventory shortfall
- Lead time
- Supplier information
- Risk information
- Estimated procurement cost

The objective is to help supply-chain teams identify materials that may require replenishment and understand the operational context behind the recommendation.

---

# 🚚 Delivery & OTIF Analytics

SupplySync includes delivery-performance analysis focused on operational fulfillment.

The analytical layer supports:

- OTIF performance
- Delivery performance
- Fulfillment analysis
- Delivery-related risk identification

This allows users to understand where delivery execution may be creating supply-chain exposure.

---

# 🏭 Production & Inventory Analytics

SupplySync provides analytical visibility across production and inventory.

Users can investigate:

- Inventory levels
- Inventory exposure
- Stockout risk
- Production activity
- Material availability
- Replenishment requirements

These insights help connect inventory conditions with downstream operational requirements.

---

# 👥 Supplier Intelligence

Supplier analysis is another core component of SupplySync.

The system provides analytical capabilities for:

- Supplier performance
- Supplier risk
- Supplier comparison
- Supplier-related operational exposure

This allows users to investigate supplier-related problems using the underlying operational evidence.

---

# 📈 Demand Analytics

SupplySync includes product-demand analysis to identify demand-related exposure.

The analytical layer supports:

- Product demand analysis
- Demand trends
- Sales-related analysis
- Product-level demand exposure

This provides an additional perspective when evaluating inventory and procurement requirements.

---

# 💰 Cost Analysis

SupplySync includes cost-oriented analytical capabilities for investigating:

- Procurement costs
- Spending
- Expenses
- Price-related information
- Cost exposure

The purpose is to connect operational supply-chain activity with its financial implications.

---

# 🤖 Ask SupplySync — AI Decision Support

One of the main features of SupplySync is **Ask SupplySync**, an AI-powered natural-language interface.

Users can ask questions such as:

```text
Which supply-chain risks require my attention right now?
```

```text
Which materials need replenishment?
```

```text
Which suppliers are currently at risk?
```

```text
What products have demand exposure?
```

Instead of allowing the AI model to independently invent answers, SupplySync first identifies the relevant analytical area and retrieves evidence from the database.

---

# 🧠 AI Architecture

The AI workflow follows a grounded analytical pipeline:

```text
                User Question
                      │
                      ▼
              Intent Detection
                      │
                      ▼
             Analytical Tool
                      │
                      ▼
              PostgreSQL Data
                      │
                      ▼
              Evidence Dataset
                      │
                      ▼
                 Gemini AI
                      │
                      ▼
             Grounded Response
```

### Available analytical tools include:

```text
Supply Risks
Inventory Risks
Supplier Performance
Product Demand
OTIF Performance
Cost Analysis
Stockout Exposure
Supplier Comparison
Replenishment Recommendations
Supplier Risk Summary
```

The AI layer is instructed to:

- Use only the supplied analytical evidence
- Avoid inventing numbers
- Avoid inventing suppliers or products
- Avoid inventing dates or costs
- Explain important findings first
- Identify insufficient evidence when necessary
- Provide decision-support rather than claiming to execute actions

This creates a separation between:

**Data retrieval → Analytical logic → AI explanation**

---

# 📋 Decision Recommendations

SupplySync includes a decision-recommendation layer connected to the risk and analytical system.

Recommendations can include actions associated with areas such as:

- Replenishment
- Supplier selection
- Production
- Delivery recovery
- Operational risk

The recommendation data contains contextual information such as:

- Recommendation type
- Risk reference
- Priority
- Recommended action
- Quantity
- Supplier
- Estimated cost
- Rationale
- Recommendation status

---

# 📡 Ingestion Monitoring

SupplySync maintains an ingestion log to track synchronization activity.

Each ingestion event can capture:

- Dataset
- Upload time
- Received rows
- Validated rows
- Inserted rows
- Updated rows
- Skipped rows
- Processing status

This provides visibility into the health of the data-ingestion pipeline.

---

# 🧪 Testing

The repository contains multiple test scripts covering different parts of the system.

```text
test_ai.py
test_critical_risks.py
test_gemini.py
test_gemini_rest.py
test_kpis.py
test_replenishment.py
test_risk_center.py
test_tools.py
```

The tests cover areas including:

- AI functionality
- Gemini connectivity
- KPI calculations
- Critical risk analysis
- Replenishment
- Risk Center
- Analytical tools

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application & analytical logic |
| Streamlit | Interactive dashboard |
| PostgreSQL | Database & analytical data layer |
| Gemini AI | AI-powered decision support |
| Power Automate | Workflow automation and process orchestration |
| Windows Task Scheduler | Automatic startup of the CSV watcher |
| Pandas | Data processing |
| Plotly | Data visualization |
| psycopg2 | PostgreSQL connectivity |
| python-dotenv | Environment configuration |
| Git | Version control |
| GitHub | Source control & portfolio |

---

# 📁 Project Structure

```text
SupplySync/
│
├── app.py
│
├── database.py
│
├── ai_engine.py
│
├── csv_watcher.py
│
├── sync_csv_to_postgres.py
│
├── requirements.txt
│
├── .gitignore
│
├── README.md
│
├── LICENSE
│
├── test_ai.py
├── test_critical_risks.py
├── test_gemini.py
├── test_gemini_rest.py
├── test_kpis.py
├── test_replenishment.py
├── test_risk_center.py
└── test_tools.py
```

---

# 📸 Application Screenshots

## 1. Executive Dashboard

The Executive Dashboard provides a centralized overview of the current supply-chain operating position.

It presents:

- Total orders
- OTIF performance
- Products at risk
- Critical risks
- Overall supply-chain status
- Priority risk queue

The dashboard provides an executive-level view before users move into specific operational areas.

---

## 2. Risk Center

The Risk Center provides centralized visibility into supply-chain risks and operational exceptions.

It allows users to analyze risks by:

- Severity
- Risk type
- Product
- Supplier

The Risk Center also presents detailed risk information including risk score, priority, recommended action, recommendation status, estimated cost, and supplier context.

---

## 3. Replenishment

The Replenishment module converts inventory exposure into procurement recommendations.

It provides visibility into:

- Materials requiring replenishment
- Recommended units
- Estimated procurement cost
- Critical replenishment items
- Current stock
- Reorder point
- Recommended order quantity
- Supplier information

Users can also filter procurement recommendations by risk level, product/reference, and supplier.

---

## 4. Data Ingestion

The Data Ingestion module manages the movement of operational CSV data into SupplySync.

The ingestion workflow includes:

```text
Receive
   ↓
Validate
   ↓
Protect
   ↓
Load
   ↓
Audit
```

---

# 🎓 Skills Demonstrated

Through this project, I developed practical experience in:

### Data Engineering

- Data ingestion pipelines
- CSV processing
- Data validation
- Data transformation
- PostgreSQL data modeling
- Database connectivity
- Ingestion monitoring

### Supply Chain Analytics

- Inventory analysis
- Supplier analysis
- Demand analysis
- OTIF analysis
- Cost analysis
- Stockout exposure
- Risk analysis
- Replenishment intelligence

### AI & Decision Support

- Gemini API integration
- Natural-language interfaces
- Intent detection
- Tool-based analytical retrieval
- Evidence-grounded AI responses
- AI-assisted decision support

### Application Development

- Python
- Streamlit
- Interactive dashboards
- Data visualization
- Modular application architecture

### Automation

- CSV monitoring
- Automated database synchronization
- Windows Task Scheduler
- Git/GitHub version control

---

# 🔮 Future Enhancements

Potential future improvements include:

- 🌍 Multilingual AI interaction
- 🧠 More advanced natural-language intent classification
- 🔔 Automated operational alerts
- 📊 Advanced forecasting
- 🤝 Supplier optimization
- 📦 Advanced inventory optimization
- ☁️ Cloud deployment
- 🔐 Role-based authentication
- 📡 Real-time data integrations
- 📈 Advanced supply-chain forecasting
- 🧾 Automated reporting
- 🔎 Greater AI explainability and traceability

---

# 📌 Project Status

### 🟢 Functional Portfolio Prototype

SupplySync currently demonstrates an end-to-end supply-chain intelligence workflow covering:

```text
Data Ingestion
      ↓
Validation
      ↓
PostgreSQL
      ↓
Analytics
      ↓
Risk Detection
      ↓
Replenishment Intelligence
      ↓
Recommendations
      ↓
Streamlit Dashboard
      ↓
Gemini AI Decision Support
```

The platform is designed as a **decision-support system**.

It provides analytical evidence and recommendations to support human decision-making rather than directly executing procurement or operational actions.

---

# 👨‍💻 Author

### Sphurrthinaaidu-09

Aspiring Data / AI & Business Analytics Professional

GitHub:

https://github.com/Sphurrthinaaidu-09

---

⭐ If you find this project interesting, consider giving the repository a star!

```

