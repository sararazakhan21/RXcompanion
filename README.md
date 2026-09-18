# 💊 RxCompanion

## Medication Safety Decision Support System

### Overview
RxCompanion is a Decision Support System (DSS) that helps clinicians analyze medication safety for elderly patients with polypharmacy. It detects drug-drug interactions, calculates risk scores, and provides deprescribing suggestions.

### Features
- 🔍 **Interaction Detection**: Identifies drug-drug interactions with severity levels
- 📊 **Risk Scoring**: Calculates patient-specific risk scores (0-100)
- 🎯 **Deprescribing Suggestions**: Prioritizes medications for review
- 🔮 **What-If Analysis**: Simulates adding or removing medications
- 📄 **Report Generation**: Exports clinical summaries

### Technology Stack
- Python 3.9+
- Streamlit (UI)
- Pandas (Data Processing)
- Plotly (Visualization)

### Setup Instructions

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python generate_data.py