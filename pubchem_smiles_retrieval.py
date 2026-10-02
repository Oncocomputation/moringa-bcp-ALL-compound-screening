import requests
import pandas as pd
import time

# Read compound names from text file
with open("compound_list.txt", "r", encoding="utf-8") as f:
    compounds = [line.strip() for line in f if line.strip()]

# Remove duplicates while preserving order
compounds = list(dict.fromkeys(compounds))

print(f"Number of compounds: {len(compounds)}")


def get_pubchem(compound):

    result = {
        "Compound": compound,
        "PubChem_CID": None,
        "Canonical_SMILES": None,
        "Isomeric_SMILES": None,
        "Status": None
    }

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        "compound/name/"
        + requests.utils.quote(compound, safe="")
        + "/property/CanonicalSMILES,IsomericSMILES/JSON"
    )

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:

            data = response.json()
            prop = data["PropertyTable"]["Properties"][0]

            result["PubChem_CID"] = prop.get("CID")
            result["Canonical_SMILES"] = prop.get("ConnectivitySMILES")
            result["Isomeric_SMILES"] = prop.get("SMILES")
            result["Status"] = "Found"

        elif response.status_code == 404:
            result["Status"] = "Not found"

        else:
            result["Status"] = f"HTTP {response.status_code}"

    except Exception as e:
        result["Status"] = f"Error: {e}"

    return result


# Retrieve PubChem information
results = []

for i, compound in enumerate(compounds, 1):

    print(f"{i}/{len(compounds)} -> {compound}")

    results.append(get_pubchem(compound))

    time.sleep(0.2)


# Create results table
results_df = pd.DataFrame(results)

print("\nStatus summary:")
print(results_df["Status"].value_counts())

# Save results
results_df.to_csv(
    "Moringa_Compounds_PubChem_SMILES.csv",
    index=False,
    encoding="utf-8"
)

print("\nResults saved as:")
print("Moringa_Compounds_PubChem_SMILES.csv")
