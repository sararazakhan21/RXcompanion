import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


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


class RiskScore:
    """Calculates and manages risk scores"""

    SEVERITY_WEIGHTS = {
        'Mild': 5,
        'Moderate': 15,
        'Severe': 30
    }

    def __init__(self, patient: Patient, interactions: List[Interaction], modifiers: Dict[str, float]):
        self.patient = patient
        self.interactions = interactions
        self.modifiers = modifiers
        self.raw_score = 0
        self.adjusted_score = 0
        self.calculate()

    def calculate(self):
        # Base score from interactions
        for interaction in self.interactions:
            self.raw_score += self.SEVERITY_WEIGHTS[interaction.severity.value]

        # Apply modifiers
        self.adjusted_score = self.raw_score
        for modifier_name, multiplier in self.modifiers.items():
            self.adjusted_score *= multiplier

        # Cap at 100
        self.adjusted_score = min(self.adjusted_score, 100)

    def get_risk_level(self) -> str:
        if self.adjusted_score >= 70:
            return "CRITICAL"
        elif self.adjusted_score >= 40:
            return "HIGH"
        elif self.adjusted_score >= 20:
            return "MODERATE"
        else:
            return "LOW"

    def get_color(self) -> str:
        levels = {
            'CRITICAL': '#FF0000',
            'HIGH': '#FF6600',
            'MODERATE': '#FFCC00',
            'LOW': '#00CC00'
        }
        return levels[self.get_risk_level()]


