import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import os
import io
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from PIL import Image
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

# ============================================================
# DOSE ADJUSTMENT KNOWLEDGE BASE
# ============================================================
DOSE_ADJUSTMENT_RULES = {
    "Metformin": {"egfr_rules": [
        {"min": 45, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
        {"min": 30, "max": 45, "text": "Reduce dose to max 1000 mg/day. Monitor renal function every 3 months.", "level": "warning"},
        {"min": 0, "max": 30, "text": "CONTRAINDICATED. Discontinue metformin. High risk of lactic acidosis.", "level": "critical"},
    ]},
    "Digoxin": {
        "egfr_rules": [
            {"min": 50, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
            {"min": 30, "max": 50, "text": "Reduce dose by 25-50%. Monitor digoxin levels and potassium.", "level": "warning"},
            {"min": 0, "max": 30, "text": "Reduce dose by 50-75%. Monitor digoxin levels weekly.", "level": "critical"},
        ],
        "k_rules": [
            {"min": 0, "max": 3.5, "text": "Hypokalemia increases digoxin toxicity risk. Correct K+ before continuing.", "level": "critical"},
        ],
    },
    "Lisinopril": {
        "egfr_rules": [
            {"min": 30, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
            {"min": 0, "max": 30, "text": "Start with low dose (2.5-5 mg). Monitor K+ and creatinine closely.", "level": "warning"},
        ],
        "k_rules": [
            {"min": 5.5, "max": 999, "text": "SEVERE HYPERKALEMIA. Avoid ACE inhibitors. Risk of cardiac arrhythmia.", "level": "critical"},
            {"min": 5.0, "max": 5.5, "text": "Moderate hyperkalemia. Monitor K+ weekly. Consider dose reduction.", "level": "warning"},
        ],
    },
    "Ramipril": {
        "egfr_rules": [
            {"min": 30, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
            {"min": 0, "max": 30, "text": "Start with 1.25-2.5 mg. Monitor K+ and creatinine.", "level": "warning"},
        ],
        "k_rules": [
            {"min": 5.5, "max": 999, "text": "SEVERE HYPERKALEMIA. Avoid ACE inhibitors.", "level": "critical"},
            {"min": 5.0, "max": 5.5, "text": "Moderate hyperkalemia. Monitor K+.", "level": "warning"},
        ],
    },
    "Losartan": {
        "egfr_rules": [
            {"min": 30, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
            {"min": 0, "max": 30, "text": "Start with low dose (25 mg). Monitor K+ and creatinine.", "level": "warning"},
        ],
        "k_rules": [
            {"min": 5.5, "max": 999, "text": "SEVERE HYPERKALEMIA. Avoid ARBs.", "level": "critical"},
            {"min": 5.0, "max": 5.5, "text": "Moderate hyperkalemia. Monitor K+.", "level": "warning"},
        ],
    },
    "Spironolactone": {
        "egfr_rules": [
            {"min": 30, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
            {"min": 0, "max": 30, "text": "AVOID. High risk of hyperkalemia in renal impairment.", "level": "critical"},
        ],
        "k_rules": [
            {"min": 5.0, "max": 999, "text": "CONTRAINDICATED. Do not use with K+ > 5.0 mEq/L.", "level": "critical"},
        ],
    },
    "Allopurinol": {"egfr_rules": [
        {"min": 60, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
        {"min": 30, "max": 60, "text": "Reduce dose to 200 mg/day.", "level": "warning"},
        {"min": 0, "max": 30, "text": "Reduce dose to 100 mg/day. Monitor for hypersensitivity.", "level": "critical"},
    ]},
    "Gabapentin": {"egfr_rules": [
        {"min": 60, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
        {"min": 30, "max": 60, "text": "Reduce dose to 600-1200 mg/day in divided doses.", "level": "warning"},
        {"min": 15, "max": 30, "text": "Reduce dose to 300-600 mg/day.", "level": "warning"},
        {"min": 0, "max": 15, "text": "Reduce dose to 150-300 mg/day. Monitor sedation.", "level": "critical"},
    ]},
    "Ciprofloxacin": {"egfr_rules": [
        {"min": 30, "max": 999, "text": "No renal adjustment required.", "level": "normal"},
        {"min": 0, "max": 30, "text": "Reduce dose to 250-500 mg every 24 hours.", "level": "warning"},
    ]},
    "Furosemide": {"k_rules": [
        {"min": 0, "max": 3.0, "text": "SEVERE HYPOKALEMIA. Reduce dose or add K+ supplement.", "level": "critical"},
        {"min": 3.0, "max": 3.5, "text": "Mild hypokalemia. Monitor K+ and consider supplementation.", "level": "warning"},
    ]},
    "Insulin Glargine": {"egfr_rules": [
        {"min": 50, "max": 999, "text": "No adjustment required.", "level": "normal"},
        {"min": 0, "max": 50, "text": "Reduce dose by 20-30% (insulin clearance reduced). Monitor glucose closely.", "level": "warning"},
    ]},
}


def get_dose_adjustments(patient_meds, egfr, potassium):
    adjustments = []
    for drug in patient_meds:
        rules = DOSE_ADJUSTMENT_RULES.get(drug)
        if not rules:
            continue
        if "egfr_rules" in rules:
            for rule in rules["egfr_rules"]:
                if rule["min"] <= egfr < rule["max"]:
                    adjustments.append({"drug": drug, "parameter": "eGFR",
                        "value": f"{egfr:.0f} mL/min", "recommendation": rule["text"], "level": rule["level"]})
                    break
        if "k_rules" in rules and potassium is not None:
            for rule in rules["k_rules"]:
                if rule["min"] <= potassium < rule["max"]:
                    adjustments.append({"drug": drug, "parameter": "Potassium",
                        "value": f"{potassium:.1f} mEq/L", "recommendation": rule["text"], "level": rule["level"]})
                    break
    return adjustments


# ============================================================
# PDF REPORT
# ============================================================
def generate_pdf_report(patient, analysis, dose_adjustments) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
        textColor=colors.HexColor("#0B3C5D"), spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#1D7874"), spaceAfter=20, alignment=TA_CENTER, fontName="Helvetica-Oblique")
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#0B3C5D"), spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold")
    body = ParagraphStyle("B", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#1A202C"), leading=14)

    story = []
    story.append(Paragraph("RxCompanion Clinical Report", title_style))
    story.append(Paragraph(f"Polypharmacy Risk Assessment | Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", sub_style))

    story.append(Paragraph("Patient Information", h2))
    pd_data = [
        ["Name", patient.name, "Age / Gender", f"{patient.age} y / {patient.gender}"],
        ["BMI", f"{patient.bmi:.1f} kg/m2", "Liver Function", patient.liver_function],
        ["eGFR", f"{patient.egfr:.0f} mL/min", "Creatinine", f"{patient.creatinine:.2f} mg/dL"],
        ["Blood Pressure", f"{patient.systolic_bp}/{patient.diastolic_bp} mmHg", "Potassium", f"{patient.potassium:.1f} mEq/L"],
        ["Medications", f"{len(patient.medications)} drugs", "Comorbidities", ", ".join(patient.comorbidities) if patient.comorbidities else "-"],
    ]
    t = Table(pd_data, colWidths=[1.3 * inch, 2.0 * inch, 1.3 * inch, 2.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F1F5F9")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    story.append(Paragraph("Risk Assessment", h2))
    risk_color = {"CRITICAL": colors.HexColor("#C53030"), "HIGH": colors.HexColor("#DD6B20"),
                  "MODERATE": colors.HexColor("#D69E2E"), "LOW": colors.HexColor("#38A169")}.get(analysis["risk_level"], colors.grey)
    t2 = Table([["Risk Score", f"{analysis['risk_score']:.0f} / 100", "Risk Level", analysis["risk_level"]]],
               colWidths=[1.3 * inch, 2.0 * inch, 1.3 * inch, 2.0 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR", (3, 0), (3, 0), risk_color),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    story.append(Paragraph("Detected Drug Interactions", h2))
    if analysis["interactions"]:
        d = [["Drug A", "Drug B", "Severity", "Recommendation"]]
        for i in analysis["interactions"]:
            d.append([i.drug_a, i.drug_b, i.severity.value, i.recommendation])
        t3 = Table(d, colWidths=[1.1 * inch, 1.1 * inch, 0.9 * inch, 3.5 * inch])
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3C5D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No interactions detected.", body))

    if dose_adjustments:
        story.append(Paragraph("Dose Adjustment Recommendations", h2))
        d = [["Drug", "Parameter", "Value", "Recommendation"]]
        for a in dose_adjustments:
            d.append([a["drug"], a["parameter"], a["value"], a["recommendation"]])
        t4 = Table(d, colWidths=[1.1 * inch, 0.9 * inch, 1.0 * inch, 3.6 * inch])
        t4.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D7874")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t4)

    if analysis["deprescribing_suggestions"]:
        story.append(Paragraph("Deprescribing Suggestions", h2))
        d = [["Priority", "Drug", "Risk Contribution", "Class"]]
        for s in analysis["deprescribing_suggestions"][:5]:
            d.append([s["priority"], s["drug"], f"{s['risk_contribution']:.1f} pts", s["drug_class"]])
        t5 = Table(d, colWidths=[1.0 * inch, 1.6 * inch, 1.5 * inch, 2.5 * inch])
        t5.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3C5D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t5)

    story.append(Spacer(1, 20))
    disc = ParagraphStyle("D", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#718096"), leading=11, fontName="Helvetica-Oblique")
    story.append(Paragraph("<b>Disclaimer:</b> This report is generated by RxCompanion, a Decision Support System, for informational purposes only. It does not constitute medical advice.", disc))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# DATA GENERATION
# ============================================================
def generate_all_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    drugs = [
        ["D001", "Warfarin", "Anticoagulant", "CYP2C9", "Oral", 10, "mg", "Bleeding|Nausea", "Active bleeding|Pregnancy", "INR weekly", "X"],
        ["D002", "Metformin", "Antidiabetic", "Renal excretion", "Oral", 2550, "mg", "GI upset|Lactic acidosis", "eGFR<30|Heart failure", "Renal function monthly", "B"],
        ["D003", "Lisinopril", "ACE Inhibitor", "Renal excretion", "Oral", 40, "mg", "Cough|Hyperkalemia", "Pregnancy|Bilateral renal stenosis", "K+ weekly", "D"],
        ["D004", "Amlodipine", "Calcium Channel Blocker", "CYP3A4", "Oral", 10, "mg", "Edema|Dizziness", "Hypotension", "BP weekly", "C"],
        ["D005", "Simvastatin", "Statin", "CYP3A4", "Oral", 40, "mg", "Myopathy|Liver toxicity", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D006", "Digoxin", "Cardiac glycoside", "Renal excretion", "Oral", 0.25, "mg", "Arrhythmia|Nausea", "Hypokalemia|AV block", "Digoxin level quarterly", "C"],
        ["D007", "Furosemide", "Loop diuretic", "Renal excretion", "Oral", 80, "mg", "Electrolyte imbalance", "Renal failure", "Electrolytes weekly", "C"],
        ["D008", "Metoprolol", "Beta-blocker", "CYP2D6", "Oral", 200, "mg", "Bradycardia|Fatigue", "Bradycardia|Asthma", "HR weekly", "C"],
        ["D009", "Losartan", "ARB", "CYP2C9", "Oral", 100, "mg", "Hyperkalemia|Dizziness", "Pregnancy|Bilateral renal stenosis", "K+ weekly", "D"],
        ["D010", "Aspirin", "Antiplatelet", "Hydrolysis", "Oral", 325, "mg", "GI bleeding|Ulcers", "Active bleeding|Asthma", "GI symptoms quarterly", "C"],
        ["D011", "Atorvastatin", "Statin", "CYP3A4", "Oral", 80, "mg", "Myopathy|Liver toxicity", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D012", "Clopidogrel", "Antiplatelet", "CYP2C19", "Oral", 75, "mg", "Bleeding|GI upset", "Active bleeding|Liver disease", "CBC quarterly", "B"],
        ["D013", "Omeprazole", "PPI", "CYP2C19", "Oral", 40, "mg", "Gastric polyps|B12 deficiency", "Long-term use", "Mag/B12 yearly", "C"],
        ["D014", "Dapagliflozin", "SGLT2 inhibitor", "UGT1A9", "Oral", 10, "mg", "UTI|Dehydration", "eGFR<30", "Volume status monthly", "C"],
        ["D015", "Insulin Glargine", "Insulin", "Subcutaneous", "Subcutaneous", 100, "units", "Hypoglycemia|Weight gain", "Hypoglycemia", "Glucose daily", "B"],
        ["D016", "Levothyroxine", "Thyroid hormone", "Liver", "Oral", 200, "mcg", "Palpitations", "Untreated hyperthyroidism", "TSH quarterly", "A"],
        ["D017", "Gabapentin", "Anticonvulsant", "Renal excretion", "Oral", 3600, "mg", "Drowsiness|Dizziness", "CrCl<15", "Creatinine monthly", "C"],
        ["D018", "Tramadol", "Opioid analgesic", "CYP2D6", "Oral", 400, "mg", "Nausea|Dizziness|Seizures", "Seizure disorder|MAOIs", "Respiratory rate monthly", "C"],
        ["D019", "Celecoxib", "COX-2 inhibitor", "CYP2C9", "Oral", 200, "mg", "CV events|GI bleeding", "NSAID allergy|Severe heart disease", "BP monthly", "C"],
        ["D020", "Allopurinol", "Xanthine oxidase inhibitor", "Renal excretion", "Oral", 800, "mg", "Rash|Hepatotoxicity", "CrCl<30", "Creatinine monthly", "B"],
        ["D021", "Spironolactone", "Aldosterone antagonist", "CYP3A4", "Oral", 100, "mg", "Hyperkalemia|Gynecomastia", "Addison's disease", "K+ weekly", "B"],
        ["D022", "Ciprofloxacin", "Antibiotic", "CYP1A2", "Oral", 1500, "mg", "Tendonitis|QT prolongation", "CYP1A2 interactions", "ECG if risk", "B"],
        ["D023", "Prednisolone", "Corticosteroid", "CYP3A4", "Oral", 60, "mg", "Hyperglycemia|Immunosuppression", "Active infection", "Glucose weekly", "C"],
        ["D024", "Diltiazem", "Calcium Channel Blocker", "CYP3A4", "Oral", 360, "mg", "Bradycardia|Heart block", "Hypotension|AV block", "HR weekly", "C"],
        ["D025", "Carvedilol", "Beta-blocker", "CYP2D6", "Oral", 50, "mg", "Bradycardia|Hypotension", "Asthma|2nd degree AV block", "BP weekly", "C"],
        ["D026", "Ramipril", "ACE Inhibitor", "Renal excretion", "Oral", 10, "mg", "Cough|Hyperkalemia", "Pregnancy", "K+ quarterly", "D"],
        ["D027", "Rosuvastatin", "Statin", "CYP2C9", "Oral", 40, "mg", "Myopathy|Liver toxicity", "Pregnancy|Active liver disease", "LFTs quarterly", "X"],
        ["D028", "Hydrochlorothiazide", "Thiazide diuretic", "Renal excretion", "Oral", 25, "mg", "Hypokalemia|Hyperglycemia", "Sulfa allergy", "Electrolytes quarterly", "B"],
        ["D029", "Empagliflozin", "SGLT2 inhibitor", "UGT1A9", "Oral", 25, "mg", "UTI|Dehydration", "eGFR<30", "Volume status monthly", "C"],
        ["D030", "Glimepiride", "Sulfonylurea", "CYP2C9", "Oral", 8, "mg", "Hypoglycemia|Weight gain", "Sulfa allergy|eGFR<30", "Glucose daily", "C"],
    ]
    pd.DataFrame(drugs, columns=["DrugID", "DrugName", "DrugClass", "Metabolism", "Route",
        "MaxDailyDose", "Unit", "CommonSideEffects", "Contraindications",
        "MonitoringRequired", "PregnancyRisk"]).to_csv("data/drugs.csv", index=False)

    ix = [
        ["I001", "Warfarin", "Aspirin", "Severe", "Increased bleeding risk", "Avoid combination", "Strong", "Immediate", "INR weekly|CBC monthly"],
        ["I002", "Warfarin", "Simvastatin", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-7 days", "INR weekly"],
        ["I003", "Warfarin", "Ciprofloxacin", "Severe", "INR increase", "Avoid if possible", "Strong", "2-5 days", "INR daily"],
        ["I004", "Warfarin", "Omeprazole", "Moderate", "Increased INR", "Monitor INR", "Weak", "3-7 days", "INR weekly"],
        ["I005", "Warfarin", "Furosemide", "Moderate", "Decreased warfarin effect", "Monitor INR", "Weak", "3-5 days", "INR weekly"],
        ["I006", "Lisinopril", "Furosemide", "Moderate", "Hypotension risk", "Monitor BP", "Strong", "Immediate", "BP daily"],
        ["I007", "Lisinopril", "Losartan", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly"],
        ["I008", "Lisinopril", "Spironolactone", "Severe", "Hyperkalemia risk", "Avoid combination", "Strong", "1-2 weeks", "K+ weekly"],
        ["I009", "Lisinopril", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I010", "Lisinopril", "Digoxin", "Moderate", "Digoxin toxicity", "Monitor K+", "Moderate", "1-2 weeks", "K+ weekly"],
        ["I011", "Metformin", "Furosemide", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I012", "Metformin", "Ciprofloxacin", "Moderate", "Increased metformin levels", "Monitor renal function", "Moderate", "1-3 days", "Creatinine monthly"],
        ["I013", "Digoxin", "Furosemide", "Moderate", "Hypokalemia increases toxicity", "Monitor K+", "Strong", "1-7 days", "K+ weekly"],
        ["I014", "Digoxin", "Amlodipine", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "3-5 days", "Digoxin level"],
        ["I015", "Amlodipine", "Simvastatin", "Moderate", "Increased statin toxicity", "Limit simvastatin dose", "Strong", "1-2 weeks", "LFTs quarterly"],
        ["I016", "Amlodipine", "Metoprolol", "Mild", "Bradycardia risk", "Monitor HR", "Moderate", "Immediate", "HR weekly"],
        ["I017", "Aspirin", "Clopidogrel", "Severe", "Bleeding risk", "Use only when necessary", "Strong", "Immediate", "CBC monthly"],
        ["I018", "Aspirin", "Omeprazole", "Moderate", "Reduced antiplatelet effect", "Use pantoprazole", "Moderate", "3-5 days", "GI symptoms"],
        ["I019", "Omeprazole", "Clopidogrel", "Moderate", "Reduced clopidogrel effect", "Use pantoprazole", "Strong", "3-5 days", "CBC if symptoms"],
        ["I020", "Omeprazole", "Digoxin", "Moderate", "Increased digoxin levels", "Monitor digoxin levels", "Moderate", "5-7 days", "Digoxin level"],
        ["I021", "Dapagliflozin", "Furosemide", "Moderate", "Dehydration risk", "Monitor volume status", "Moderate", "Immediate", "BP weekly"],
        ["I022", "Dapagliflozin", "Insulin", "Moderate", "Hypoglycemia risk", "Reduce insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I023", "Dapagliflozin", "Metformin", "Moderate", "Lactic acidosis risk", "Monitor renal function", "Moderate", "1-4 weeks", "Creatinine monthly"],
        ["I024", "Insulin", "Metoprolol", "Moderate", "Hypoglycemia symptoms masked", "Monitor glucose closely", "Moderate", "Immediate", "Glucose daily"],
        ["I025", "Insulin", "Metformin", "Moderate", "Hypoglycemia risk", "Monitor glucose", "Moderate", "Immediate", "Glucose daily"],
        ["I026", "Insulin", "Prednisolone", "Severe", "Hyperglycemia", "Increase insulin dose", "Strong", "Immediate", "Glucose daily"],
        ["I027", "Spironolactone", "Losartan", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"],
        ["I028", "Ramipril", "Spironolactone", "Severe", "Hyperkalemia risk", "Monitor K+ weekly", "Strong", "1-2 weeks", "K+ weekly"],
        ["I029", "Warfarin", "Clopidogrel", "Severe", "Bleeding risk", "Avoid if possible", "Strong", "Immediate", "INR weekly"],
        ["I030", "Warfarin", "Allopurinol", "Moderate", "Increased INR", "Reduce warfarin dose", "Moderate", "3-5 days", "INR weekly"],
    ]
    pd.DataFrame(ix, columns=["InteractionID", "DrugA", "DrugB", "Severity", "Mechanism",
        "Recommendation", "EvidenceLevel", "TimeToOnset", "MonitoringRequired"]).to_csv("data/interactions.csv", index=False)

    first = ["Rajesh", "Lakshmi", "Abdul", "Sneha", "Vikram", "Meera", "Ram", "Sunita",
             "Anand", "Priya", "Ravi", "Anita", "Suresh", "Kavita", "Mohan", "Radha",
             "Vijay", "Deepa", "Rajiv", "Sarita"]
    last = ["Kumar", "Iyer", "Rahman", "Patel", "Singh", "Nair", "Shastri", "Desai",
            "Gupta", "Joshi", "Deshmukh", "Sharma", "Reddy", "Rao", "Lal", "Krishnan",
            "Tendulkar", "Sharma", "Gupta", "Patel"]
    meds = ["Warfarin", "Metformin", "Lisinopril", "Amlodipine", "Simvastatin", "Digoxin",
            "Furosemide", "Metoprolol", "Losartan", "Aspirin", "Atorvastatin", "Clopidogrel",
            "Omeprazole", "Dapagliflozin", "Insulin Glargine", "Levothyroxine", "Gabapentin",
            "Tramadol", "Celecoxib", "Allopurinol", "Spironolactone", "Ciprofloxacin",
            "Prednisolone", "Diltiazem", "Carvedilol", "Ramipril"]
    comorbs = ["Hypertension", "Diabetes", "Atrial Fibrillation", "Heart Failure", "CKD",
               "CAD", "Hyperlipidemia", "Osteoarthritis", "GERD", "Hypothyroidism",
               "Neuropathy", "Gout", "COPD"]
    rows = []
    for i in range(20):
        age = random.randint(65, 85)
        rows.append({
            "PatientID": f"P{i+1:03d}",
            "Name": f"{random.choice(first)} {random.choice(last)}",
            "Age": age, "Gender": random.choice(["M", "F"]),
            "BMI": round(random.uniform(18, 35), 1),
            "eGFR": round(max(15, 120 - (age - 60) * 1.5 + random.uniform(-15, 15)), 0),
            "Creatinine": round(random.uniform(0.8, 2.5), 2),
            "Potassium": round(random.uniform(3.2, 5.8), 1),
            "Sodium": round(random.uniform(130, 145), 0),
            "Hemoglobin": round(random.uniform(9, 15), 1),
            "LiverFunction": random.choices(["Normal", "MildlyImpaired", "Abnormal"], weights=[0.7, 0.2, 0.1])[0],
            "Medications": "|".join(random.sample(meds, random.randint(4, 8))),
            "Comorbidities": "|".join(random.sample(comorbs, random.randint(1, 4))),
            "Allergies": "",
            "Smoking": random.choices(["No", "Former", "Current"], weights=[0.6, 0.3, 0.1])[0],
            "Alcohol": random.choices(["None", "Occasional", "Moderate", "Heavy"], weights=[0.5, 0.3, 0.15, 0.05])[0],
            "SystolicBP": random.randint(110, 180),
            "DiastolicBP": random.randint(70, 100),
        })
    pd.DataFrame(rows).to_csv("data/patients.csv", index=False)


# ============================================================
# DSS ENGINE
# ============================================================
class Severity(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


@dataclass
class Drug:
    drug_id: str; name: str; drug_class: str; metabolism: str; route: str
    max_daily_dose: float; unit: str; common_side_effects: List[str]
    contraindications: List[str]; monitoring_required: List[str]; pregnancy_risk: str


@dataclass
class Interaction:
    drug_a: str; drug_b: str; severity: Severity; mechanism: str
    recommendation: str; evidence_level: str; time_to_onset: str
    monitoring_required: List[str]


@dataclass
class Patient:
    patient_id: str; name: str; age: int; gender: str; bmi: float; egfr: float
    liver_function: str; medications: List[str]; comorbidities: List[str]
    allergies: List[str]; smoking: str; alcohol: str
    systolic_bp: int = 120; diastolic_bp: int = 80
    creatinine: float = 1.0; potassium: float = 4.0
    sodium: float = 140.0; hemoglobin: float = 13.0


class DrugInteractionAnalyzer:
    def __init__(self, drugs_path, interactions_path):
        self.drugs = self._load_drugs(drugs_path)
        self.interactions = self._load_ix(interactions_path)

    def _load_drugs(self, path):
        df = pd.read_csv(path)
        out = {}
        for _, row in df.iterrows():
            out[row["DrugName"]] = Drug(
                drug_id=row["DrugID"], name=row["DrugName"], drug_class=row["DrugClass"],
                metabolism=row["Metabolism"], route=row["Route"],
                max_daily_dose=float(row["MaxDailyDose"]), unit=row["Unit"],
                common_side_effects=row["CommonSideEffects"].split("|") if pd.notna(row["CommonSideEffects"]) else [],
                contraindications=row["Contraindications"].split("|") if pd.notna(row["Contraindications"]) else [],
                monitoring_required=row["MonitoringRequired"].split("|") if pd.notna(row["MonitoringRequired"]) else [],
                pregnancy_risk=row["PregnancyRisk"])
        return out

    def _load_ix(self, path):
        df = pd.read_csv(path)
        out = []
        for _, r in df.iterrows():
            out.append(Interaction(
                drug_a=r["DrugA"], drug_b=r["DrugB"],
                severity=Severity(r["Severity"]), mechanism=r["Mechanism"],
                recommendation=r["Recommendation"], evidence_level=r["EvidenceLevel"],
                time_to_onset=r["TimeToOnset"],
                monitoring_required=r["MonitoringRequired"].split("|") if pd.notna(r["MonitoringRequired"]) else []))
        return out

    def get_patient_modifiers(self, p):
        m = {}
        if p.age >= 85: m["Age >= 85"] = 2.0
        elif p.age >= 75: m["Age >= 75"] = 1.5
        if p.egfr < 30: m["eGFR < 30"] = 2.0
        elif p.egfr < 45: m["eGFR < 45"] = 1.5
        if p.liver_function == "Abnormal": m["Hepatic impairment"] = 1.8
        elif p.liver_function == "MildlyImpaired": m["Mild hepatic impairment"] = 1.3
        if p.bmi < 18.5: m["Low BMI"] = 1.3
        n = len(p.medications)
        if n >= 10: m["Polypharmacy (>=10)"] = 2.0
        elif n >= 8: m["Polypharmacy (>=8)"] = 1.8
        elif n >= 5: m["Polypharmacy (>=5)"] = 1.4
        if "Heart Failure" in p.comorbidities: m["Heart Failure"] = 1.5
        if p.smoking == "Current": m["Current Smoker"] = 1.2
        if p.systolic_bp >= 180 or p.diastolic_bp >= 120: m["Severe Hypertension"] = 1.6
        elif p.systolic_bp >= 140 or p.diastolic_bp >= 90: m["Uncontrolled Hypertension"] = 1.3
        if p.potassium >= 5.5: m["Severe Hyperkalemia"] = 1.7
        elif p.potassium >= 5.0: m["Moderate Hyperkalemia"] = 1.3
        elif p.potassium < 3.5: m["Hypokalemia"] = 1.4
        if p.creatinine >= 2.0: m["Elevated Creatinine"] = 1.4
        if p.hemoglobin < 10: m["Anemia"] = 1.2
        return m

    def detect_interactions(self, meds):
        found = []
        for i, a in enumerate(meds):
            for b in meds[i + 1:]:
                for ix in self.interactions:
                    if (ix.drug_a == a and ix.drug_b == b) or (ix.drug_a == b and ix.drug_b == a):
                        found.append(ix)
                        break
        return found

    def get_drug_info(self, name):
        return self.drugs.get(name)

    def analyze_patient(self, p):
        interactions = self.detect_interactions(p.medications)
        modifiers = self.get_patient_modifiers(p)
        w = {"Mild": 5, "Moderate": 15, "Severe": 30}
        raw = sum(w[i.severity.value] for i in interactions)
        adjusted = raw
        for v in modifiers.values():
            adjusted *= v
        adjusted = min(adjusted, 100)
        level = ("CRITICAL" if adjusted >= 70 else "HIGH" if adjusted >= 40
                 else "MODERATE" if adjusted >= 20 else "LOW")
        color = {"CRITICAL": "#C53030", "HIGH": "#DD6B20",
                 "MODERATE": "#D69E2E", "LOW": "#38A169"}[level]
        return {"patient": p, "interactions": interactions, "modifiers": modifiers,
                "risk_score": adjusted, "risk_level": level, "risk_color": color,
                "deprescribing_suggestions": self.suggest_deprescribing(p)}

    def suggest_deprescribing(self, p):
        out = []
        orig = self.detect_interactions(p.medications)
        w = {"Mild": 5, "Moderate": 15, "Severe": 30}
        for d in p.medications:
            c = sum(w[i.severity.value] for i in orig if i.drug_a == d or i.drug_b == d)
            if p.age > 75:
                c *= 1.5
            info = self.get_drug_info(d)
            out.append({"drug": d, "drug_class": info.drug_class if info else "Unknown",
                "risk_contribution": c,
                "priority": "HIGH" if c > 20 else "MEDIUM" if c > 10 else "LOW"})
        out.sort(key=lambda x: x["risk_contribution"], reverse=True)
        return out

    def what_if_analysis(self, p, scenario, drug_name):
        orig = self.analyze_patient(p)
        new_meds = (p.medications + [drug_name] if scenario == "add"
                    else [m for m in p.medications if m != drug_name])
        new_p = Patient(**{**p.__dict__, "medications": new_meds})
        new_a = self.analyze_patient(new_p)
        change = new_a["risk_score"] - orig["risk_score"]
        if change < 0:
            rec = f"Risk reduced by {abs(change):.1f} points. Recommend this change."
        elif change > 0:
            rec = f"Risk increased by {change:.1f} points. Exercise caution."
        else:
            rec = "No significant change in risk."
        return {"original_risk": orig["risk_score"], "new_risk": new_a["risk_score"],
                "risk_change": change, "recommendation": rec,
                "new_analysis": new_a, "new_patient": new_p}


# ============================================================
# THEME
# ============================================================
def inject_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1A202C; }
    .stApp { background: #F7FAFC; }
    #MainMenu {visibility: hidden;}
    section[data-testid="stSidebar"] {
        min-width: 320px !important; max-width: 380px !important;
        transform: none !important; visibility: visible !important;
        display: block !important; background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important; transform: none !important;
        visibility: visible !important;
    }
    .med-header {
        background: linear-gradient(135deg, #0B3C5D 0%, #1D7874 100%);
        padding: 24px 32px; border-radius: 12px; margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(11, 60, 93, 0.15);
    }
    .med-header h1 { color: #FFF !important; font-size: 26px !important; font-weight: 700 !important; margin: 0 !important; }
    .med-header p { color: #B8D4E3 !important; font-size: 13px !important; margin: 4px 0 0 0 !important; }
    .section-title {
        color: #0B3C5D; font-size: 14px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.8px;
        padding-bottom: 8px; border-bottom: 2px solid #1D7874;
        margin: 24px 0 14px 0;
    }
    .card { background: #FFF; border: 1px solid #E2E8F0; border-radius: 10px;
            padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
                   gap: 12px; margin-bottom: 20px; }
    .metric-tile { background: #FFF; border: 1px solid #E2E8F0;
                   border-left: 4px solid #1D7874; border-radius: 8px;
                   padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    .metric-tile .label { font-size: 10px; color: #718096; text-transform: uppercase;
                          letter-spacing: 0.6px; font-weight: 600; margin-bottom: 4px; }
    .metric-tile .value { font-size: 20px; color: #0B3C5D; font-weight: 700; line-height: 1.2; }
    .metric-tile .sub { font-size: 10px; color: #718096; margin-top: 2px; }
    .ix-severe { background: #FFF5F5; border-left: 4px solid #C53030; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .ix-moderate { background: #FFFAF0; border-left: 4px solid #DD6B20; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .ix-mild { background: #FFFFF0; border-left: 4px solid #D69E2E; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .ix-title { font-size: 13px; font-weight: 700; color: #1A202C; margin-bottom: 4px; }
    .ix-body { font-size: 12px; color: #4A5568; line-height: 1.5; }
    .dose-critical { background: #FFF5F5; border-left: 4px solid #C53030; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .dose-warning { background: #FFFAF0; border-left: 4px solid #DD6B20; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .dose-normal { background: #F0FFF4; border-left: 4px solid #38A169; padding: 12px 16px; margin: 8px 0; border-radius: 6px; }
    .dose-title { font-size: 13px; font-weight: 700; color: #1A202C; margin-bottom: 4px; }
    .dose-body { font-size: 12px; color: #4A5568; }
    .dose-tag { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px;
                border-radius: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-right: 8px; }
    .tag-critical { background: #FED7D7; color: #822727; }
    .tag-warning { background: #FEEBC8; color: #7B341E; }
    .tag-normal { background: #C6F6D5; color: #22543D; }
    .dep-item { background: #FFF; border: 1px solid #E2E8F0; border-radius: 8px;
                padding: 12px 16px; margin: 6px 0; display: flex;
                justify-content: space-between; align-items: center; }
    .dep-name { font-size: 13px; font-weight: 600; color: #1A202C; }
    .dep-class { font-size: 11px; color: #718096; }
    .dep-priority-HIGH { color: #C53030; font-weight: 700; font-size: 12px; }
    .dep-priority-MEDIUM { color: #DD6B20; font-weight: 700; font-size: 12px; }
    .dep-priority-LOW { color: #38A169; font-weight: 700; font-size: 12px; }
    .stButton>button { background: #0B3C5D; color: #FFF; border: none; border-radius: 6px;
                       font-weight: 600; font-size: 13px; padding: 8px 16px; }
    .stButton>button:hover { background: #1D7874; color: #FFF; }
    .stDownloadButton>button { background: #1D7874 !important; color: #FFF !important;
                               border: none !important; border-radius: 6px !important; font-weight: 600 !important; }
    .disclaimer { background: #EDF2F7; border-left: 3px solid #718096; padding: 12px 16px;
                  border-radius: 6px; font-size: 11px; color: #4A5568; line-height: 1.5; margin-top: 24px; }
    </style>
    """, unsafe_allow_html=True)


def section(t):
    st.markdown(f'<div class="section-title">{t}</div>', unsafe_allow_html=True)


# ============================================================
# MAIN
# ============================================================
def main():
    st.set_page_config(
        page_title="RxCompanion | Clinical DSS",
        page_icon=":hospital:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_theme()

    st.markdown("""
    <div class="med-header">
        <h1>RxCompanion</h1>
        <p>Clinical Decision Support System &middot; Polypharmacy Risk Assessment &amp; Medication Safety</p>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_resource
    def load_analyzer():
        return DrugInteractionAnalyzer("data/drugs.csv", "data/interactions.csv")

    try:
        analyzer = load_analyzer()
    except FileNotFoundError:
        generate_all_data()
        st.rerun()

    if "patient" not in st.session_state:
        st.session_state.patient = None
    if "what_if_result" not in st.session_state:
        st.session_state.what_if_result = None

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("### Patient Management")
        st.markdown("---")

        # BP image upload + manual entry
        with st.expander("Blood Pressure Reading", expanded=False):
            bp_image = st.file_uploader(
                "Upload BP monitor photo (optional reference)",
                type=["jpg", "jpeg", "png"],
                key="bp_image_upload"
            )
            if bp_image is not None:
                st.image(bp_image, caption="Reference image", use_container_width=True)
                st.caption("Read the values from the image and enter them below.")

            st.markdown("**Enter BP values:**")
            bc1, bc2 = st.columns(2)
            with bc1:
                bp_sys_in = st.number_input("Systolic (mmHg)", 80, 250,
                                             st.session_state.get("scanned_sys", 120),
                                             key="bp_sys_field")
            with bc2:
                bp_dia_in = st.number_input("Diastolic (mmHg)", 50, 150,
                                             st.session_state.get("scanned_dia", 80),
                                             key="bp_dia_field")
            if st.button("Save BP", use_container_width=True, key="save_bp_btn"):
                st.session_state["scanned_sys"] = bp_sys_in
                st.session_state["scanned_dia"] = bp_dia_in
                st.success(f"BP saved: {bp_sys_in}/{bp_dia_in} mmHg")

        mode = st.radio("Mode", ["Load Sample Patient", "Create New Patient"],
                        label_visibility="collapsed")

        if mode == "Load Sample Patient":
            df = pd.read_csv("data/patients.csv")
            name = st.selectbox("Select Patient", df["Name"].tolist())
            if name and st.button("Load Patient", use_container_width=True):
                r = df[df["Name"] == name].iloc[0]
                st.session_state.patient = Patient(
                    patient_id=r["PatientID"], name=r["Name"],
                    age=int(r["Age"]), gender=r["Gender"], bmi=float(r["BMI"]),
                    egfr=float(r["eGFR"]), liver_function=r["LiverFunction"],
                    medications=r["Medications"].split("|"),
                    comorbidities=r["Comorbidities"].split("|") if pd.notna(r["Comorbidities"]) else [],
                    allergies=r["Allergies"].split("|") if pd.notna(r["Allergies"]) and r["Allergies"] else [],
                    smoking=r["Smoking"] if pd.notna(r["Smoking"]) else "No",
                    alcohol=r["Alcohol"] if pd.notna(r["Alcohol"]) else "None",
                    systolic_bp=int(r.get("SystolicBP", 120)),
                    diastolic_bp=int(r.get("DiastolicBP", 80)),
                    creatinine=float(r.get("Creatinine", 1.0)),
                    potassium=float(r.get("Potassium", 4.0)),
                    sodium=float(r.get("Sodium", 140.0)),
                    hemoglobin=float(r.get("Hemoglobin", 13.0)),
                )
                st.session_state.what_if_result = None
                st.success(f"Loaded: {name}")
        else:
            name = st.text_input("Name", "Jane Doe")
            age = st.number_input("Age", 18, 120, 72)
            gender = st.selectbox("Gender", ["M", "F"])
            bmi = st.number_input("BMI (kg/m2)", 10.0, 50.0, 22.4)
            egfr = st.number_input("eGFR (mL/min/1.73m2)", 5.0, 120.0, 45.0)
            creatinine = st.number_input("Serum Creatinine (mg/dL)", 0.1, 15.0, 1.2)
            potassium = st.number_input("Potassium K+ (mEq/L)", 2.0, 8.0, 4.2)
            sodium = st.number_input("Sodium Na+ (mEq/L)", 110.0, 160.0, 140.0)
            hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0, 12.5)

            c1, c2 = st.columns(2)
            with c1:
                sys_bp = st.number_input("Systolic BP", 80, 250,
                                          st.session_state.get("scanned_sys", 120))
            with c2:
                dia_bp = st.number_input("Diastolic BP", 50, 150,
                                          st.session_state.get("scanned_dia", 80))

            liver_fn = st.selectbox("Liver Function", ["Normal", "MildlyImpaired", "Abnormal"])
            meds = st.multiselect("Current Medications", list(analyzer.drugs.keys()))
            comorb_txt = st.text_input("Comorbidities (comma separated)", "")
            comorb = [c.strip() for c in comorb_txt.split(",") if c.strip()]
            allergy_txt = st.text_input("Allergies (comma separated)", "")
            allergy = [a.strip() for a in allergy_txt.split(",") if a.strip()]
            smoking = st.selectbox("Smoking", ["No", "Former", "Current"])
            alcohol = st.selectbox("Alcohol", ["None", "Occasional", "Moderate", "Heavy"])

            if st.button("Analyze Patient", use_container_width=True):
                st.session_state.patient = Patient(
                    patient_id="P999", name=name, age=age, gender=gender, bmi=bmi,
                    egfr=egfr, liver_function=liver_fn, medications=meds,
                    comorbidities=comorb, allergies=allergy, smoking=smoking,
                    alcohol=alcohol, systolic_bp=sys_bp, diastolic_bp=dia_bp,
                    creatinine=creatinine, potassium=potassium,
                    sodium=sodium, hemoglobin=hemoglobin,
                )
                st.session_state.what_if_result = None
                st.success(f"Analyzed: {name}")

    # ---------------- MAIN ----------------
    patient = st.session_state.patient
    if patient is None:
        st.info("Select or create a patient from the sidebar to begin.")
        return

    analysis = analyzer.analyze_patient(patient)
    dose_adjustments = get_dose_adjustments(patient.medications, patient.egfr, patient.potassium)

    what_if = st.session_state.what_if_result
    display_score = what_if["new_risk"] if what_if else analysis["risk_score"]
    display_level = what_if["new_analysis"]["risk_level"] if what_if else analysis["risk_level"]
    display_color = what_if["new_analysis"]["risk_color"] if what_if else analysis["risk_color"]

    bp_display = f"{patient.systolic_bp}/{patient.diastolic_bp}"
    bp_flag = " !" if patient.systolic_bp >= 140 or patient.diastolic_bp >= 90 else ""
    k_flag = " !" if patient.potassium >= 5.0 or patient.potassium < 3.5 else ""

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-tile" style="border-left-color:{display_color};">
            <div class="label">Risk Score</div>
            <div class="value" style="color:{display_color};">{display_score:.0f}<span style="font-size:13px;color:#718096;">/100</span></div>
            <div class="sub">{display_level}{' (simulated)' if what_if else ''}</div>
        </div>
        <div class="metric-tile"><div class="label">Interactions</div>
            <div class="value">{len(analysis['interactions'])}</div><div class="sub">Detected</div></div>
        <div class="metric-tile"><div class="label">Medications</div>
            <div class="value">{len(patient.medications)}</div><div class="sub">Active</div></div>
        <div class="metric-tile"><div class="label">eGFR</div>
            <div class="value">{patient.egfr:.0f}<span style="font-size:12px;color:#718096;"> mL/min</span></div>
            <div class="sub">Renal function</div></div>
        <div class="metric-tile"><div class="label">Potassium</div>
            <div class="value" style="color:{'#C53030' if patient.potassium >= 5.0 or patient.potassium < 3.5 else '#0B3C5D'};">{patient.potassium:.1f}<span style="font-size:12px;color:#718096;"> mEq/L</span></div>
            <div class="sub">{k_flag.strip() or 'Normal'}</div></div>
        <div class="metric-tile"><div class="label">Blood Pressure</div>
            <div class="value" style="font-size:18px;">{bp_display}<span style="font-size:11px;color:#718096;"> mmHg</span></div>
            <div class="sub">{bp_flag.strip() or 'Normal'}</div></div>
    </div>
    """, unsafe_allow_html=True)

    if what_if:
        st.markdown(f"""
        <div style="background:#FFF8E5; border-left:4px solid #D69E2E; padding:10px 16px;
                    border-radius:6px; margin-bottom:16px; font-size:13px; color:#7B341E;">
            <b>Simulation active:</b> Showing results for
            {"adding" if what_if.get("scenario") == "add" else "removing"}
            <b>{what_if['drug']}</b>.
            <span style="color:#718096;">Original score: {what_if['original_risk']:.0f}</span>
        </div>
        """, unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        section("Patient Profile")
        st.markdown(f"""
        <div class="card">
        <table style="width:100%; font-size:13px; color:#4A5568; border-collapse:collapse;">
            <tr><td style="padding:4px 0; width:40%;"><b>Name</b></td><td>{patient.name}</td></tr>
            <tr><td style="padding:4px 0;"><b>Age / Gender</b></td><td>{patient.age} y &middot; {patient.gender}</td></tr>
            <tr><td style="padding:4px 0;"><b>BMI</b></td><td>{patient.bmi:.1f} kg/m2</td></tr>
            <tr><td style="padding:4px 0;"><b>Liver Function</b></td><td>{patient.liver_function}</td></tr>
            <tr><td style="padding:4px 0;"><b>Comorbidities</b></td><td>{', '.join(patient.comorbidities) if patient.comorbidities else '-'}</td></tr>
            <tr><td style="padding:4px 0;"><b>Allergies</b></td><td>{', '.join(patient.allergies) if patient.allergies else 'None reported'}</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

        section("Laboratory Values")
        st.markdown(f"""
        <div class="card">
        <table style="width:100%; font-size:13px; color:#4A5568; border-collapse:collapse;">
            <tr><td style="padding:6px 0;"><b>Serum Creatinine</b></td><td>{patient.creatinine:.2f} mg/dL</td>
                <td style="padding:6px 0;"><b>eGFR</b></td><td>{patient.egfr:.0f} mL/min</td></tr>
            <tr><td style="padding:6px 0;"><b>Potassium (K+)</b></td>
                <td style="color:{'#C53030' if patient.potassium >= 5.0 or patient.potassium < 3.5 else '#1A202C'};">{patient.potassium:.1f} mEq/L</td>
                <td style="padding:6px 0;"><b>Sodium (Na+)</b></td><td>{patient.sodium:.0f} mEq/L</td></tr>
            <tr><td style="padding:6px 0;"><b>Hemoglobin</b></td><td>{patient.hemoglobin:.1f} g/dL</td>
                <td style="padding:6px 0;"><b>Blood Pressure</b></td><td>{patient.systolic_bp}/{patient.diastolic_bp} mmHg</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

        section("Dose Adjustment Recommendations")
        if dose_adjustments:
            for adj in dose_adjustments:
                cls = {"critical": "dose-critical", "warning": "dose-warning", "normal": "dose-normal"}[adj["level"]]
                tag = {"critical": "tag-critical", "warning": "tag-warning", "normal": "tag-normal"}[adj["level"]]
                st.markdown(f"""
                <div class="{cls}">
                    <div class="dose-title"><span class="dose-tag {tag}">{adj['level']}</span>
                        {adj['drug']} &middot; <span style="font-weight:400;color:#718096;">{adj['parameter']}: {adj['value']}</span></div>
                    <div class="dose-body">{adj['recommendation']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="color:#718096; font-size:13px;">No dose adjustments required.</div>', unsafe_allow_html=True)

        section("Detected Drug Interactions")
        if analysis["interactions"]:
            for ix in analysis["interactions"]:
                cls = {"Severe": "ix-severe", "Moderate": "ix-moderate", "Mild": "ix-mild"}[ix.severity.value]
                st.markdown(f"""
                <div class="{cls}">
                    <div class="ix-title">{ix.drug_a} + {ix.drug_b} &middot; {ix.severity.value}</div>
                    <div class="ix-body"><b>Mechanism:</b> {ix.mechanism}<br>
                        <b>Recommendation:</b> {ix.recommendation}<br>
                        <b>Monitoring:</b> {', '.join(ix.monitoring_required)}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="color:#38A169; font-size:13px;">No interactions detected. Regimen appears safe.</div>', unsafe_allow_html=True)

        section("Deprescribing Suggestions")
        for s in analysis["deprescribing_suggestions"][:6]:
            st.markdown(f"""
            <div class="dep-item">
                <div><div class="dep-name">{s['drug']}</div>
                <div class="dep-class">{s['drug_class']} &middot; Risk: {s['risk_contribution']:.1f} pts</div></div>
                <div class="dep-priority-{s['priority']}">{s['priority']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        section("Risk Assessment")

        if what_if:
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="gauge+number", value=what_if["original_risk"],
                title={"text": "Before", "font": {"size": 12, "color": "#718096"}},
                domain={"x": [0, 0.45], "y": [0, 1]},
                gauge={"axis": {"range": [0, 100], "tickfont": {"size": 8}},
                       "bar": {"color": "#718096", "thickness": 0.3},
                       "steps": [{"range": [0, 20], "color": "#C6F6D5"},
                                 {"range": [20, 40], "color": "#FEFCBF"},
                                 {"range": [40, 70], "color": "#FEEBC8"},
                                 {"range": [70, 100], "color": "#FED7D7"}]}))
            fig.add_trace(go.Indicator(
                mode="gauge+number", value=what_if["new_risk"],
                title={"text": "After", "font": {"size": 12, "color": "#1D7874"}},
                domain={"x": [0.55, 1], "y": [0, 1]},
                gauge={"axis": {"range": [0, 100], "tickfont": {"size": 8}},
                       "bar": {"color": what_if["new_analysis"]["risk_color"], "thickness": 0.3},
                       "steps": [{"range": [0, 20], "color": "#C6F6D5"},
                                 {"range": [20, 40], "color": "#FEFCBF"},
                                 {"range": [40, 70], "color": "#FEEBC8"},
                                 {"range": [70, 100], "color": "#FED7D7"}]}))
            fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter"})
            st.plotly_chart(fig, use_container_width=True)

            delta = what_if["risk_change"]
            arrow = "v" if delta < 0 else "^" if delta > 0 else "="
            dcolor = "#38A169" if delta < 0 else "#C53030" if delta > 0 else "#718096"
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:11px; color:#718096; text-transform:uppercase; font-weight:600;">Change</div>
                <div style="font-size:24px; font-weight:700; color:{dcolor}; margin-top:4px;">{arrow} {abs(delta):.0f}</div>
                <div style="font-size:12px; color:#4A5568; margin-top:6px;">{what_if['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Apply Change", use_container_width=True):
                    st.session_state.patient = what_if["new_patient"]
                    st.session_state.what_if_result = None
                    st.rerun()
            with c2:
                if st.button("Discard", use_container_width=True):
                    st.session_state.what_if_result = None
                    st.rerun()
        else:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=analysis["risk_score"],
                number={"font": {"size": 34, "color": analysis["risk_color"], "family": "Inter"}},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={"axis": {"range": [None, 100], "tickfont": {"size": 10, "color": "#718096"}},
                       "bar": {"color": analysis["risk_color"], "thickness": 0.28},
                       "bgcolor": "#F7FAFC", "borderwidth": 0,
                       "steps": [{"range": [0, 20], "color": "#C6F6D5"},
                                 {"range": [20, 40], "color": "#FEFCBF"},
                                 {"range": [40, 70], "color": "#FEEBC8"},
                                 {"range": [70, 100], "color": "#FED7D7"}],
                       "threshold": {"line": {"color": analysis["risk_color"], "width": 3},
                                     "thickness": 0.75, "value": analysis["risk_score"]}}))
            fig.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter"})
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:11px; color:#718096; text-transform:uppercase; font-weight:600;">Risk Level</div>
                <div style="font-size:22px; font-weight:700; color:{analysis['risk_color']}; margin-top:4px;">{analysis['risk_level']}</div>
            </div>
            """, unsafe_allow_html=True)

        section("Risk Modifiers")
        if analysis["modifiers"]:
            for k, v in analysis["modifiers"].items():
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:6px 0;
                            border-bottom:1px solid #EDF2F7; font-size:12px;">
                    <span style="color:#4A5568;">{k}</span>
                    <span style="color:#C53030; font-weight:600;">x{v}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#718096; font-size:12px; padding:6px 0;">No modifiers applied.</div>', unsafe_allow_html=True)

        section("What-If Analysis")
        scenario = st.selectbox("Scenario", ["Add Medication", "Remove Medication"], key="wf")
        if scenario == "Add Medication":
            avail = [d for d in analyzer.drugs.keys() if d not in patient.medications]
            drug = st.selectbox("Drug to add", avail, key="wf_drug") if avail else None
        else:
            drug = st.selectbox("Drug to remove", patient.medications, key="wf_drug") if patient.medications else None

        if drug and st.button("Run Simulation", use_container_width=True):
            sim = analyzer.what_if_analysis(
                patient, "add" if scenario == "Add Medication" else "remove", drug)
            sim["drug"] = drug
            sim["scenario"] = "add" if scenario == "Add Medication" else "remove"
            st.session_state.what_if_result = sim
            st.rerun()

        section("Export")
        pdf_bytes = generate_pdf_report(patient, analysis, dose_adjustments)
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"RxCompanion_{patient.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf", use_container_width=True)

    st.markdown("""
    <div class="disclaimer">
        <b>Clinical Disclaimer:</b> RxCompanion is a Decision Support System intended for
        informational purposes only. It does not replace professional medical judgment.
        All recommendations must be independently verified by a licensed healthcare professional.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    if not os.path.exists("data/drugs.csv"):
        generate_all_data()
    main()
