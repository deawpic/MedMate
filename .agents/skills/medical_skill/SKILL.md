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

## 2. Standard Medical Terminologies & MCP Routing Matrix (`medical-terminologies-mcp`)

The system integrates seven international clinical coding systems (LOINC, RxNorm, ATC, MeSH, ICD-11, ICD-10/CID-10, SNOMED CT) via `medical-terminologies-mcp`:

### 2.1 🧪 LOINC (Lab Tests, Observations & Clinical Scales)
Fetches observation codes, reference units, clinical panels, and standardized assessment scales:
- **`loinc_search`**: Search by test name or keyword (e.g. `"creatinine"`, `"glucose"`, `"INR"`, `"troponin"`, `"arterial blood gas"`).
- **`loinc_details`**: Fetch specific LOINC component, property, time aspect, and system details.
- **`loinc_panels`**: Retrieve full panel compositions (e.g. Basic Metabolic Panel, Lipid Panel, ABG Panel).
- **`loinc_answers`**: Fetch discrete answer lists or scoring values (e.g. for NIHSS, Glasgow Coma Scale, APGAR).

### 2.2 💊 RxNorm (Normalized Clinical Drugs & Ingredients)
Retrieves normalized drug concepts, active ingredients, formulations, brand names, and RxCUIs:
- **`rxnorm_search`**: Search drug concepts by brand or generic name (e.g. `"Alteplase"`, `"Metformin"`, `"Warfarin"`, `"Ceftriaxone"`).
- **`rxnorm_concept`**: Look up concept details by RxCUI identifier.
- **`rxnorm_ingredients`**: Deconstruct multi-ingredient combination drugs into base components.
- **`rxnorm_classes`**: Retrieve drug classes associated with an RxCUI.
- **`rxnorm_ndc`**: National Drug Code cross-referencing.

### 2.3 🧬 ATC Classification (Anatomical Therapeutic Chemical)
Provides WHO ATC hierarchy (Levels 1–5: Anatomical, Therapeutic, Pharmacological, Chemical):
- **`atc_classify`**: Classify a drug name into its standard ATC codes and drug classes (e.g. `"Metformin"` -> `A10BA` Biguanides; `"Alteplase"` -> `B01AD` Enzymes).
- **`atc_lookup`**: Resolve ATC codes (levels 1–4) to class names and hierarchy.
- **`atc_members`**: List drugs belonging to an ATC class.

### 2.4 📚 MeSH (Biomedical Subject Headings)
Searches indexed biomedical concepts and hierarchical taxonomy:
- **`mesh_search`**: Find MeSH descriptors for clinical diseases and conditions (e.g. `"Ischemic Stroke"`, `"Atrial Fibrillation"`, `"Diabetic Ketoacidosis"`).
- **`mesh_descriptor`**: Retrieve tree numbers, scope notes, and details for a MeSH ID.
- **`mesh_tree`**: Navigate the MeSH hierarchy (parent and child terms).
- **`mesh_qualifiers`**: Retrieve standard topical qualifiers (e.g. therapy, etiology, diagnosis).

### 2.5 🌐 Cross-Terminology & Equivalent Search
- **`find_equivalent`**: Unified ranked search mapping a single clinical concept across multiple terminologies (LOINC, RxNorm, MeSH, SNOMED, ICD-11) with lexical similarity scores.
- **`map_icd10_to_icd11`**: Official WHO mapping between ICD-10 and ICD-11 classifications.
- **`map_loinc_to_snomed`**: Map laboratory observation codes to SNOMED CT clinical terms.
- **`validate_codes`**: Validate code formatting and syntax against target standard systems.

---

## 3. Global Biomedical Evidence, Drug Safety & Guidelines (`medical-mcp`)

The system connects to authoritative global repositories (PubMed, US FDA, WHO Global Health Observatory, NLM) via `medical-mcp`:

