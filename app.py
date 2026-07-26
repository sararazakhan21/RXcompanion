import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import os
import re
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from PIL import Image

# Try to import OCR libraries – fallback if not installed
try:
    import cv2
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================================
# DATA GENERATION FUNCTIONS
# ============================================================

def generate_all_data():
    """Generate all data files if they don't exist"""
    
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Drugs data
    drugs = [
        ["D001", "Warfarin", "Anticoagulant", "CYP2C9", "Oral", 10, "mg", "Bleeding|Nausea", "Active bleeding|Pregnancy", "INR weekly", "X"],
        ["D002", "Metformin", "Antidiabetic", "Renal excretion", "Oral", 2550, "mg", "GI upset|Lactic acidosis", "eGFR<30|Heart failure", "Renal function monthly", "B"],
        ["D003", "Lisinopril", "ACE Inhibitor", "Renal excretion", "Oral", 40, "mg", "Cough|Hyperkalemia|Angioedema", "Pregnancy|Bilateral renal stenosis", "K+ weekly", "D"],
        ["D004", "Amlodipine", "Calcium Channel Blocker", "CYP3A4", "Oral", 10, "mg", "Edema|Dizziness|Flushing", "Hypotension", "BP weekly", "C"],
        ["D005", "Simvastatin", "Statin", "CYP3A4", "Oral", 40, "mg", "Myopathy|Liver toxicity|Diabetes", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D006", "Digoxin", "Cardiac glycoside", "Renal excretion", "Oral", 0.25, "mg", "Arrhythmia|Nausea|Visual changes", "Hypokalemia|AV block", "Digoxin level quarterly", "C"],
        ["D007", "Furosemide", "Loop diuretic", "Renal excretion", "Oral", 80, "mg", "Electrolyte imbalance|Dehydration", "Renal failure", "Electrolytes weekly", "C"],
        ["D008", "Metoprolol", "Beta-blocker", "CYP2D6", "Oral", 200, "mg", "Bradycardia|Fatigue|Depression", "Bradycardia|Asthma", "HR weekly", "C"],
        ["D009", "Losartan", "ARB", "CYP2C9", "Oral", 100, "mg", "Hyperkalemia|Dizziness", "Pregnancy|Bilateral renal stenosis", "K+ weekly", "D"],
        ["D010", "Aspirin", "Antiplatelet", "Hydrolysis", "Oral", 325, "mg", "GI bleeding|Ulcers", "Active bleeding|Asthma", "GI symptoms quarterly", "C"],
        ["D011", "Atorvastatin", "Statin", "CYP3A4", "Oral", 80, "mg", "Myopathy|Liver toxicity", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D012", "Clopidogrel", "Antiplatelet", "CYP2C19", "Oral", 75, "mg", "Bleeding|GI upset", "Active bleeding|Liver disease", "CBC quarterly", "B"],
        ["D013", "Omeprazole", "PPI", "CYP2C19", "Oral", 40, "mg", "Gastric polyps|B12 deficiency", "Long-term use", "Mag/B12 yearly", "C"],
        ["D014", "Dapagliflozin", "SGLT2 inhibitor", "UGT1A9", "Oral", 10, "mg", "UTI|Dehydration|Euglycemic DKA", "eGFR<30", "Volume status monthly", "C"],
        ["D015", "Insulin Glargine", "Insulin", "Subcutaneous", "Subcutaneous", 100, "units", "Hypoglycemia|Weight gain", "Hypoglycemia", "Glucose daily", "B"],
        ["D016", "Levothyroxine", "Thyroid hormone", "Liver", "Oral", 200, "mcg", "Palpitations|Tachycardia", "Untreated hyperthyroidism", "TSH quarterly", "A"],
        ["D017", "Gabapentin", "Anticonvulsant", "Renal excretion", "Oral", 3600, "mg", "Drowsiness|Dizziness", "CrCl<15", "Creatinine monthly", "C"],
        ["D018", "Tramadol", "Opioid analgesic", "CYP2D6", "Oral", 400, "mg", "Nausea|Dizziness|Seizures", "Seizure disorder|MAOIs", "Respiratory rate monthly", "C"],
        ["D019", "Celecoxib", "COX-2 inhibitor", "CYP2C9", "Oral", 200, "mg", "CV events|GI bleeding", "NSAID allergy|Severe heart disease", "BP monthly", "C"],
        ["D020", "Allopurinol", "Xanthine oxidase inhibitor", "Renal excretion", "Oral", 800, "mg", "Rash|Hepatotoxicity", "CrCl<30", "Creatinine monthly", "B"],
        ["D021", "Spironolactone", "Aldosterone antagonist", "CYP3A4", "Oral", 100, "mg", "Hyperkalemia|Gynecomastia", "Addison's disease", "K+ weekly", "B"],
        ["D022", "Ciprofloxacin", "Antibiotic", "CYP1A2", "Oral", 1500, "mg", "Tendonitis|QT prolongation", "CYP1A2 interactions", "ECG if risk", "B"],
        ["D023", "Prednisolone", "Corticosteroid", "CYP3A4", "Oral", 60, "mg", "Hyperglycemia|Immunosuppression", "Active infection", "Glucose weekly", "C"],
        ["D024", "Diltiazem", "Calcium Channel Blocker", "CYP3A4", "Oral", 360, "mg", "Bradycardia|Heart block|Edema", "Hypotension|AV block", "HR weekly", "C"],
        ["D025", "Carvedilol", "Beta-blocker", "CYP2D6", "Oral", 50, "mg", "Bradycardia|Hypotension|Dizziness", "Asthma|2nd degree AV block", "BP weekly", "C"],
        ["D026", "Ramipril", "ACE Inhibitor", "Renal excretion", "Oral", 10, "mg", "Cough|Hyperkalemia|Angioedema", "Pregnancy", "K+ quarterly", "D"],
        ["D027", "Rosuvastatin", "Statin", "CYP2C9", "Oral", 40, "mg", "Myopathy|Liver toxicity|Diabetes", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D028", "Hydrochlorothiazide", "Thiazide diuretic", "Renal excretion", "Oral", 25, "mg", "Hypokalemia|Hyperglycemia", "Sulfa allergy", "Electrolytes quarterly", "B"],
        ["D029", "Empagliflozin", "SGLT2 inhibitor", "UGT1A9", "Oral", 25, "mg", "UTI|Dehydration|Euglycemic DKA", "eGFR<30", "Volume status monthly", "C"],
        ["D030", "Glimepiride", "Sulfonylurea", "CYP2C9", "Oral", 8, "mg", "Hypoglycemia|Weight gain", "Sulfa allergy|eGFR<30", "Glucose daily", "C"],
    ]
    
    drugs_df = pd.DataFrame(drugs, columns=[
        "DrugID", "DrugName", "DrugClass", "Metabolism", "Route",
        "MaxDailyDose", "Unit", "CommonSideEffects", "Contraindications",
        "MonitoringRequired", "PregnancyRisk"
    ])
    drugs_df.to_csv('data/drugs.csv', index=False)
    
    # Interactions data
    interactions = [
        ["I001", "Warfarin", "Aspirin", "Severe", "Increased bleeding risk", "Avoid combination", "Strong", "Immediate", "INR weekly|CBC monthly"],
        ["I002", "Warfarin", "Simvastatin", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-7 days", "INR weekly"],
        ["I003", "Warfarin", "Ciprofloxacin", "Severe", "INR increase", "Avoid if possible", "Strong", "2-5 days", "INR daily"],
        ["I004", "Warfarin", "Omeprazole", "Moderate", "Increased INR", "Monitor INR", "Weak", "3-7 days", "INR weekly"],
        ["I005", "Warfarin", "Furosemide", "Moderate", "Decreased warfarin effect", "Monitor INR", "Weak", "3-5 days", "INR weekly|BP weekly"],
        ["I006", "Lisinopril", "Furosemide", "Moderate", "Hypotension risk", "Monitor BP", "Strong", "Immediate", "BP daily|Electrolytes weekly"],
        ["I007", "Lisinopril", "Losartan", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly|Creatinine weekly"],
        ["I008", "Lisinopril", "Spironolactone", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly|Creatinine weekly"],
        ["I009", "Lisinopril", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I010", "Lisinopril", "Digoxin", "Moderate", "Digoxin toxicity", "Monitor K+", "Moderate", "1-2 weeks", "K+ weekly|Digoxin level"],
        ["I011", "Metformin", "Furosemide", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I012", "Metformin", "Ciprofloxacin", "Moderate", "Increased metformin levels", "Monitor renal function", "Moderate", "1-3 days", "Creatinine monthly"],
        ["I013", "Digoxin", "Furosemide", "Moderate", "Hypokalemia increases toxicity", "Monitor K+", "Strong", "1-7 days", "K+ weekly|Digoxin level"],
        ["I014", "Digoxin", "Amlodipine", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "3-5 days", "Digoxin level quarterly"],
        ["I015", "Amlodipine", "Simvastatin", "Moderate", "Increased statin toxicity", "Limit simvastatin dose", "Strong", "1-2 weeks", "LFTs quarterly"],
        ["I016", "Amlodipine", "Metoprolol", "Mild", "Bradycardia risk", "Monitor HR", "Moderate", "Immediate", "HR weekly"],
        ["I017", "Aspirin", "Clopidogrel", "Severe", "Bleeding risk", "Use only when necessary", "Strong", "Immediate", "CBC monthly"],
        ["I018", "Aspirin", "Omeprazole", "Moderate", "Reduced antiplatelet effect", "Use pantoprazole", "Moderate", "3-5 days", "GI symptoms"],
        ["I019", "Omeprazole", "Clopidogrel", "Moderate", "Reduced clopidogrel effect", "Use pantoprazole", "Strong", "3-5 days", "CBC if symptoms"],
        ["I020", "Omeprazole", "Digoxin", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "5-7 days", "Digoxin level quarterly"],
        ["I021", "Dapagliflozin", "Furosemide", "Moderate", "Dehydration risk", "Monitor volume status", "Moderate", "Immediate", "BP weekly"],
        ["I022", "Dapagliflozin", "Insulin", "Moderate", "Hypoglycemia risk", "Reduce insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I023", "Dapagliflozin", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I024", "Insulin", "Metoprolol", "Moderate", "Hypoglycemia symptoms masked", "Monitor glucose closely", "Moderate", "Immediate", "Glucose daily"],
        ["I025", "Insulin", "Metformin", "Moderate", "Hypoglycemia risk", "Monitor glucose", "Moderate", "Immediate", "Glucose daily"],
        ["I026", "Insulin", "Prednisolone", "Severe", "Hyperglycemia", "Increase insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I027", "Spironolactone", "Losartan", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"],
        ["I028", "Ramipril", "Spironolactone", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"],
        ["I029", "Warfarin", "Clopidogrel", "Severe", "Bleeding risk", "Avoid if possible", "Strong", "Immediate", "INR weekly|CBC monthly"],
        ["I030", "Warfarin", "Allopurinol", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-5 days", "INR weekly"],
    ]
    
    interactions_df = pd.DataFrame(interactions, columns=[
        "InteractionID", "DrugA", "DrugB", "Severity", "Mechanism",
        "Recommendation", "EvidenceLevel", "TimeToOnset", "MonitoringRequired"
    ])
    interactions_df.to_csv('data/interactions.csv', index=False)
    
    # Patients data
    first_names = ["Rajesh", "Lakshmi", "Abdul", "Sneha", "Vikram", "Meera", "Ram",
                   "Sunita", "Anand", "Priya", "Ravi", "Anita", "Suresh", "Kavita",
                   "Mohan", "Radha", "Vijay", "Deepa", "Rajiv", "Sarita"]
    last_names = ["Kumar", "Iyer", "Rahman", "Patel", "Singh", "Nair", "Shastri",
                  "Desai", "Gupta", "Joshi", "Deshmukh", "Sharma", "Reddy", "Rao",
                  "Lal", "Krishnan", "Tendulkar", "Sharma", "Gupta", "Patel"]
    
    common_meds = ["Warfarin", "Metformin", "Lisinopril", "Amlodipine", "Simvastatin",
                   "Digoxin", "Furosemide", "Metoprolol", "Losartan", "Aspirin",
                   "Atorvastatin", "Clopidogrel", "Omeprazole", "Dapagliflozin",
                   "Insulin Glargine", "Levothyroxine", "Gabapentin", "Tramadol",
                   "Celecoxib", "Allopurinol", "Spironolactone", "Ciprofloxacin",
                   "Prednisolone", "Diltiazem", "Carvedilol", "Ramipril"]
    
    comorbidities_list = ["Hypertension", "Diabetes", "Atrial Fibrillation", "Heart Failure", 
                          "CKD", "CAD", "Hyperlipidemia", "Osteoarthritis", "GERD", 
                          "Hypothyroidism", "Neuropathy", "Gout", "COPD"]
    
    patients = []
    for i in range(20):
        age = random.randint(65, 85)
        gender = random.choice(["M", "F"])
        bmi = round(random.uniform(18, 35), 1)
        egfr = round(max(15, 120 - (age - 60) * 1.5 + random.uniform(-15, 15)), 0)
        num_meds = random.randint(4, 8)
        selected_meds = random.sample(common_meds, min(num_meds, len(common_meds)))
        num_comorbidities = random.randint(1, 4)
        selected_comorbidities = random.sample(comorbidities_list, min(num_comorbidities, len(comorbidities_list)))
        liver_status = random.choices(["Normal", "MildlyImpaired", "Abnormal"], weights=[0.7, 0.2, 0.1])[0]
        
        patients.append({
            'PatientID': f"P{i+1:03d}",
            'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'Age': age,
            'Gender': gender,
            'BMI': bmi,
            'eGFR': egfr,
            'LiverFunction': liver_status,
            'Medications': '|'.join(selected_meds),
            'Comorbidities': '|'.join(selected_comorbidities),
            'Allergies': '',
            'Smoking': random.choices(["No", "Former", "Current"], weights=[0.6, 0.3, 0.1])[0],
            'Alcohol': random.choices(["None", "Occasional", "Moderate", "Heavy"], weights=[0.5, 0.3, 0.15, 0.05])[0],
            'SystolicBP': random.randint(110, 180),
            'DiastolicBP': random.randint(70, 100)
        })
    
    patients_df = pd.DataFrame(patients)
    patients_df.to_csv('data/patients.csv', index=False)
    
    print("✅ All data files generated successfully!")


# ============================================================
# BP SCANNING FUNCTION (OCR)
# ============================================================

def extract_bp_from_image(image_file) -> tuple:
    """Extract Systolic/Diastolic BP from an image using OCR"""
    if not OCR_AVAILABLE:
        return None, None
    
    try:
        # Read image
        img = Image.open(image_file)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Preprocess
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # OCR
        text = pytesseract.image_to_string(thresh)
        
        # Look for patterns like "120/80" or "120 / 80"
        patterns = [
            r'(\d{2,3})\s*/\s*(\d{2,3})',
            r'(\d{2,3})\s*mmHg',
            r'BP\s*[:=]\s*(\d{2,3})\s*/\s*(\d{2,3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    return int(match.group(1)), int(match.group(2))
                elif len(match.groups()) == 1:
                    # If only one number found, try to find another
                    numbers = re.findall(r'\d{2,3}', text)
                    if len(numbers) >= 2:
                        return int(numbers[0]), int(numbers[1])
        
        return None, None
    except Exception:
        return None, None


# ============================================================
# DSS ENGINE CLASSES
# ============================================================

class Severity(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"

@dataclass
class Drug:
    drug_id: str
    name: str
    drug_class: str
    metabolism: str
    route: str
    max_daily_dose: float
    unit: str
    common_side_effects: List[str]
    contraindications: List[str]
    monitoring_required: List[str]
    pregnancy_risk: str

@dataclass
class Interaction:
    drug_a: str
    drug_b: str
    severity: Severity
    mechanism: str
    recommendation: str
    evidence_level: str
    time_to_onset: str
    monitoring_required: List[str]

@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    gender: str
    bmi: float
    egfr: float
    liver_function: str
    medications: List[str]
    comorbidities: List[str]
    allergies: List[str]
    smoking: str
    alcohol: str
    systolic_bp: int = 120
    diastolic_bp: int = 80

class DrugInteractionAnalyzer:
    def __init__(self, drugs_csv_path: str, interactions_csv_path: str):
        self.drugs = self._load_drugs(drugs_csv_path)
        self.interactions = self._load_interactions(interactions_csv_path)

    def _load_drugs(self, path: str) -> Dict[str, Drug]:
        df = pd.read_csv(path)
        drugs = {}
        for _, row in df.iterrows():
            drug = Drug(
                drug_id=row['DrugID'],
                name=row['DrugName'],
                drug_class=row['DrugClass'],
                metabolism=row['Metabolism'],
                route=row['Route'],
                max_daily_dose=float(row['MaxDailyDose']),
                unit=row['Unit'],
                common_side_effects=row['CommonSideEffects'].split('|') if pd.notna(row['CommonSideEffects']) else [],
                contraindications=row['Contraindications'].split('|') if pd.notna(row['Contraindications']) else [],
                monitoring_required=row['MonitoringRequired'].split('|') if pd.notna(row['MonitoringRequired']) else [],
                pregnancy_risk=row['PregnancyRisk']
            )
            drugs[row['DrugName']] = drug
        return drugs

    def _load_interactions(self, path: str) -> List[Interaction]:
        df = pd.read_csv(path)
        interactions = []
        for _, row in df.iterrows():
            interaction = Interaction(
                drug_a=row['DrugA'],
                drug_b=row['DrugB'],
                severity=Severity(row['Severity']),
                mechanism=row['Mechanism'],
                recommendation=row['Recommendation'],
                evidence_level=row['EvidenceLevel'],
                time_to_onset=row['TimeToOnset'],
                monitoring_required=row['MonitoringRequired'].split('|') if pd.notna(row['MonitoringRequired']) else []
            )
            interactions.append(interaction)
        return interactions

    def get_patient_modifiers(self, patient: Patient) -> Dict[str, float]:
        modifiers = {}
        
        # Age modifiers
        if patient.age >= 85:
            modifiers['age_very_elderly'] = 2.0
        elif patient.age >= 75:
            modifiers['age_elderly'] = 1.5
        
        # Renal function modifiers
        if patient.egfr < 30:
            modifiers['renal_impairment'] = 2.0
        elif patient.egfr < 45:
            modifiers['renal_moderate'] = 1.5
        
        # Hepatic function
        if patient.liver_function == 'Abnormal':
            modifiers['hepatic_impairment'] = 1.8
        elif patient.liver_function == 'MildlyImpaired':
            modifiers['hepatic_mild'] = 1.3
        
        # BMI
        if patient.bmi < 18.5:
            modifiers['low_bmi'] = 1.3
        
        # Polypharmacy
        med_count = len(patient.medications)
        if med_count >= 10:
            modifiers['polypharmacy_10'] = 2.0
        elif med_count >= 8:
            modifiers['polypharmacy_8'] = 1.8
        elif med_count >= 5:
            modifiers['polypharmacy_5'] = 1.4
        
        # Comorbidities
        if 'Heart Failure' in patient.comorbidities:
            modifiers['heart_failure'] = 1.5
        
        # Smoking
        if patient.smoking == 'Current':
            modifiers['smoking'] = 1.2
        
        # ============================================================
        # NEW: BP MODIFIERS
        # ============================================================
        if patient.systolic_bp >= 180 or patient.diastolic_bp >= 120:
            modifiers['severe_hypertension'] = 1.6
        elif patient.systolic_bp >= 140 or patient.diastolic_bp >= 90:
            modifiers['uncontrolled_hypertension'] = 1.3
        
        return modifiers

    def detect_interactions(self, medication_list: List[str]) -> List[Interaction]:
        found_interactions = []
        for i, drug_a in enumerate(medication_list):
            for drug_b in medication_list[i+1:]:
                for interaction in self.interactions:
                    if (interaction.drug_a == drug_a and interaction.drug_b == drug_b) or \
                       (interaction.drug_a == drug_b and interaction.drug_b == drug_a):
                        found_interactions.append(interaction)
                        break
        return found_interactions

    def get_drug_info(self, drug_name: str) -> Optional[Drug]:
        return self.drugs.get(drug_name)

    def analyze_patient(self, patient: Patient) -> Dict[str, Any]:
        interactions = self.detect_interactions(patient.medications)
        modifiers = self.get_patient_modifiers(patient)
        
        severity_weights = {'Mild': 5, 'Moderate': 15, 'Severe': 30}
        raw_score = sum(severity_weights[i.severity.value] for i in interactions)
        
        adjusted_score = raw_score
        for multiplier in modifiers.values():
            adjusted_score *= multiplier
        adjusted_score = min(adjusted_score, 100)
        
        risk_level = "CRITICAL" if adjusted_score >= 70 else "HIGH" if adjusted_score >= 40 else "MODERATE" if adjusted_score >= 20 else "LOW"
        risk_color = {'CRITICAL': '#FF0000', 'HIGH': '#FF6600', 'MODERATE': '#FFCC00', 'LOW': '#00CC00'}[risk_level]
        
        deprescribing = self.suggest_deprescribing(patient)
        
        return {
            'patient': patient,
            'interactions': interactions,
            'modifiers': modifiers,
            'risk_score': adjusted_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'deprescribing_suggestions': deprescribing
        }

    def suggest_deprescribing(self, patient: Patient) -> List[Dict[str, Any]]:
        suggestions = []
        original_interactions = self.detect_interactions(patient.medications)
        severity_weights = {'Mild': 5, 'Moderate': 15, 'Severe': 30}
        
        for drug in patient.medications:
            contribution = 0
            for interaction in original_interactions:
                if interaction.drug_a == drug or interaction.drug_b == drug:
                    contribution += severity_weights[interaction.severity.value]
            
            if patient.age > 75:
                contribution *= 1.5
            
            drug_info = self.get_drug_info(drug)
            suggestions.append({
                'drug': drug,
                'drug_class': drug_info.drug_class if drug_info else 'Unknown',
                'risk_contribution': contribution,
                'priority': 'HIGH' if contribution > 20 else 'MEDIUM' if contribution > 10 else 'LOW'
            })
        
        suggestions.sort(key=lambda x: x['risk_contribution'], reverse=True)
        return suggestions

    def what_if_analysis(self, patient: Patient, scenario_type: str, drug_name: str) -> Dict[str, Any]:
        original = self.analyze_patient(patient)
        
        if scenario_type == 'add':
            new_meds = patient.medications + [drug_name]
        elif scenario_type == 'remove':
            new_meds = [m for m in patient.medications if m != drug_name]
        else:
            new_meds = patient.medications.copy()
        
        new_patient = Patient(
            patient_id=patient.patient_id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            bmi=patient.bmi,
            egfr=patient.egfr,
            liver_function=patient.liver_function,
            medications=new_meds,
            comorbidities=patient.comorbidities,
            allergies=patient.allergies,
            smoking=patient.smoking,
            alcohol=patient.alcohol,
            systolic_bp=patient.systolic_bp,
            diastolic_bp=patient.diastolic_bp
        )
        
        new_analysis = self.analyze_patient(new_patient)
        
        change = new_analysis['risk_score'] - original['risk_score']
        if change < 0:
            recommendation = f"✅ Risk reduced by {-change:.1f} points" if -change > 20 else f"✅ Minor risk reduction: {-change:.1f} points"
        else:
            recommendation = f"⚠️ Risk increased by {change:.1f} points" if change > 20 else f"⚠️ Minor risk increase: {change:.1f} points"
        
        return {
            'scenario_type': scenario_type,
            'drug_modified': drug_name,
            'original_risk': original['risk_score'],
            'new_risk': new_analysis['risk_score'],
            'risk_change': change,
            'risk_reduction': -change if change < 0 else 0,
            'original_level': original['risk_level'],
            'new_level': new_analysis['risk_level'],
            'recommendation': recommendation
        }


# ============================================================
# STREAMLIT UI
# ============================================================

def main():
    st.set_page_config(page_title="RxCompanion - AI- Assisted Polypharmacy Risk Analyzer", page_icon="💊", layout="wide")
    
    st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1E88E5; font-weight: bold; text-align: center; margin-bottom: 2rem; }
    .interaction-severe { background-color: #FFE5E5; border-left: 5px solid #FF0000; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0.3rem; }
    .interaction-moderate { background-color: #FFF3E5; border-left: 5px solid #FF6600; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0.3rem; }
    .interaction-mild { background-color: #FFFFE5; border-left: 5px solid #FFCC00; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0.3rem; }
    .bp-normal { background-color: #d4edda; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    .bp-elevated { background-color: #fff3cd; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    .bp-high { background-color: #f8d7da; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    .bp-severe { background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">💊 RxCompanion</div>', unsafe_allow_html=True)
    st.markdown("### AI- Assisted Polypharmacy Risk Analyzer")
    st.markdown("---")
    
    # Load analyzer
    @st.cache_resource
    def load_analyzer():
        return DrugInteractionAnalyzer('data/drugs.csv', 'data/interactions.csv')
    
    try:
        analyzer = load_analyzer()
    except FileNotFoundError:
        st.error("⚠️ Data files not found. Generating data...")
        generate_all_data()
        st.rerun()
    
    # ============================================================
    # BP SCAN FEATURE IN SIDEBAR
    # ============================================================
    with st.sidebar:
        st.header("👤 Patient Management")
        
        # BP Scan section
        with st.expander("📷 Scan BP from Image", expanded=False):
            if OCR_AVAILABLE:
                uploaded_file = st.file_uploader("Upload BP monitor photo", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    if st.button("🔍 Extract BP Reading"):
                        systolic, diastolic = extract_bp_from_image(uploaded_file)
                        if systolic and diastolic:
                            st.success(f"✅ Detected: {systolic}/{diastolic} mmHg")
                            st.session_state['scanned_sys'] = systolic
                            st.session_state['scanned_dia'] = diastolic
                        else:
                            st.error("❌ Could not detect BP. Please try a clearer image.")
            else:
                st.warning("⚠️ OCR libraries not installed. Run: pip install opencv-python pytesseract pillow numpy")
                st.info("You can still enter BP manually below.")
        
        patient_option = st.radio("Select Patient", ["Load Sample Patient", "Create New Patient"])
        
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
                        alcohol=patient_data['Alcohol'] if pd.notna(patient_data['Alcohol']) else 'None',
                        systolic_bp=int(patient_data.get('SystolicBP', 120)),
                        diastolic_bp=int(patient_data.get('DiastolicBP', 80))
                    )
                    st.success(f"✅ Loaded patient: {patient.name}")
            except FileNotFoundError:
                st.error("⚠️ Data files not found. Please generate data first.")
                st.stop()
        else:
            # Create New Patient Form
            name = st.text_input("Full Name", "John Doe")
            age = st.number_input("Age", min_value=18, max_value=120, value=72)
            gender = st.selectbox("Gender", ["M", "F"])
            bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=22.4)
            egfr = st.number_input("eGFR (mL/min)", min_value=5, max_value=120, value=45)
            liver_function = st.selectbox("Liver Function", ["Normal", "MildlyImpaired", "Abnormal"])
            
            # ============================================================
            # BP INPUT SECTION
            # ============================================================
            st.subheader("🩸 Blood Pressure")
            
            # Use scanned values if available, otherwise default
            default_sys = st.session_state.get('scanned_sys', 120)
            default_dia = st.session_state.get('scanned_dia', 80)
            
            col_bp1, col_bp2 = st.columns(2)
            with col_bp1:
                systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=80, max_value=250, value=default_sys)
            with col_bp2:
                diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=50, max_value=150, value=default_dia)
            
            # BP Status display
            if systolic_bp < 120 and diastolic_bp < 80:
                bp_status = "🟢 Normal"
                bp_class = "bp-normal"
            elif systolic_bp < 130 and diastolic_bp < 80:
                bp_status = "🟡 Elevated"
                bp_class = "bp-elevated"
            elif systolic_bp < 140 or diastolic_bp < 90:
                bp_status = "🟠 High (Stage 1)"
                bp_class = "bp-high"
            elif systolic_bp >= 140 or diastolic_bp >= 90:
                bp_status = "🔴 High (Stage 2)"
                bp_class = "bp-severe"
            else:
                bp_status = "🟢 Normal"
                bp_class = "bp-normal"
            
            st.markdown(f"**Status:** <span class='{bp_class}'>{bp_status}</span>", unsafe_allow_html=True)
            
            # Clear scanned values after use
            if st.session_state.get('scanned_sys'):
                st.session_state['scanned_sys'] = None
                st.session_state['scanned_dia'] = None
            
            all_drugs = list(analyzer.drugs.keys())
            medications = st.multiselect("Current Medications", all_drugs)
            comorbidities_text = st.text_input("Comorbidities (comma-separated)", "")
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
                    alcohol=alcohol,
                    systolic_bp=systolic_bp,
                    diastolic_bp=diastolic_bp
                )
                st.success(f"✅ Created patient: {patient.name}")
    
    # ============================================================
    # MAIN CONTENT
    # ============================================================
    if 'patient' in locals():
        try:
            analysis = analyzer.analyze_patient(patient)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                st.markdown("### 📊 Risk Score")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=analysis['risk_score'],
                    title={'text': "Risk Score", 'font': {'size': 14}},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': analysis['risk_color']},
                        'steps': [
                            {'range': [0, 20], 'color': "#00CC00"},
                            {'range': [20, 40], 'color': "#FFCC00"},
                            {'range': [40, 70], 'color': "#FF6600"},
                            {'range': [70, 100], 'color': "#FF0000"}
                        ]
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
                # Display BP in summary
                bp_display = f"{patient.systolic_bp}/{patient.diastolic_bp} mmHg"
                if patient.systolic_bp >= 140 or patient.diastolic_bp >= 90:
                    bp_display += " ⚠️"
                st.markdown(f"**BP:** {bp_display}")
                st.markdown(f"**Medications:** {len(patient.medications)}")
            
            with col3:
                st.markdown("### 💊 Medication List")
                for drug in patient.medications:
                    drug_info = analyzer.get_drug_info(drug)
                    if drug_info:
                        st.markdown(f"• **{drug}** ({drug_info.drug_class})")
                    else:
                        st.markdown(f"• {drug}")
            
            st.markdown("---")
            st.markdown("### 🔍 Detected Interactions")
            
            if analysis['interactions']:
                for interaction in analysis['interactions']:
                    severity_class = {'Severe': 'interaction-severe', 'Moderate': 'interaction-moderate', 'Mild': 'interaction-mild'}[interaction.severity.value]
                    emoji = {'Severe': '🔴', 'Moderate': '🟠', 'Mild': '🟡'}[interaction.severity.value]
                    st.markdown(f"""
                    <div class="{severity_class}">
                        <b>{emoji} {interaction.drug_a} + {interaction.drug_b}</b>
                        <br><b>Severity:</b> {interaction.severity.value}
                        <br><b>Mechanism:</b> {interaction.mechanism}
                        <br><b>Recommendation:</b> {interaction.recommendation}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No interactions detected!")
            
            st.markdown("---")
            st.markdown("### 🎯 Deprescribing Suggestions")
            
            if analysis['deprescribing_suggestions']:
                for i, suggestion in enumerate(analysis['deprescribing_suggestions'][:5]):
                    priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟢'}.get(suggestion['priority'], '⚪')
                    st.markdown(f"""
                    <div style="background:#F5F5F5; padding:0.5rem; margin:0.3rem 0; border-radius:0.3rem;">
                        <b>{i+1}. {suggestion['drug']}</b> ({suggestion['drug_class']})
                        <br><b>Risk Contribution:</b> {suggestion['risk_contribution']:.1f} points
                        <br><b>Priority:</b> {priority_icon} {suggestion['priority']}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🔮 What-If Analysis")
            
            what_if_col1, what_if_col2 = st.columns([2, 1])
            
            with what_if_col1:
                scenario_type = st.selectbox("Scenario Type", ["Add Medication", "Remove Medication"])
                if scenario_type == "Add Medication":
                    available_drugs = [d for d in list(analyzer.drugs.keys()) if d not in patient.medications]
                    drug_to_modify = st.selectbox("Select drug to add", available_drugs) if available_drugs else None
                else:
                    drug_to_modify = st.selectbox("Select drug to remove", patient.medications) if patient.medications else None
            
            with what_if_col2:
                if drug_to_modify and st.button("Run Simulation", use_container_width=True):
                    scenario = 'add' if scenario_type == "Add Medication" else 'remove'
                    result = analyzer.what_if_analysis(patient, scenario, drug_to_modify)
                    
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Original Risk**")
                        st.markdown(f"<h2>{analysis['risk_score']:.0f}</h2>", unsafe_allow_html=True)
                    with col2:
                        change = result['risk_change']
                        st.markdown("**Change**")
                        st.markdown(f"<h2 style='color:{'green' if change < 0 else 'red'}'>{'⬇️' if change < 0 else '⬆️'} {abs(change):.0f}</h2>", unsafe_allow_html=True)
                    with col3:
                        st.markdown("**New Risk**")
                        st.markdown(f"<h2 style='color:{'green' if result['new_risk'] < result['original_risk'] else 'red'}'>{result['new_risk']:.0f}</h2>", unsafe_allow_html=True)
                    
                    st.markdown(f"**Recommendation:** {result['recommendation']}")
            
            # ============================================================
            # 📤 EXPORT REPORT - DOWNLOAD OPTION
            # ============================================================
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
- Blood Pressure: {patient.systolic_bp}/{patient.diastolic_bp} mmHg

## Risk Assessment
- Risk Score: {analysis['risk_score']:.1f}/100
- Risk Level: {analysis['risk_level']}

## Interactions Detected: {len(analysis['interactions'])}

## Recommendations
"""
                for i, suggestion in enumerate(analysis['deprescribing_suggestions'][:5]):
                    report += f"\n{i+1}. Consider reviewing {suggestion['drug']} (Priority: {suggestion['priority']}, Risk Contribution: {suggestion['risk_contribution']:.1f})"

                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"RxCompanion_Report_{patient.name.replace(' ', '_')}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("👈 Please select or create a patient from the sidebar")

# ============================================================
# RUN THE APP
# ============================================================

if __name__ == "__main__":
    # Generate data if not already present
    if not os.path.exists('data/drugs.csv'):
        generate_all_data()
    
    main()
