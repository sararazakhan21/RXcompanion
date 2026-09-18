import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dss_engine import DrugInteractionAnalyzer, Patient

# Page configuration
st.set_page_config(
    page_title="RxCompanion - Medication Safety DSS",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize analyzer
@st.cache_resource
def load_analyzer():
    return DrugInteractionAnalyzer('data/drugs.csv', 'data/interactions.csv')

analyzer = load_analyzer()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .interaction-severe {
        background-color: #FFE5E5;
        border-left: 5px solid #FF0000;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    .interaction-moderate {
        background-color: #FFF3E5;
        border-left: 5px solid #FF6600;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    .interaction-mild {
        background-color: #FFFFE5;
        border-left: 5px solid #FFCC00;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">💊 RxCompanion</div>', unsafe_allow_html=True)
st.markdown("### Medication Safety Decision Support System")
st.markdown("---")

# Sidebar for patient selection/input
with st.sidebar:
    st.header("👤 Patient Management")

    patient_option = st.radio(
        "Select Patient",
        ["Load Sample Patient", "Create New Patient"]
    )

    if patient_option == "Load Sample Patient":
        try:
            sample_patients = pd.read_csv('data/patients.csv')
            patient_names = sample_patients['Name'].tolist()
            selected_name = st.selectbox("Choose Patient", patient_names)

            if selected_name:
                patient_data = sample_patients[sample_patients['Name'] == selected_name].iloc[0]
                patient = Patient(
                    patient_id=patient_data['PatientID'],
                    name=patient_data['Name'],
                    age=int(patient_data['Age']),
                    gender=patient_data['Gender'],
                    bmi=float(patient_data['BMI']),
                    egfr=float(patient_data['eGFR']),
                    liver_function=patient_data['LiverFunction'],
                    medications=patient_data['Medications'].split('|'),
                    comorbidities=patient_data['Comorbidities'].split('|') if pd.notna(patient_data['Comorbidities']) else [],
                    allergies=patient_data['Allergies'].split('|') if pd.notna(patient_data['Allergies']) else [],
                    smoking=patient_data['Smoking'] if pd.notna(patient_data['Smoking']) else 'No',
                    alcohol=patient_data['Alcohol'] if pd.notna(patient_data['Alcohol']) else 'None'
                )
                st.success(f"✅ Loaded patient: {patient.name}")
        except FileNotFoundError:
            st.error("Please run generate_data.py first to create patient data.")
            st.stop()

    else:
        # Create new patient form
        st.subheader("New Patient")

        name = st.text_input("Full Name", "John Doe")
        age = st.number_input("Age", min_value=18, max_value=120, value=72)
        gender = st.selectbox("Gender", ["M", "F"])
        bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=22.4)
        egfr = st.number_input("eGFR (mL/min)", min_value=5, max_value=120, value=45)
        liver_function = st.selectbox("Liver Function", ["Normal", "MildlyImpaired", "Abnormal"])

        all_drugs = list(analyzer.drugs.keys())
        medications = st.multiselect("Current Medications", all_drugs)

        comorbidities_text = st.text_input("Comorbidities (comma-separated)", "Hypertension, Atrial Fibrillation")
        comorbidities = [c.strip() for c in comorbidities_text.split(',') if c.strip()]

        allergies_text = st.text_input("Allergies (comma-separated)", "")
        allergies = [a.strip() for a in allergies_text.split(',') if a.strip()]

        smoking = st.selectbox("Smoking Status", ["No", "Former", "Current"])
        alcohol = st.selectbox("Alcohol Consumption", ["None", "Occasional", "Moderate", "Heavy"])

        if st.button("Analyze Patient"):
            patient = Patient(
                patient_id="P999",
                name=name,
                age=age,
                gender=gender,
                bmi=bmi,
                egfr=egfr,
                liver_function=liver_function,
                medications=medications,
                comorbidities=comorbidities,
                allergies=allergies,
                smoking=smoking,
                alcohol=alcohol
            )
            st.success(f"✅ Created patient: {patient.name}")

# Main content area
if 'patient' in locals():
    try:
        # Analyze patient
        analysis = analyzer.analyze_patient(patient)

        # Display results
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.markdown("### 📊 Risk Score")
            risk_color = analysis['risk_color']

            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=analysis['risk_score'],
                title={'text': "Risk Score", 'font': {'size': 14}},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': risk_color},
                    'steps': [
                        {'range': [0, 20], 'color': "#00CC00"},
                        {'range': [20, 40], 'color': "#FFCC00"},
                        {'range': [40, 70], 'color': "#FF6600"},
                        {'range': [70, 100], 'color': "#FF0000"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': analysis['risk_score']
                    }
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📋 Patient Summary")
            st.markdown(f"**Name:** {patient.name}")
            st.markdown(f"**Age:** {patient.age} years")
            st.markdown(f"**Gender:** {patient.gender}")
            st.markdown(f"**BMI:** {patient.bmi:.1f}")
            st.markdown(f"**eGFR:** {patient.egfr:.0f} mL/min")
            st.markdown(f"**Liver Function:** {patient.liver_function}")
            st.markdown(f"**Smoking:** {patient.smoking}")
            st.markdown(f"**Alcohol:** {patient.alcohol}")

        with col3:
            st.markdown("### 💊 Medication List")
            for drug in patient.medications:
                drug_info = analyzer.get_drug_info(drug)
                if drug_info:
                    st.markdown(f"""
                    <div style="background:#F0F8FF; padding:0.3rem; margin:0.2rem 0; border-radius:0.3rem;">
                    <b>{drug}</b> ({drug_info.drug_class})
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"• {drug}")

            st.markdown(f"**Total Medications:** {len(patient.medications)}")
            if patient.comorbidities:
                st.markdown(f"**Comorbidities:** {', '.join(patient.comorbidities)}")
            if patient.allergies:
                st.markdown(f"**Allergies:** {', '.join(patient.allergies)}")

        st.markdown("---")

        # Interactions section
        st.markdown("### 🔍 Detected Interactions")

        if analysis['interactions']:
            severe_count = sum(1 for i in analysis['interactions'] if i.severity.value == 'Severe')
            moderate_count = sum(1 for i in analysis['interactions'] if i.severity.value == 'Moderate')
            mild_count = sum(1 for i in analysis['interactions'] if i.severity.value == 'Mild')

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Interactions", len(analysis['interactions']))
            with col2:
                st.metric("⚠️ Severe", severe_count)
            with col3:
                st.metric("⚠️ Moderate", moderate_count)
            with col4:
                st.metric("⚠️ Mild", mild_count)

            st.markdown("---")

            for interaction in analysis['interactions']:
                severity_class = {
                    'Severe': 'interaction-severe',
                    'Moderate': 'interaction-moderate',
                    'Mild': 'interaction-mild'
                }[interaction.severity.value]

                emoji = {
                    'Severe': '🔴',
                    'Moderate': '🟠',
                    'Mild': '🟡'
                }[interaction.severity.value]

                st.markdown(f"""
                <div class="{severity_class}">
                    <b>{emoji} {interaction.drug_a} + {interaction.drug_b}</b>
                    <br>
                    <b>Severity:</b> {interaction.severity.value}
                    <br>
                    <b>Mechanism:</b> {interaction.mechanism}
                    <br>
                    <b>Recommendation:</b> {interaction.recommendation}
                    <br>
                    <b>Time to Onset:</b> {interaction.time_to_onset}
                    <br>
                    <b>Monitoring Required:</b> {', '.join(interaction.monitoring_required)}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No interactions detected! This medication list appears safe.")

        st.markdown("---")

        # Deprescribing suggestions
        st.markdown("### 🎯 Deprescribing Suggestions")
        st.markdown("Priority order for medication review:")

        if analysis['deprescribing_suggestions']:
            for i, suggestion in enumerate(analysis['deprescribing_suggestions'][:5]):
                priority_icon = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟠',
                    'LOW': '🟢'
                }.get(suggestion['priority'], '⚪')

                st.markdown(f"""
                <div style="background:#F5F5F5; padding:0.5rem; margin:0.3rem 0; border-radius:0.3rem;">
                    <b>{i+1}. {suggestion['drug']}</b> ({suggestion['drug_class']})
                    <br>
                    <b>Risk Contribution:</b> {suggestion['risk_contribution']:.1f} points
                    <br>
                    <b>Priority:</b> {priority_icon} {suggestion['priority']}
                    <br>
                    <b>Reason:</b> {suggestion['reason']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No deprescribing suggestions available.")

        st.markdown("---")

        # What-if analysis section
        st.markdown("### 🔮 What-If Analysis")
        st.markdown("Simulate the effect of changing medications")

        what_if_col1, what_if_col2 = st.columns([2, 1])

        with what_if_col1:
            scenario_type = st.selectbox(
                "Scenario Type",
                ["Add Medication", "Remove Medication"],
                key="what_if_scenario"
            )

            if scenario_type == "Add Medication":
                available_drugs = [d for d in list(analyzer.drugs.keys()) if d not in patient.medications]
                if available_drugs:
                    drug_to_modify = st.selectbox("Select drug to add", available_drugs)
                else:
                    st.warning("Patient is already on all available drugs.")
                    drug_to_modify = None
            else:
                if patient.medications:
                    drug_to_modify = st.selectbox("Select drug to remove", patient.medications)
                else:
                    st.warning("No medications to remove.")
                    drug_to_modify = None

        with what_if_col2:
            if drug_to_modify and st.button("Run Simulation", use_container_width=True):
                scenario = 'add' if scenario_type == "Add Medication" else 'remove'

                try:
                    result = analyzer.what_if_analysis(patient, scenario, drug_to_modify)

                    st.markdown("---")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Original Risk**")
                        st.markdown(f"<h2 style='color:{analysis['risk_color']}'>{analysis['risk_score']:.0f}</h2>",
                                   unsafe_allow_html=True)
                        st.markdown(f"*{analysis['risk_level']}*")

                    with col2:
                        st.markdown("**Change**")
                        change = result['risk_change']
                        change_color = "green" if change < 0 else "red"
                        change_icon = "⬇️" if change < 0 else "⬆️"
                        st.markdown(f"<h2 style='color:{change_color}'>{change_icon} {abs(change):.0f}</h2>",
                                   unsafe_allow_html=True)

                    with col3:
                        st.markdown("**New Risk**")
                        new_color = '#00CC00' if result['new_risk'] < result['original_risk'] else '#FF0000'
                        st.markdown(f"<h2 style='color:{new_color}'>{result['new_risk']:.0f}</h2>",
                                   unsafe_allow_html=True)
                        st.markdown(f"*{result['new_level']}*")

                    st.markdown("---")

                    st.markdown(f"### 📝 Recommendation")
                    st.markdown(f"<div style='background:#F0F8FF; padding:1rem; border-radius:0.5rem;'>{result['recommendation']}</div>",
                               unsafe_allow_html=True)

                    if result['risk_reduction'] > 0:
                        st.success(f"✅ Risk reduced by {result['risk_reduction']:.1f} points")
                    else:
                        st.warning(f"⚠️ Risk increased by {abs(result['risk_reduction']):.1f} points")

                except Exception as e:
                    st.error(f"Error running simulation: {str(e)}")

        st.markdown("---")

        # Summary
        st.markdown("### 📄 Clinical Summary")
        st.markdown(analysis['summary'])

        # Export options
        st.markdown("---")
        st.markdown("### 📤 Export Report")
        if st.button("Generate Report"):
            report = f"""
            # RxCompanion Clinical Report

            ## Patient Information
            - Name: {patient.name}
            - Age: {patient.age}
            - Gender: {patient.gender}
            - BMI: {patient.bmi:.1f}
            - eGFR: {patient.egfr:.0f}
            - Liver Function: {patient.liver_function}

            ## Risk Assessment
            - Risk Score: {analysis['risk_score']:.1f}/100
            - Risk Level: {analysis['risk_level']}

            ## Interactions Detected: {len(analysis['interactions'])}

            ## Recommendations
            """
            for i, suggestion in enumerate(analysis['deprescribing_suggestions'][:3]):
                report += f"\n{i+1}. Consider reviewing {suggestion['drug']} (Priority: {suggestion['priority']})"

            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"RxCompanion_Report_{patient.name.replace(' ', '_')}.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"Error analyzing patient: {str(e)}")
        st.info("Please ensure all data files are correctly loaded.")
else:
    st.info("👈 Please select or create a patient from the sidebar to begin analysis.")

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:gray; font-size:0.8rem;">
    RxCompanion v1.0 | Built with  for Medication Safety
</div>
""", unsafe_allow_html=True)