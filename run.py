"""
RxCompanion - Medication Safety Decision Support System
Run this file to start the application
"""

import os
import subprocess
import sys


def check_data_files():
    """Check if all required data files exist"""
    required_files = [
        'data/drugs.csv',
        'data/interactions.csv',
        'data/patients.csv',
        'data/risk_modifiers.csv'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(" Missing data files. Generating data...")
        subprocess.run([sys.executable, 'generate_data.py'])
    else:
        print(" All data files found.")


def main():
    print("=" * 60)
    print(" RxCompanion - Medication Safety DSS")
    print("=" * 60)

    check_data_files()

    print("\n Starting Streamlit application...")
    print(" Opening at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the application")
    print("=" * 60)

    subprocess.run(['streamlit', 'run', 'app.py'])


if __name__ == "__main__":
    main()