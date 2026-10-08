"""Generate synthetic, general-education healthcare PDFs for the RAG knowledge base.

Run from the project root:  python scripts/generate_documents.py

These are short educational summaries written for a demo. They are NOT medical
guidance and are not copied from any source. Replace or extend them with
reputable public guideline PDFs (e.g. WHO, CDC, NIH) if you want a larger corpus.
"""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent.parent / "data" / "documents"

# filename -> (title, [(heading, text), ...])
DOCS = {
    "diabetes_guidelines.pdf": ("Type 2 Diabetes: General Information", [
        ("What is Type 2 diabetes?",
         "Type 2 diabetes is a long-term condition in which the body does not use insulin "
         "well, so sugar (glucose) builds up in the blood. It is the most common form of "
         "diabetes in adults. It often develops gradually over years."),
        ("Common symptoms",
         "Common symptoms of Type 2 diabetes include increased thirst, frequent urination, "
         "increased hunger, unexplained weight loss, tiredness, blurred vision, and slow "
         "healing of cuts and sores. Some people have no symptoms for a long time, which is "
         "why screening matters."),
        ("Risk factors",
         "Risk factors include being overweight, low physical activity, family history of "
         "diabetes, older age, a history of high blood pressure, and a history of "
         "gestational diabetes. Risk can often be reduced through lifestyle changes."),
        ("How diabetes is detected",
         "Healthcare professionals use blood tests. A fasting glucose of 126 mg/dL or higher, "
         "or an HbA1c of 6.5 percent or higher, is generally in the diabetes range. A fasting "
         "glucose of 100 to 125 mg/dL, or an HbA1c of 5.7 to 6.4 percent, is generally in the "
         "prediabetes range. Only a qualified professional can interpret results for an "
         "individual."),
        ("Managing diabetes",
         "General management includes a balanced eating pattern, regular physical activity, "
         "maintaining a healthy weight, regular blood sugar monitoring as advised, and "
         "attending routine check-ups for eyes, feet, kidneys and heart health. Medication "
         "decisions must be made with a healthcare professional."),
        ("Possible complications",
         "Over time, poorly controlled blood sugar can damage blood vessels and nerves. "
         "Possible complications include heart disease, stroke, kidney disease, eye damage, "
         "and nerve damage in the feet. Good control and regular check-ups lower these risks."),
    ]),
    "hypertension_guidelines.pdf": ("Hypertension (High Blood Pressure): General Information", [
        ("What is hypertension?",
         "Hypertension means blood pressure that stays higher than the healthy range. "
         "Blood pressure is written as two numbers, systolic over diastolic, for example "
         "120/80 mmHg. Hypertension usually has no symptoms, so it is sometimes called a "
         "silent condition."),
        ("Blood pressure categories",
         "In general, normal blood pressure is below 120/80 mmHg. Elevated is a systolic "
         "number of 120 to 129 with a diastolic number below 80. Stage 1 hypertension is "
         "130 to 139 systolic or 80 to 89 diastolic. Stage 2 hypertension is 140/90 or "
         "higher. A diagnosis requires repeated readings and professional assessment."),
        ("Risk factors",
         "Common risk factors for hypertension include older age, family history, excess "
         "body weight, low physical activity, a diet high in salt, heavy alcohol use, "
         "tobacco use, ongoing stress, and some other health conditions."),
        ("Lifestyle measures",
         "Lifestyle measures that help lower blood pressure include eating more fruits, "
         "vegetables and whole grains, reducing sodium (salt) intake, staying physically "
         "active, keeping a healthy weight, limiting alcohol, avoiding tobacco, and managing "
         "stress and sleep."),
        ("Why it matters",
         "Untreated high blood pressure increases the risk of heart attack, stroke, heart "
         "failure, kidney disease and vision problems. Regular blood pressure checks allow "
         "early detection and follow-up with a healthcare professional."),
        ("Symptoms needing urgent care",
         "Very high blood pressure together with severe headache, chest pain, shortness of "
         "breath, confusion, vision changes or weakness on one side of the body can be an "
         "emergency. Anyone with these symptoms should seek emergency care immediately."),
    ]),
    "heart_health.pdf": ("Heart Health: General Information", [
        ("Keeping the heart healthy",
         "Heart disease is a leading cause of death worldwide. Many risk factors can be "
         "improved: high blood pressure, high cholesterol, diabetes, smoking, excess weight, "
         "physical inactivity and an unhealthy diet."),
        ("Physical activity",
         "Adults are generally advised to aim for at least 150 minutes of moderate-intensity "
         "aerobic activity per week, such as brisk walking or cycling, plus muscle-"
         "strengthening activity on two or more days. People with existing conditions should "
         "check with a healthcare professional before starting a new routine."),
        ("Heart-healthy eating",
         "A heart-healthy eating pattern emphasises vegetables, fruits, whole grains, legumes, "
         "nuts, fish and unsaturated oils, while limiting processed foods, added sugars, "
         "saturated fat and salt."),
        ("Warning signs of a heart attack",
         "Warning signs can include chest pain or pressure, pain spreading to the arm, jaw, "
         "neck or back, shortness of breath, cold sweat, nausea and light-headedness. "
         "Symptoms can differ between people. These signs need emergency medical help "
         "right away; do not wait to see if they pass."),
    ]),
    "nutrition_guidelines.pdf": ("Nutrition Guidelines: General Information", [
        ("Balanced eating",
         "A balanced diet includes a variety of vegetables, fruits, whole grains, protein "
         "foods and healthy fats. Variety helps provide the vitamins, minerals and fibre "
         "the body needs."),
        ("Salt and sugar",
         "Adults are generally advised to keep sodium below about 2,300 mg per day, which is "
         "roughly one teaspoon of table salt. Added sugars should be limited, especially in "
         "sugary drinks, sweets and highly processed snacks."),
        ("Body mass index (BMI)",
         "BMI is a screening measure calculated from weight and height. For adults, a BMI of "
         "18.5 to 24.9 is generally considered the healthy range, 25 to 29.9 overweight, and "
         "30 or higher obesity. BMI does not measure body fat directly and is only one factor "
         "among many in assessing health."),
        ("Hydration and alcohol",
         "Water is the best everyday drink. Alcohol, if consumed at all, should be limited, "
         "since heavy drinking raises blood pressure and increases many health risks."),
    ]),
    "medication_safety.pdf": ("Medication Safety: General Information", [
        ("Using medicines safely",
         "Always take medicines exactly as directed by a prescriber or the product label. "
         "Do not share prescription medicines, and do not stop or change a prescribed "
         "medicine without speaking to a healthcare professional."),
        ("Keeping a medicine list",
         "Keep an up-to-date list of every medicine, vitamin and supplement you take and "
         "share it with your doctor and pharmacist. Some medicines interact with each other "
         "or with certain foods and alcohol."),
        ("Side effects and allergies",
         "Read the information leaflet for possible side effects. If a severe reaction such "
         "as swelling of the face or throat, trouble breathing or a widespread rash occurs, "
         "seek emergency care immediately. Tell every provider about any known allergies."),
        ("Storage and disposal",
         "Store medicines as the label directs, away from heat and moisture and out of reach "
         "of children. Dispose of expired or unused medicines through a pharmacy take-back "
         "program where available."),
        ("Limits of this document",
         "This document gives general safety information only. It does not provide dosage "
         "instructions. Questions about whether to take a medicine, or how much, must be "
         "answered by a doctor or pharmacist who knows the person's situation."),
    ]),
    "patient_education.pdf": ("Patient Education: Preparing for Care", [
        ("Before an appointment",
         "Write down your symptoms, when they started and what makes them better or worse. "
         "Bring a list of your medicines and any questions you want to ask."),
        ("During an appointment",
         "Describe your concerns clearly, ask for explanations in plain language, and "
         "confirm the plan before leaving. Taking notes or bringing a trusted person can "
         "help you remember the details."),
        ("Preventive care",
         "Regular check-ups can detect problems early. Common preventive steps include blood "
         "pressure checks, cholesterol and blood sugar screening as advised, recommended "
         "vaccinations and age-appropriate cancer screening discussed with a doctor."),
        ("Healthy habits",
         "Regular activity, balanced eating, adequate sleep, not smoking, limited alcohol and "
         "stress management all support long-term health."),
    ]),
    "healthcare_faq.pdf": ("Healthcare FAQ", [
        ("Can this assistant diagnose me?",
         "No. This assistant provides general educational information only. It cannot "
         "diagnose conditions, interpret personal test results, or recommend personal "
         "treatment or medication. A qualified healthcare professional should be consulted "
         "for personal medical decisions."),
        ("What should I do in an emergency?",
         "If you or someone else has severe chest pain, difficulty breathing, signs of a "
         "stroke such as face drooping, arm weakness or slurred speech, severe bleeding, or "
         "loss of consciousness, call your local emergency number immediately."),
        ("How often should I check my blood pressure?",
         "Many adults are advised to have their blood pressure checked at least once a year, "
         "and more often if it has been high or if they have other risk factors. A healthcare "
         "professional can advise on the right schedule."),
        ("Where does this information come from?",
         "The documents in this knowledge base are short synthetic educational summaries "
         "created for a portfolio demonstration. They are not a substitute for professional "
         "medical guidance or official clinical guidelines."),
    ]),
}


def build(filename, title, sections):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUT / filename), pagesize=letter, title=title,
                            leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 18)]
    for i, (heading, text) in enumerate(sections):
        if i and i % 3 == 0:          # ~3 sections per page so documents span pages
            story.append(PageBreak())
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (title, sections) in DOCS.items():
        build(name, title, sections)
        print("Wrote", name)