### 3.1 💊 Pharmacology, Drug Safety & Interactions Suite
- **`search-drugs`**: Search FDA-approved drug database (brand name, generic name, active ingredients, dosage forms, manufacturer, and approval status).
- **`get-drug-details`**: Retrieve in-depth labeling, black box warnings, indications, contraindications, and NDC identifiers.
- **`search-drug-nomenclature`**: Standardized drug naming and aliases lookup via NLM RxNorm.
- **`check-drug-interactions`**: Automated Drug-Drug Interaction (DDI) analysis between two medications (returns severity level, clinical risk mechanisms, and evidence-based management guidance).

### 3.2 📖 Biomedical Literature & Research Suite
- **`search-medical-literature`**: Live search of PubMed for clinical trials, randomized controlled trials (RCTs), systematic reviews, and cohort studies with PMIDs and abstracts.
- **`get-article-details`**: Fetch complete article metadata, author affiliations, abstract, and publication dates by PMID.
- **`search-google-scholar`**: Cross-reference academic citations, author profiles, and scholarly publications.
- **`search-medical-journals`**: Targeted literature search filtered by leading biomedical peer-reviewed journals (e.g. NEJM, Lancet, JAMA, Circulation, Stroke).
- **`search-medical-databases`**: Federated search across multiple international biomedical repositories.

### 3.3 📋 Clinical Guidelines & Global Health Indicators Suite
- **`search-clinical-guidelines`**: Search international clinical practice guidelines, consensus statements, and meta-analyses categorized by medical specialty and evidence level.
- **`get-health-statistics`**: Query global health indicators and epidemiological statistics from the WHO Global Health Observatory (by country code and indicator).

### 3.4 💡 Proactive Evidence-on-Demand Protocol (Tier 1 & Tier 2)
- **Explicit Request**: If the user explicitly asks for latest evidence, RCTs, PMID, or guidelines -> Call `search-medical-literature` / `search-clinical-guidelines` immediately.
- **General Clinical Inquiry / Case Discussion**: Deliver concise clinical synthesis / SOAP note first, then append a polite proactive suggestion offering to retrieve PubMed trials/systematic reviews if desired:
  > *"💡 **ทางเลือกเพิ่มเติม:** หากต้องการหลักฐานเชิงประจักษ์ฉบับเต็ม สามารถแจ้งให้ผมสืบค้นงานวิจัย RCTs / Systematic Reviews ล่าสุดจาก PubMed พร้อมระบุ PMID และระดับหลักฐาน (Level of Evidence) เพิ่มเติมได้ครับ"*
- **Tier 3 (Patient)**: Skip PubMed offers to prevent medical jargon overload.

### 3.5 🛡️ Anti-Hallucination, Citation Verification & Uncertainty Protocol
- **Strict Prohibition on Fabricated Citations**: Never hallucinate PMIDs, DOIs, study designs, author names, or sample sizes. Only cite papers returned by `medical-mcp` or `pubmed-database`.
- **Honest Absence of Evidence**: If a search query yields no relevant RCTs or guideline recommendations, explicitly disclose this (e.g. *"Currently, no published RCTs directly address this specific scenario in PubMed"*), rather than inventing consensus.
- **Clinical Data Incompleteness Gate**: When presented with partial lab data or ambiguous vital signs, refuse to make definitive diagnostic leaps; instead, explicitly state missing diagnostic components (e.g., missing anion gap inputs, missing baseline creatinine, or missing right-sided EKG leads).

---

## 4. Local Clinical Documents & RAG (`local-rag`)

- **`read_file`**, **`search_files`**, **`list_directory`**: Sandboxed access strictly within `./RAG` (e.g. `"case_study_01.txt"`, `"case_study_03.txt"`).

### 4.1 💾 User File Export Destination (`./output/`) & UTF-8 Protocol
- All generated reports, clinical cheat-sheets, exported markdown summaries, or data files requested by the user must be saved inside `./output/` (e.g. `./output/filename.md`).
- **UTF-8 Encoding Mandate**: Always enforce UTF-8 encoding (`encoding='utf-8'` / UTF-8 without BOM) for any files containing Thai characters or Thai filenames to prevent font corruption and encoding issues across all platforms.