class DrugInteractionAnalyzer:
    """Main DSS Engine for Drug Interaction Analysis"""

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
        """Calculate all risk modifiers for a given patient"""
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

        return modifiers

    def detect_interactions(self, medication_list: List[str]) -> List[Interaction]:
        """Detect all interactions among the given medications"""
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
        """Get drug information by name"""
        return self.drugs.get(drug_name)

    def analyze_patient(self, patient: Patient) -> Dict[str, Any]:
        """Complete analysis for a patient"""
        # Detect interactions
        interactions = self.detect_interactions(patient.medications)

        # Get modifiers
        modifiers = self.get_patient_modifiers(patient)

        # Calculate risk score
        risk = RiskScore(patient, interactions, modifiers)

        # Generate deprescribing suggestions
        deprescribing = self.suggest_deprescribing(patient)

        return {
            'patient': patient,
            'interactions': interactions,
            'modifiers': modifiers,
            'risk_score': risk.adjusted_score,
            'risk_level': risk.get_risk_level(),
            'risk_color': risk.get_color(),
            'deprescribing_suggestions': deprescribing,
            'summary': self._generate_summary(patient, interactions, risk)
        }

    def suggest_deprescribing(self, patient: Patient) -> List[Dict[str, Any]]:
        """Suggest which drug to remove first based on risk contribution"""
        suggestions = []

        # Get original risk
        original_interactions = self.detect_interactions(patient.medications)
        original_modifiers = self.get_patient_modifiers(patient)
        original_risk = RiskScore(patient, original_interactions, original_modifiers)

        for drug in patient.medications:
            # Calculate risk without this drug
            temp_meds = [m for m in patient.medications if m != drug]
            temp_patient = Patient(
                patient_id=patient.patient_id,
                name=patient.name,
                age=patient.age,
                gender=patient.gender,
                bmi=patient.bmi,
                egfr=patient.egfr,
                liver_function=patient.liver_function,
                medications=temp_meds,
                comorbidities=patient.comorbidities,
                allergies=patient.allergies,
                smoking=patient.smoking,
                alcohol=patient.alcohol
            )
            temp_interactions = self.detect_interactions(temp_meds)
            temp_modifiers = self.get_patient_modifiers(temp_patient)
            temp_risk = RiskScore(temp_patient, temp_interactions, temp_modifiers)

            risk_reduction = original_risk.adjusted_score - temp_risk.adjusted_score

            drug_info = self.get_drug_info(drug)

            suggestions.append({
                'drug': drug,
                'drug_class': drug_info.drug_class if drug_info else 'Unknown',
                'risk_contribution': risk_reduction,
                'priority': 'HIGH' if risk_reduction > 20 else 'MEDIUM' if risk_reduction > 10 else 'LOW',
                'reason': self._get_deprescribing_reason(drug, original_interactions)
            })

        # Sort by risk contribution (highest first)
        suggestions.sort(key=lambda x: x['risk_contribution'], reverse=True)
        return suggestions

    def _get_deprescribing_reason(self, drug: str, interactions: List[Interaction]) -> str:
        """Generate reason for deprescribing a specific drug"""
        reasons = []
        for interaction in interactions:
            if interaction.drug_a == drug or interaction.drug_b == drug:
                reasons.append(f"{interaction.severity.value} interaction with {interaction.drug_a if interaction.drug_a != drug else interaction.drug_b}")

        if reasons:
            return f"High risk contribution due to: {', '.join(reasons[:3])}"
        return "Potential for polypharmacy reduction"

    def what_if_analysis(self, patient: Patient, scenario_type: str, drug_name: str) -> Dict[str, Any]:
        """
        Run what-if analysis for different scenarios

        scenario_type: 'add' or 'remove'
        """
        original_analysis = self.analyze_patient(patient)

        if scenario_type == 'add':
            new_meds = patient.medications + [drug_name]
        elif scenario_type == 'remove':
            new_meds = [m for m in patient.medications if m != drug_name]
        else:
            new_meds = patient.medications.copy()

        # Create new patient with modified medications
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
            alcohol=patient.alcohol
        )

        new_analysis = self.analyze_patient(new_patient)

        return {
            'scenario_type': scenario_type,
            'drug_modified': drug_name,
            'original_risk': original_analysis['risk_score'],
            'new_risk': new_analysis['risk_score'],
            'risk_change': new_analysis['risk_score'] - original_analysis['risk_score'],
            'risk_reduction': original_analysis['risk_score'] - new_analysis['risk_score'],
            'original_level': original_analysis['risk_level'],
            'new_level': new_analysis['risk_level'],
            'new_interactions': new_analysis['interactions'],
            'new_deprescribing': new_analysis['deprescribing_suggestions'],
            'recommendation': self._generate_what_if_recommendation(
                original_analysis['risk_score'],
                new_analysis['risk_score'],
                scenario_type
            )
        }

    def _generate_what_if_recommendation(self, old_risk: float, new_risk: float, scenario_type: str) -> str:
        """Generate recommendation based on what-if analysis"""
        if new_risk < old_risk:
            change = old_risk - new_risk
            if change > 20:
                return f"✅ SIGNIFICANT RISK REDUCTION: Risk decreases by {change:.1f} points. Strongly consider this change."
            elif change > 10:
                return f"✅ MODERATE RISK REDUCTION: Risk decreases by {change:.1f} points. Consider this change."
            else:
                return f"✅ MINOR RISK REDUCTION: Risk decreases by {change:.1f} points. Marginal benefit."
        else:
            change = new_risk - old_risk
            if change > 20:
                return f"⚠️ SIGNIFICANT RISK INCREASE: Risk increases by {change:.1f} points. AVOID this change."
            elif change > 10:
                return f"⚠️ MODERATE RISK INCREASE: Risk increases by {change:.1f} points. Exercise caution."
            else:
                return f"⚠️ MINOR RISK INCREASE: Risk increases by {change:.1f} points. Monitor closely."

    def _generate_summary(self, patient: Patient, interactions: List[Interaction], risk: RiskScore) -> str:
        """Generate a natural language summary"""
        severe_count = sum(1 for i in interactions if i.severity == Severity.SEVERE)
        moderate_count = sum(1 for i in interactions if i.severity == Severity.MODERATE)
        mild_count = sum(1 for i in interactions if i.severity == Severity.MILD)

        summary = f"""
        Patient: {patient.name}, {patient.age} years, {patient.gender}
        Medications: {', '.join(patient.medications)} ({len(patient.medications)} drugs)

        RISK ANALYSIS:
        • Risk Score: {risk.adjusted_score:.1f}/100 - {risk.get_risk_level()}
        • Interactions: {len(interactions)} total
          - Severe: {severe_count}
          - Moderate: {moderate_count}
          - Mild: {mild_count}

        KEY FINDINGS:
        """

        if interactions:
            sorted_interactions = sorted(interactions, key=lambda x:
                                        {'Severe': 3, 'Moderate': 2, 'Mild': 1}[x.severity.value], reverse=True)
            for i, interaction in enumerate(sorted_interactions[:3]):
                summary += f"\n    {i+1}. {interaction.drug_a} + {interaction.drug_b}: {interaction.severity.value}"
                summary += f"\n       → {interaction.mechanism}"
                summary += f"\n       → {interaction.recommendation}"

        return summary