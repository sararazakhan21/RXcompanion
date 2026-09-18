import pandas as pd
import random

def generate_drugs():
    """Generate drug database - 50 drugs"""
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
        ["D031", "Pioglitazone", "Thiazolidinedione", "CYP2C8", "Oral", 45, "mg", "Edema|Heart failure|Weight gain", "Heart failure NYHA III/IV", "Weight monthly", "C"],
        ["D032", "Sitagliptin", "DPP-4 inhibitor", "Renal excretion", "Oral", 100, "mg", "Pancreatitis|Arthralgia", "eGFR<30", "Renal function monthly", "B"],
        ["D033", "Fenofibrate", "Fibrate", "UGT1A9", "Oral", 160, "mg", "Myopathy|Gallstones", "Liver disease|Severe renal", "Creatinine monthly", "C"],
        ["D034", "Apixaban", "Direct Xa inhibitor", "CYP3A4", "Oral", 10, "mg", "Bleeding|Hepatotoxicity", "Active bleeding|Severe liver", "Creatinine quarterly", "C"],
        ["D035", "Rivaroxaban", "Direct Xa inhibitor", "CYP3A4", "Oral", 20, "mg", "Bleeding|Hepatotoxicity", "Active bleeding|Severe liver", "Creatinine quarterly", "C"],
        ["D036", "Dabigatran", "Direct thrombin inhibitor", "P-gp", "Oral", 300, "mg", "Bleeding|Dyspepsia", "Active bleeding|CrCl<30", "Creatinine quarterly", "C"],
        ["D037", "Enoxaparin", "LMWH", "Renal excretion", "Subcutaneous", 80, "mg", "Bleeding|Thrombocytopenia", "Active bleeding|HIT", "Platelets monthly", "B"],
        ["D038", "Erythropoietin", "Hormone", "Liver", "Subcutaneous", 40000, "units", "Thrombosis|Hypertension", "Hemoglobin>12|Uncontrolled HTN", "BP weekly", "B"],
        ["D039", "Sevelamer", "Phosphate binder", "Oral", "Oral", 2400, "mg", "GI upset|Constipation", "Bowel obstruction", "Phosphate monthly", "B"],
        ["D040", "Calcium Carbonate", "Calcium supplement", "Oral", "Oral", 3000, "mg", "Hypercalcemia|Constipation", "Hypercalcemia", "Calcium monthly", "B"],
        ["D041", "Cinacalcet", "Calcimimetic", "CYP3A4", "Oral", 120, "mg", "Hypocalcemia|QT prolongation", "Hypocalcemia", "Calcium weekly", "B"],
        ["D042", "Calcitriol", "Vitamin D analog", "CYP3A4", "Oral", 1, "mcg", "Hypercalcemia|Hyperphosphatemia", "Hypercalcemia", "Calcium monthly", "B"],
        ["D043", "Iron Sucrose", "Iron supplement", "Oral", "Oral", 300, "mg", "GI upset|Constipation", "Iron overload|Anaphylaxis", "Ferritin monthly", "B"],
        ["D044", "Folic Acid", "Vitamin B9", "Oral", "Oral", 5, "mg", "GI upset", "None", "CBC monthly", "A"],
        ["D045", "Metronidazole", "Antibiotic", "CYP2C9", "Oral", 1500, "mg", "Nausea|Headache", "Alcohol", "Liver function", "B"],
        ["D046", "Amiodarone", "Antiarrhythmic", "CYP3A4", "Oral", 400, "mg", "Pulmonary toxicity|Thyroid", "Liver disease", "LFTs quarterly", "D"],
        ["D047", "Theophylline", "Bronchodilator", "CYP1A2", "Oral", 900, "mg", "Tachycardia|Seizures", "CYP1A2 interactions", "Theophylline level", "C"],
        ["D048", "Methotrexate", "Immunosuppressant", "Renal", "Oral", 25, "mg", "Hepatotoxicity|Myelosuppression", "Renal impairment", "CBC monthly", "X"],
        ["D049", "Insulin Aspart", "Insulin", "Subcutaneous", "Subcutaneous", 100, "units", "Hypoglycemia|Lipodystrophy", "Hypoglycemia", "Glucose daily", "B"],
        ["D050", "Thyroxine", "Thyroid hormone", "Liver", "Oral", 200, "mcg", "Palpitations|Tachycardia", "Untreated hyperthyroidism", "TSH quarterly", "A"]
    ]
    return pd.DataFrame(drugs, columns=[
        "DrugID", "DrugName", "DrugClass", "Metabolism", "Route",
        "MaxDailyDose", "Unit", "CommonSideEffects", "Contraindications",
        "MonitoringRequired", "PregnancyRisk"
    ])


