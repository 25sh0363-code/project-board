import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

COUNTRIES = ["India", "America", "Canada", "China", "Russia", "Australia", "South Korea", "France", "Germany", "Japan"]
DISEASES = ["HIV/AIDS", "Diabetes", "Tuberculosis", "COVID-19", "Colon Cancer", "Alzheimer's"]

def generate_csv_data(disease, country):
    """Generate sample data for a disease-country combination"""
    start_date = datetime(2000, 1, 1)
    dates = [start_date + timedelta(days=i*30) for i in range(300)]
    
    base_cases = {
        "HIV/AIDS": 500,
        "Diabetes": 2000,
        "Tuberculosis": 800,
        "COVID-19": 100,
        "Colon Cancer": 300,
        "Alzheimer's": 400
    }
    
    base = base_cases.get(disease, 500)
    
    if disease == "COVID-19":
        cases = []
        for i, date in enumerate(dates):
            if date.year < 2020:
                cases.append(0)
            elif date.year == 2020:
                cases.append(int(base * (i % 12) * np.random.uniform(0.8, 1.2)))
            elif date.year == 2021:
                cases.append(int(base * 15 * np.random.uniform(0.9, 1.3)))
            else:
                cases.append(int(base * 8 * np.random.uniform(0.7, 1.1)))
    else:
        cases = [int(base * (1 + 0.05 * i) * np.random.uniform(0.8, 1.2)) for i in range(len(dates))]
    
    deaths = [int(c * np.random.uniform(0.01, 0.05)) for c in cases]
    
    return pd.DataFrame({
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'cases': cases,
        'deaths': deaths
    })

def generate_history_text(disease, country):
    """Generate sample history text for a disease-country combination"""
    return f"""# {disease} in {country}

{disease} has been a significant public health concern in {country} since the early 2000s. The disease patterns have evolved considerably over the past two decades.

## Historical Overview
In the year 2000, {country} reported its initial cases of {disease}, marking the beginning of extensive monitoring and public health interventions. The government responded by establishing specialized treatment centers and launching awareness campaigns.

## Major Developments
Between 2005 and 2010, {country} experienced fluctuating case numbers due to various factors including improved diagnostic capabilities, public health initiatives, and changing demographic patterns. Healthcare infrastructure was significantly enhanced during this period.

## Recent Trends
From 2015 onwards, {country} has implemented advanced treatment protocols and prevention strategies. The integration of technology in healthcare delivery has improved disease tracking and patient outcomes. Modern medical interventions have shown promising results in managing {disease}.

## Current Status
As of 2025, {country} continues to monitor and manage {disease} cases through comprehensive healthcare programs. Ongoing research and international collaboration contribute to better understanding and treatment of this condition.

Data Source: National Health Database and WHO estimates."""

