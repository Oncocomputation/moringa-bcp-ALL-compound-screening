# Moringa oleifera Compound Screening for BCP-ALL

## About this project

I am working on a research project exploring the potential of *Moringa oleifera* leaf compounds against molecular targets associated with B-cell precursor acute lymphoblastic leukemia (BCP-ALL).

For this project, I first collected compounds reported from *Moringa oleifera* leaves using IMPPAT, Dr. Duke's Phytochemical and Ethnobotanical Databases, and published literature.

I combined the compound lists and removed duplicate entries. I then used Python to automate the retrieval of compound information from PubChem.

## What I did using Python

The Python script in this repository:

* Reads the curated compound list
* Searches PubChem for each compound
* Retrieves the PubChem Compound ID (CID)
* Retrieves canonical SMILES
* Retrieves isomeric SMILES when available
* Records compounds that could not be identified
* Saves the results for further analysis

## Current compound list

The current list contains 70 unique compounds after removing duplicate entries.

## Workflow

Moringa oleifera leaf compounds
↓
IMPPAT + Dr. Duke + published literature
↓
Combine and remove duplicates
↓
PubChem identification
↓
CID and SMILES retrieval
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
Contains the curated list of Moringa oleifera leaf compounds used in this analysis.

**pubchem_smiles_retrieval.py**
Python script I developed to automate PubChem compound identification and SMILES retrieval.

## Important point

The PubChem result for a compound will still need to be checked when the compound has an ambiguous name, different stereochemical forms, or a complex glycoside structure.

Also, finding a compound in the literature does not automatically mean that it will be present in the same concentration or fraction in my own Moringa leaf extract. This will need to be confirmed experimentally where required.

## Next steps

I plan to use the curated compound library for further computational analysis, including ADME/toxicity assessment, target mapping using BCP-ALL-related data, molecular docking, and selection of candidates for experimental validation.