def generate_interactions():
    """Generate interaction database - 40 interactions"""
    interactions = [
        ["I001", "Warfarin", "Aspirin", "Severe", "Increased bleeding risk", "Avoid combination", "Strong", "Immediate", "INR weekly|CBC monthly"],
        ["I002", "Warfarin", "Simvastatin", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-7 days", "INR weekly"],
        ["I003", "Warfarin", "Ciprofloxacin", "Severe", "INR increase", "Avoid if possible", "Strong", "2-5 days", "INR daily"],
        ["I004", "Warfarin", "Amiodarone", "Severe", "INR increase", "Reduce warfarin dose", "Strong", "1-2 weeks", "INR weekly"],
        ["I005", "Warfarin", "Celecoxib", "Moderate", "Increased bleeding risk", "Monitor for bleeding", "Moderate", "Immediate", "INR weekly"],
        ["I006", "Warfarin", "Clopidogrel", "Severe", "Bleeding risk", "Avoid if possible", "Strong", "Immediate", "INR weekly|CBC monthly"],
        ["I007", "Warfarin", "Allopurinol", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-5 days", "INR weekly"],
        ["I008", "Warfarin", "Omeprazole", "Moderate", "Increased INR", "Monitor INR", "Weak", "3-7 days", "INR weekly"],
        ["I009", "Warfarin", "Furosemide", "Moderate", "Decreased warfarin effect", "Monitor INR", "Weak", "3-5 days", "INR weekly|BP weekly"],
        ["I010", "Warfarin", "Metronidazole", "Severe", "INR increase", "Avoid if possible", "Strong", "2-5 days", "INR daily"],
        ["I011", "Lisinopril", "Furosemide", "Moderate", "Hypotension risk", "Monitor BP", "Strong", "Immediate", "BP daily|Electrolytes weekly"],
        ["I012", "Lisinopril", "Losartan", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly|Creatinine weekly"],
        ["I013", "Lisinopril", "Spironolactone", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly|Creatinine weekly"],
        ["I014", "Lisinopril", "Aspirin", "Moderate", "Reduced ACE effect", "Monitor BP", "Weak", "1-3 days", "BP weekly"],
        ["I015", "Lisinopril", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I016", "Lisinopril", "Digoxin", "Moderate", "Digoxin toxicity", "Monitor K+", "Moderate", "1-2 weeks", "K+ weekly|Digoxin level"],
        ["I017", "Metformin", "Furosemide", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I018", "Metformin", "Digoxin", "Moderate", "Digoxin toxicity", "Monitor digoxin levels", "Moderate", "1-2 weeks", "Digoxin level quarterly"],
        ["I019", "Metformin", "Ciprofloxacin", "Moderate", "Increased metformin levels", "Monitor renal function", "Moderate", "1-3 days", "Creatinine monthly"],
        ["I020", "Digoxin", "Furosemide", "Moderate", "Hypokalemia increases toxicity", "Monitor K+", "Strong", "1-7 days", "K+ weekly|Digoxin level"],
        ["I021", "Digoxin", "Amlodipine", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "3-5 days", "Digoxin level quarterly"],
        ["I022", "Digoxin", "Spironolactone", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "3-5 days", "Digoxin level quarterly"],
        ["I023", "Amlodipine", "Simvastatin", "Moderate", "Increased statin toxicity", "Limit simvastatin dose", "Strong", "1-2 weeks", "LFTs quarterly"],
        ["I024", "Amlodipine", "Metoprolol", "Mild", "Bradycardia risk", "Monitor HR", "Moderate", "Immediate", "HR weekly"],
        ["I025", "Amlodipine", "Diltiazem", "Mild", "Heart block risk", "Monitor HR", "Moderate", "Immediate", "HR weekly"],
        ["I026", "Amlodipine", "Atorvastatin", "Moderate", "Increased statin toxicity", "Limit atorvastatin dose", "Strong", "1-2 weeks", "LFTs quarterly"],
        ["I027", "Aspirin", "Clopidogrel", "Severe", "Bleeding risk", "Use only when necessary", "Strong", "Immediate", "CBC monthly"],
        ["I028", "Aspirin", "Apixaban", "Severe", "Bleeding risk", "Avoid if possible", "Strong", "Immediate", "CBC monthly"],
        ["I029", "Aspirin", "Omeprazole", "Moderate", "Reduced antiplatelet effect", "Use pantoprazole", "Moderate", "3-5 days", "GI symptoms"],
        ["I030", "Atorvastatin", "Clopidogrel", "Moderate", "Reduced clopidogrel effect", "Consider pravastatin", "Weak", "3-7 days", "CBC if symptoms"],
        ["I031", "Omeprazole", "Clopidogrel", "Moderate", "Reduced clopidogrel effect", "Use pantoprazole", "Strong", "3-5 days", "CBC if symptoms"],
        ["I032", "Omeprazole", "Digoxin", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "5-7 days", "Digoxin level quarterly"],
        ["I033", "Dapagliflozin", "Furosemide", "Moderate", "Dehydration risk", "Monitor volume status", "Moderate", "Immediate", "BP weekly"],
        ["I034", "Dapagliflozin", "Insulin", "Moderate", "Hypoglycemia risk", "Reduce insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I035", "Dapagliflozin", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I036", "Insulin", "Metoprolol", "Moderate", "Hypoglycemia symptoms masked", "Monitor glucose closely", "Moderate", "Immediate", "Glucose daily"],
        ["I037", "Insulin", "Metformin", "Moderate", "Hypoglycemia risk", "Monitor glucose", "Moderate", "Immediate", "Glucose daily"],
        ["I038", "Insulin", "Prednisolone", "Severe", "Hyperglycemia", "Increase insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I039", "Spironolactone", "Losartan", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"],
        ["I040", "Ramipril", "Spironolactone", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"]
    ]
    return pd.DataFrame(interactions, columns=[
        "InteractionID", "DrugA", "DrugB", "Severity", "Mechanism",
        "Recommendation", "EvidenceLevel", "TimeToOnset", "MonitoringRequired"
    ])


def generate_patients(n=20):
    """Generate realistic patient profiles"""
    patients = []

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
                   "Prednisolone", "Diltiazem", "Carvedilol", "Ramipril", "Rosuvastatin",
                   "Hydrochlorothiazide", "Empagliflozin"]

    comorbidities_list = [
        "Hypertension", "Diabetes", "Atrial Fibrillation", "Heart Failure", "CKD",
        "CAD", "Hyperlipidemia", "Osteoarthritis", "GERD", "Hypothyroidism",
        "Neuropathy", "Gout", "COPD"
    ]

    smoking_status = ["No", "Former", "Current"]
    alcohol_status = ["None", "Occasional", "Moderate", "Heavy"]
    liver_status = ["Normal", "MildlyImpaired", "Abnormal"]

    for i in range(n):
        age = random.randint(65, 85)
        gender = random.choice(["M", "F"])
        bmi = round(random.uniform(18, 35), 1)
        egfr = round(max(15, 120 - (age - 60) * 1.5 + random.uniform(-15, 15)), 0)

        num_meds = random.randint(4, 8)
        selected_meds = random.sample(common_meds, min(num_meds, len(common_meds)))

        num_comorbidities = random.randint(1, 4)
        selected_comorbidities = random.sample(comorbidities_list, min(num_comorbidities, len(comorbidities_list)))

        patients.append({
            'PatientID': f"P{i+1:03d}",
            'Name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'Age': age,
            'Gender': gender,
            'BMI': bmi,
            'eGFR': egfr,
            'LiverFunction': random.choices(liver_status, weights=[0.7, 0.2, 0.1])[0],
            'Medications': '|'.join(selected_meds),
            'Comorbidities': '|'.join(selected_comorbidities),
            'Allergies': '',
            'Smoking': random.choices(smoking_status, weights=[0.6, 0.3, 0.1])[0],
            'Alcohol': random.choices(alcohol_status, weights=[0.5, 0.3, 0.15, 0.05])[0]
        })

    return pd.DataFrame(patients)


def generate_risk_modifiers():
    """Generate risk modifiers"""
    modifiers = [
        ["R001", "Age_Elderly", "Age", "Age", 75, 1.5, "Strong"],
        ["R002", "Age_VeryElderly", "Age", "Age", 85, 2.0, "Strong"],
        ["R003", "Renal_Impairment", "eGFR", "eGFR", 30, 2.0, "Strong"],
        ["R004", "Renal_Moderate", "eGFR", "eGFR", 45, 1.5, "Moderate"],
        ["R005", "Hepatic_Impairment", "LiverFunction", "LiverFunction", "Abnormal", 1.8, "Strong"],
        ["R006", "Hepatic_Mild", "LiverFunction", "LiverFunction", "MildlyImpaired", 1.3, "Moderate"],
        ["R007", "LOW_BMI", "BMI", "BMI", 18.5, 1.3, "Moderate"],
        ["R008", "Polypharmacy_5", "NumberOfDrugs", "NumberOfDrugs", 5, 1.4, "Strong"],
        ["R009", "Polypharmacy_8", "NumberOfDrugs", "NumberOfDrugs", 8, 1.8, "Strong"],
        ["R010", "Polypharmacy_10", "NumberOfDrugs", "NumberOfDrugs", 10, 2.0, "Strong"],
        ["R011", "Smoking", "Smoking", "Smoking", "Current", 1.2, "Weak"],
    ]
    return pd.DataFrame(modifiers, columns=[
        "ModifierID", "ModifierName", "Condition", "Measurement",
        "Threshold", "RiskMultiplier", "EvidenceLevel"
    ])


if __name__ == "__main__":
    import os

    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    print("Generating drug database...")
    drugs_df = generate_drugs()
    drugs_df.to_csv('data/drugs.csv', index=False)
    print(f"✅ Generated {len(drugs_df)} drugs")

    print("Generating interactions...")
    interactions_df = generate_interactions()
    interactions_df.to_csv('data/interactions.csv', index=False)
    print(f"✅ Generated {len(interactions_df)} interactions")

    print("Generating patient profiles...")
    patients_df = generate_patients(20)
    patients_df.to_csv('data/patients.csv', index=False)
    print(f"✅ Generated {len(patients_df)} patients")

    print("Generating risk modifiers...")
    modifiers_df = generate_risk_modifiers()
    modifiers_df.to_csv('data/risk_modifiers.csv', index=False)
    print(f"✅ Generated {len(modifiers_df)} risk modifiers")

    print("\n✅ All data files generated successfully!")
    print("\n📁 Files created in 'data/' folder:")
    print("   - drugs.csv")
    print("   - interactions.csv")
    print("   - patients.csv")
    print("   - risk_modifiers.csv")
    print("\n🚀 Now run: streamlit run app.py")