def generate_disease_info(disease):
    """Generate disease information page"""
    info = {
        "HIV/AIDS": """# HIV/AIDS - Complete Information

## What is HIV/AIDS?
HIV (Human Immunodeficiency Virus) is a virus that attacks the body's immune system. If untreated, it can lead to AIDS (Acquired Immunodeficiency Syndrome), the most severe phase of HIV infection.

## Symptoms
- Early stage: Flu-like symptoms, fever, fatigue
- Later stages: Rapid weight loss, recurring fever, extreme fatigue
- Advanced stage: Opportunistic infections, certain cancers

## Transmission
- Unprotected sexual contact
- Sharing needles or syringes
- Mother to child during pregnancy, childbirth, or breastfeeding
- Blood transfusions (now rare due to screening)

## Prevention
- Use protection during sexual activity
- Never share needles
- Pre-exposure prophylaxis (PrEP) for high-risk individuals
- Regular testing and early treatment

## Treatment
- Antiretroviral therapy (ART)
- Regular monitoring and medication adherence
- Treatment significantly extends life expectancy
- Modern treatments allow people with HIV to live normal lifespans""",

        "Diabetes": """# Diabetes - Complete Information

## What is Diabetes?
Diabetes is a chronic condition that affects how your body processes blood sugar (glucose). Type 2 diabetes is the most common form, where the body becomes resistant to insulin or doesn't produce enough.

## Symptoms
- Increased thirst and frequent urination
- Extreme hunger and unexplained weight loss
- Fatigue and blurred vision
- Slow-healing sores and frequent infections

## Transmission
- Not contagious - develops due to genetic and lifestyle factors
- Risk factors include obesity, family history, and sedentary lifestyle

## Prevention
- Maintain healthy weight
- Regular physical activity
- Balanced diet with limited processed sugars
- Regular health screenings

## Treatment
- Blood sugar monitoring
- Medications or insulin therapy
- Healthy eating plan
- Regular exercise and weight management""",

        "Tuberculosis": """# Tuberculosis - Complete Information

## What is Tuberculosis?
Tuberculosis (TB) is a bacterial infection that primarily affects the lungs but can spread to other organs. It's caused by Mycobacterium tuberculosis bacteria.

## Symptoms
- Persistent cough lasting 3+ weeks
- Coughing up blood or mucus
- Chest pain and pain with breathing
- Fever, night sweats, and weight loss

## Transmission
- Airborne spread through coughing, sneezing, or speaking
- Prolonged exposure increases risk
- Not spread through touching or sharing food

## Prevention
- BCG vaccination in high-risk areas
- Prompt treatment of active cases
- Proper ventilation in living spaces
- Wearing masks in high-risk settings

## Treatment
- 6-9 month course of antibiotics
- Combination of multiple drugs
- Directly observed therapy (DOT)
- Drug-resistant TB requires longer treatment""",

        "COVID-19": """# COVID-19 - Complete Information

## What is COVID-19?
COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus. First identified in 2019, it led to a global pandemic affecting millions worldwide.

## Symptoms
- Fever, cough, and difficulty breathing
- Loss of taste or smell
- Fatigue and body aches
- Sore throat and headache
- Severe cases: pneumonia, respiratory failure

## Transmission
- Airborne through respiratory droplets
- Close contact with infected persons
- Touching contaminated surfaces then face
- Can spread before symptoms appear

## Prevention
- Vaccination (primary and booster doses)
- Wearing masks in crowded areas
- Hand hygiene and sanitization
- Social distancing when cases are high
- Adequate ventilation

## Treatment
- Most cases: rest, fluids, symptom management
- Severe cases: hospitalization, oxygen therapy
- Antiviral medications for high-risk patients
- Continuous monitoring of oxygen levels""",

        "Colon Cancer": """# Colon Cancer - Complete Information

## What is Colon Cancer?
Colon cancer is cancer that begins in the large intestine (colon). It typically starts as noncancerous polyps that can become cancerous over time.

## Symptoms
- Changes in bowel habits
- Blood in stool
- Persistent abdominal discomfort
- Unexplained weight loss
- Weakness and fatigue

## Risk Factors
- Age over 50
- Family history of colon cancer
- Diet high in red/processed meats
- Sedentary lifestyle and obesity
- Smoking and heavy alcohol use

## Prevention
- Regular screening (colonoscopy) after age 45-50
- High-fiber diet with fruits and vegetables
- Regular physical activity
- Limit red meat and processed foods
- Avoid smoking and limit alcohol

## Treatment
- Surgery to remove cancerous tissue
- Chemotherapy and radiation therapy
- Targeted drug therapy
- Immunotherapy for certain cases
- Early detection significantly improves outcomes""",

        "Alzheimer's": """# Alzheimer's Disease - Complete Information

## What is Alzheimer's?
Alzheimer's disease is a progressive neurological disorder that causes brain cells to degenerate and die, leading to memory loss and cognitive decline.

## Symptoms
- Memory loss affecting daily life
- Difficulty planning or solving problems
- Confusion with time or place
- Trouble with words and communication
- Changes in mood and personality

## Risk Factors
- Age (most common after 65)
- Family history and genetics
- Head injuries
- Cardiovascular conditions
- Lifestyle factors

## Prevention
- Regular physical exercise
- Mental stimulation and social engagement
- Heart-healthy diet (Mediterranean diet)
- Quality sleep
- Manage cardiovascular risk factors

## Treatment
- Medications to manage symptoms
- Cognitive training and therapy
- Lifestyle modifications
- Support for caregivers
- Clinical trials for new treatments
- No cure currently, but treatments can slow progression"""
    }
    
    return info.get(disease, f"Information about {disease} coming soon.")

os.makedirs('data', exist_ok=True)
os.makedirs('content/history', exist_ok=True)
os.makedirs('content/diseases', exist_ok=True)

print("Generating CSV files...")
for country in COUNTRIES:
    for disease in DISEASES:
        disease_file = disease.lower().replace("-", "").replace("/", "_").replace(" ", "_")
        country_file = country.lower().replace(" ", "_")
        
        csv_path = f"data/{disease_file}_{country_file}.csv"
        df = generate_csv_data(disease, country)
        df.to_csv(csv_path, index=False)
        print(f"Created: {csv_path}")

print("\nGenerating history files...")
for country in COUNTRIES:
    for disease in DISEASES:
        disease_file = disease.lower().replace("-", "").replace("/", "_").replace(" ", "_")
        country_file = country.lower().replace(" ", "_")
        
        history_path = f"content/history/{disease_file}_{country_file}.txt"
        history_text = generate_history_text(disease, country)
        with open(history_path, 'w', encoding='utf-8') as f:
            f.write(history_text)
        print(f"Created: {history_path}")

print("\nGenerating disease info files...")
for disease in DISEASES:
    disease_file = disease.lower().replace("-", "").replace("/", "_").replace(" ", "_")
    
    info_path = f"content/diseases/{disease_file}_info.txt"
    info_text = generate_disease_info(disease)
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_text)
    print(f"Created: {info_path}")

print("\n✅ All sample data generated successfully!")
print(f"Total files created: {len(COUNTRIES) * len(DISEASES) * 2 + len(DISEASES)} files")
print("- 60 CSV files in data/")
print("- 60 history files in content/history/")
print("- 6 disease info files in content/diseases/")
