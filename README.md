
# Moringa oleifera Compound Screening for BCP-ALL

## About this project

I am working on a research project exploring the potential of *Moringa oleifera* leaf compounds against molecular targets associated with B-cell precursor acute lymphoblastic leukemia (BCP-ALL).

For this project, I collected compounds reported from *Moringa oleifera* leaves using IMPPAT, Dr. Duke's Phytochemical and Ethnobotanical Databases, and published literature.

The compound lists were combined and duplicate entries were removed. Python was then used to automate the retrieval and organization of compound information from PubChem.

## Compound curation and PubChem identification

The initial curated compound list contained 70 unique compounds after removal of duplicate entries.

PubChem was used to retrieve compound identifiers and structural information, including:

- PubChem Compound ID (CID)
- Canonical SMILES
- Isomeric SMILES when available

Compounds with unresolved or ambiguous structures were excluded from subsequent structure-based analysis.

Following structure verification and curation, 56 compounds were retained for the ProTox-3.0 toxicity analysis.

## What I did using Python

### PubChem compound identification

The `pubchem_smiles_retrieval.py` script was developed to automate:

- Searching PubChem for each compound
- Retrieval of PubChem Compound IDs (CIDs)
- Retrieval of canonical SMILES
- Retrieval of isomeric SMILES when available
- Recording compounds that could not be identified
- Saving the results for further analysis

### ProTox-3.0 batch prediction

The `protox3_batch.py` script was developed to automate batch acute oral toxicity prediction using the ProTox-3.0 web interface.

The script:

- Reads the curated compound dataset
- Submits compound SMILES to ProTox-3.0
- Retrieves predicted LD50 values
- Retrieves predicted toxicity classes
- Extracts additional molecular properties reported by ProTox-3.0
- Records toxicity targets
- Saves individual raw prediction results
- Saves results incrementally to prevent loss of completed predictions
- Handles timeouts and browser-session errors

The ProTox-3.0 analysis was performed on the 56-compound structure-verified library.

## Workflow

*Moringa oleifera* leaf compounds  
↓  
IMPPAT + Dr. Duke + published literature  
↓  
Combine and remove duplicates  
↓  
PubChem identification and structure verification  
↓  
Curated compound library  
↓  
ADME and toxicity analysis  
↓  
BCP-ALL target mapping  
↓  
Molecular docking  
↓  
Selection of compounds and targets for experimental validation

## Files

**compound_list.txt**  
Contains the curated list of *Moringa oleifera* leaf compounds used during compound collection.

**pubchem_smiles_retrieval.py**  
Python script developed to automate PubChem compound identification and SMILES retrieval.

**protox3_batch.py**  
Python/Selenium script developed to automate batch ProTox-3.0 acute oral toxicity prediction.

**ProTox_56_compounds.csv**  
Input compound dataset containing the 56 structure-verified compounds used for ProTox analysis.

## Important points

PubChem identification results require manual verification when compounds have ambiguous names, different stereochemical forms, or complex glycoside structures.

Finding a compound in published literature does not automatically mean that it will be present at the same concentration or in the same fraction in an experimentally prepared *Moringa oleifera* leaf extract. Experimental confirmation may therefore be required.

Similarly, ProTox-3.0 predictions are computational model outputs and should not be interpreted as experimental toxicity measurements.

## Next steps

The curated compound library will be used for further computational analysis, including:

- ADME assessment
- BCP-ALL transcriptomic analysis
- Target mapping
- Molecular docking
- Prioritization of candidate compounds and targets
- Experimental validation of selected candidates
