---
name: medical_skill
description: >-
  Medical & Local Knowledge Capabilities for Thai Medical Agent. Provides instructions,
  clinical runbooks (Acid-Base, Anion Gap, AKI KDIGO staging, DKA criteria), and tool routing
  for searching medical literature, clinical guidelines, standard terminologies (ICD-11, LOINC,
  RxNorm, ATC, MeSH), drug interactions, and local RAG knowledge documents.
---

# Medical & Clinical Knowledge Capabilities (MedMate)

This skill provides clinical calculation runbooks, terminology mapping protocols, and tool routing for the **ThaiMedicalAgent**.

---

## 1. Clinical Interpretation & Calculation Runbooks

### 1.1 Arterial Blood Gas (ABG) & Acid-Base Analysis
When interpreting blood gas data:
1. **Assess pH**:
   - Normal: 7.35 - 7.45
   - Acidemia: pH < 7.35
   - Alkalemia: pH > 7.45
2. **Determine Primary Disturbance**:
   - Metabolic Acidosis: Low pH + Low HCO3- (< 22 mEq/L)
   - Respiratory Acidosis: Low pH + High pCO2 (> 45 mmHg)
   - Metabolic Alkalosis: High pH + High HCO3- (> 26 mEq/L)
   - Respiratory Alkalosis: High pH + Low pCO2 (< 35 mmHg)
3. **Calculate Serum Anion Gap (AG)**:
   6639\text{Anion Gap} = \text{Na}^+ - (\text{Cl}^- + \text{HCO}_3^-)6639
   - Normal Range: 0 \pm 2\text{ mEq/L}$ (8 - 12)
   - **High Anion Gap Metabolic Acidosis (HAGMA)** (AG > 12): Remember *GOLD MARK* (Glycols, Oxoproline, L-lactate, D-lactate, Methanol, Aspirin, Renal failure / Uremia, Ketoacidosis - DKA/AKA/Starvation).
   - **Delta Ratio (Delta-Delta)**: $\Delta \text{AG} / \Delta \text{HCO}_3^- = (\text{AG} - 12) / (24 - \text{HCO}_3^-)$
     - $< 0.8$: Mixed HAGMA + Normal AG Metabolic Acidosis
     - bash.8 - 2.0$: Pure HAGMA (e.g. typical DKA)
     - $> 2.0$: Mixed HAGMA + Pre-existing Metabolic Alkalosis

---

### 1.2 Diabetic Ketoacidosis (DKA) Staging & Diagnostic Criteria
- **Blood Glucose**: $> 250\text{ mg/dL}$
- **Arterial pH**:
  - Mild: .25 - 7.30$
  - Moderate: .00 - 7.24$
  - Severe: $< 7.00$
- **Serum Bicarbonate**:
  - Mild: 5 - 18\text{ mEq/L}$
  - Moderate: 0 - <15\text{ mEq/L}$
  - Severe: $< 10\text{ mEq/L}$
- **Urine/Serum Ketones**: Positive (3+ to 4+ or beta-hydroxybutyrate $> 3.0\text{ mmol/L}$)
- **Anion Gap**: $> 12\text{ mEq/L}$ (HAGMA)
- **Mental Status**: Alert (Mild) -> Alert/Drowsy (Moderate) -> Stupor/Coma (Severe)

---

### 1.3 Acute Kidney Injury (AKI) KDIGO Staging
- **Stage 1**: Serum Creatinine .5 - 1.9\times$ baseline OR increase $\ge 0.3\text{ mg/dL}$ within 48 hours; Urine output $< 0.5\text{ mL/kg/h}$ for 6-12 hours.
- **Stage 2**: Serum Creatinine .0 - 2.9\times$ baseline; Urine output $< 0.5\text{ mL/kg/h}$ for $\ge 12$ hours.
- **Stage 3**: Serum Creatinine .0\times$ baseline OR increase $\ge 4.0\text{ mg/dL}$ OR initiation of RRT; Urine output $< 0.3\text{ mL/kg/h}$ for $\ge 24$ hours OR Anuria for $\ge 12$ hours.
- **Prerenal vs Intrinsic AKI (BUN/Cr Ratio)**:
  - $\text{BUN/Cr} > 20:1$ strongly indicates **Prerenal Azotemia / Dehydration** (as seen when urea reabsorption increases alongside proximal sodium reabsorption).

---

## 2. MCP Tool Routing Matrix

### 2.1 search_pubmed / search_literature
Queries global biomedical literature and clinical trials.
- **tool**: `search-medical-literature`, `get-article-details`, `search-google-scholar` (server: `medical-mcp`)
- **fallback skill**: `pubmed-database` (Direct E-utilities REST API)

### 2.2 decode_icd11 / icd_search
Translates clinical concepts, diagnostic queries, and disease classifications.
- **tool**: `icd11_search`, `icd11_lookup`, `map_icd10_to_icd11` (server: `medical-terminologies-mcp`)
- **tool**: `search-clinical-guidelines`, `search-medical-databases` (server: `medical-mcp`)

### 2.3 decode_loinc_range / loinc_search
Fetches standard clinical laboratory observation data, reference metadata, and tests.
- **tool**: `loinc_search`, `loinc_details`, `loinc_panels` (server: `medical-terminologies-mcp`)
- **tool**: `get-health-statistics` (server: `medical-mcp`)

### 2.4 check_drugs / drug_terminologies
Searches drugs, inspects dosages, indications, checks drug interactions, and standard classifications.
- **tool**: `search-drugs`, `get-drug-details`, `check-drug-interactions` (server: `medical-mcp`)
- **tool**: `rxnorm_search`, `rxnorm_concept`, `atc_classify`, `atc_lookup` (server: `medical-terminologies-mcp`)

### 2.5 mesh_search / cross_terminology
Searches biomedical subject headings and finds equivalent terms across coding systems.
- **tool**: `mesh_search`, `mesh_descriptor`, `find_equivalent` (server: `medical-terminologies-mcp`)

### 2.6 search_local_rag
Searches and reads custom user text files, lecture notes, and spreadsheets stored inside the local `./RAG` folder.
- **tool**: `read_file`, `search_files`, `list_directory` (server: `local-rag`)
- **arguments**:
  - `path`: The target filename inside the RAG directory (e.g., "case_study_01.txt", "lecture.txt", "cases.csv").
