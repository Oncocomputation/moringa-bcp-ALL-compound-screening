import os
import re
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    InvalidSessionIdException
)

# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "ProTox_56_compounds.csv"
OUTPUT_FILE = "ProTox_56_ProTox_results.csv"
RAW_FOLDER = "ProTox_56_raw_results"

URL = "https://tox.charite.de/protox3/index.php?site=compound_input"

MAX_WAIT = 300
PAUSE = 3

os.makedirs(RAW_FOLDER, exist_ok=True)


# ============================================================
# LOAD INPUT
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("Loaded input file.")
print("Columns:", list(df.columns))
print("Compounds:", len(df))


# ============================================================
# FIND COLUMNS AUTOMATICALLY
# ============================================================

def find_column(columns, possibilities):

    for p in possibilities:
        for c in columns:
            if str(c).strip().lower() == p.lower():
                return c

    for p in possibilities:
        for c in columns:
            if p.lower() in str(c).strip().lower():
                return c

    return None


name_col = find_column(
    df.columns,
    [
        "Compound",
        "Compound Name",
        "Name",
        "Chemical",
        "Chemical Name",
        "Molecule"
    ]
)

smiles_col = find_column(
    df.columns,
    [
        "SMILES",
        "Canonical SMILES",
        "Canonical_Smiles",
        "CanonicalSMILES",
        "Smiles",
        "Structure"
    ]
)

if name_col is None or smiles_col is None:

    print("\nCould not identify columns.")
    print(list(df.columns))

    raise ValueError(
        "Could not identify compound-name and SMILES columns."
    )


df = df.rename(
    columns={
        name_col: "Compound",
        smiles_col: "SMILES"
    }
)

df["Compound"] = df["Compound"].astype(str).str.strip()
df["SMILES"] = df["SMILES"].astype(str).str.strip()

print("Compound column:", name_col)
print("SMILES column:", smiles_col)


# ============================================================
# LOAD EXISTING RESULTS
# ============================================================

if os.path.exists(OUTPUT_FILE):

    results = pd.read_csv(OUTPUT_FILE)

    print(
        "\nExisting results:",
        len(results)
    )

else:

    results = pd.DataFrame()

    print("\nNo previous results found.")


# ============================================================
# START / RESTART CHROME
# ============================================================

driver = None


def start_browser():

    global driver

    # Safely close old browser
    try:
        if driver is not None:
            driver.quit()
    except Exception:
        pass

    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")

    # Helps prevent Chrome from sleeping/disconnecting
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Chrome(
        options=options
    )

    print("\n*** Chrome session started ***\n")

    return driver


start_browser()


# ============================================================
# RESULT EXTRACTION
# ============================================================

def extract_result(text):

    data = {}

    patterns = {

        "Predicted_LD50":
            r"Predicted LD50:\s*([^\n]+)",

        "Predicted_Toxicity_Class":
            r"Predicted Toxicity Class:\s*([^\n]+)",

        "Average_Similarity":
            r"Average similarity:\s*([^\n]+)",

        "Prediction_Accuracy":
            r"Prediction accuracy:\s*([^\n]+)",

        "Molweight":
            r"Molweight\s*([^\n]+)",

        "H_Bond_Acceptors":
            r"Number of hydrogen bond acceptors\s*([^\n]+)",

        "H_Bond_Donors":
            r"Number of hydrogen bond donors\s*([^\n]+)",

        "Number_of_Atoms":
            r"Number of atoms\s*([^\n]+)",

        "Number_of_Bonds":
            r"Number of bonds\s*([^\n]+)",

        "Rotatable_Bonds":
            r"Number of rotable bonds\s*([^\n]+)",

        "Molecular_Refractivity":
            r"Molecular refractivity\s*([^\n]+)",

        "TPSA":
            r"Topological Polar Surface Area\s*([^\n]+)",

        "LogP":
            r"octanol/water partition coefficient\(logP\)\s*([^\n]+)"
    }

    for key, pattern in patterns.items():

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = ""

    # ProTox's 16 toxicity targets
    known_targets = [
        "AA2AR",
        "ADRB2",
        "ANDR",
        "AOFA",
        "CRFR1",
        "DRD3",
        "ESR1",
        "ESR2",
        "GCR",
        "HRH1",
        "NR1I2",
        "OPRK",
        "OPRM",
        "PDE4D",
        "PGH1",
        "PRGR"
    ]

    found = []

    for target in known_targets:

        if re.search(
            r"\b" + re.escape(target) + r"\b",
            text
        ):
            found.append(target)

    data["Toxicity_Targets"] = "; ".join(found)

    return data


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(new_row, compound):

    global results

    if (
        len(results) > 0
        and "Compound" in results.columns
    ):

        results = results[
            results["Compound"].astype(str).str.strip()
            != compound
        ]

    results = pd.concat(
        [
            results,
            pd.DataFrame([new_row])
        ],
        ignore_index=True
    )

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )


# ============================================================
# MAIN LOOP
# ============================================================

for i, row in df.iterrows():

    compound = row["Compound"]
    smiles = row["SMILES"]

    print("\n" + "=" * 70)
    print(
        f"[{i+1}/{len(df)}] {compound}"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # SKIP ALREADY SUCCESSFUL
    # --------------------------------------------------------

    if (
        len(results) > 0
        and
        "Compound" in results.columns
        and
        "Status" in results.columns
    ):

        old = results[
            results["Compound"].astype(str).str.strip()
            == compound
        ]

        if (
            len(old) > 0
            and
            str(old.iloc[-1]["Status"]).lower()
            == "success"
        ):

            print(
                "Already successfully completed."
            )

            continue


    print("SMILES:", smiles)


    # --------------------------------------------------------
    # TRY COMPOUND
    # --------------------------------------------------------

    try:

        # ====================================================
        # OPEN PROTOX
        # ====================================================

        driver.get(URL)

        time.sleep(2)


        # ====================================================
        # ENTER SMILES
        # ====================================================

        smiles_box = WebDriverWait(
            driver,
            30
        ).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "smiles_field"
                )
            )
        )

        smiles_box.clear()
        smiles_box.send_keys(smiles)

        print("1. SMILES entered.")


        # ====================================================
        # LOAD MOLECULE
        # ====================================================

        load_button = WebDriverWait(
            driver,
            30
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@name='start' "
                    "and @value='smiles']"
                )
            )
        )

        load_button.click()

        print("2. Molecule submitted.")

        time.sleep(5)


        # ====================================================
        # START TOX PREDICTION
        # ====================================================

        prediction_button = WebDriverWait(
            driver,
            30
        ).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[contains("
                    "translate(@value,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'start tox-prediction')]"
                )
            )
        )

        prediction_button.click()

        print(
            "3. START TOX-PREDICTION clicked."
        )


        # ====================================================
        # WAIT FOR RESULTS
        # ====================================================

        start_time = time.time()

        result_text = None

        while (
            time.time() - start_time
            < MAX_WAIT
        ):

            time.sleep(5)

            try:

                text = driver.find_element(
                    By.TAG_NAME,
                    "body"
                ).text

            except (
                WebDriverException,
                InvalidSessionIdException
            ):

                print(
                    "\nChrome session disappeared."
                )

                # Restart Chrome
                start_browser()

                raise RuntimeError(
                    "Chrome session disconnected."
                )


            elapsed = int(
                time.time() - start_time
            )

            print(
                f"{elapsed}s | "
                f"{len(text)} characters",
                end="\r"
            )

            lower = text.lower()

            if (
                "predicted ld50:" in lower
                and
                "predicted toxicity class:" in lower
            ):

                result_text = text

                print()

                break


        # ====================================================
        # TIMEOUT
        # ====================================================

        if result_text is None:

            print(
                "\nTIMEOUT — moving to next compound."
            )

            safe = re.sub(
                r"[^A-Za-z0-9_-]",
                "_",
                compound
            )

            with open(
                os.path.join(
                    RAW_FOLDER,
                    f"{i+1:02d}_{safe}_TIMEOUT.txt"
                ),
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    text
                )

            save_result(
                {
                    "Compound": compound,
                    "SMILES": smiles,
                    "Status": "Timeout"
                },
                compound
            )

            continue


        # ====================================================
        # SAVE RAW RESULT
        # ====================================================

        safe = re.sub(
            r"[^A-Za-z0-9_-]",
            "_",
            compound
        )

        raw_file = os.path.join(
            RAW_FOLDER,
            f"{i+1:02d}_{safe}.txt"
        )

        with open(
            raw_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(result_text)


        # ====================================================
        # EXTRACT
        # ====================================================

        extracted = extract_result(
            result_text
        )

        new_row = {
            "Compound": compound,
            "SMILES": smiles,
            "Status": "Success",
            **extracted
        }


        # ====================================================
        # SAVE IMMEDIATELY
        # ====================================================

        save_result(
            new_row,
            compound
        )


        # ====================================================
        # SHOW RESULT
        # ====================================================

        print("\nSUCCESS!")

        print(
            "LD50:",
            extracted["Predicted_LD50"]
        )

        print(
            "Toxicity class:",
            extracted["Predicted_Toxicity_Class"]
        )

        print(
            "Similarity:",
            extracted["Average_Similarity"]
        )

        print(
            "Accuracy:",
            extracted["Prediction_Accuracy"]
        )

        print(
            "Saved:",
            OUTPUT_FILE
        )


    # ========================================================
    # CHROME / SELENIUM ERROR
    # ========================================================

    except (
        WebDriverException,
        InvalidSessionIdException,
        RuntimeError
    ) as e:

        print(
            "\nBrowser error:",
            type(e).__name__
        )

        print(
            "The browser will be restarted."
        )

        # IMPORTANT:
        # Do NOT query driver.current_url or body here.
        # The session may already be dead.

        safe = re.sub(
            r"[^A-Za-z0-9_-]",
            "_",
            compound
        )

        error_file = os.path.join(
            RAW_FOLDER,
            f"{i+1:02d}_{safe}_ERROR.txt"
        )

        with open(
            error_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"Compound: {compound}\n"
                f"SMILES: {smiles}\n\n"
                f"Error: {repr(e)}\n"
            )

        save_result(
            {
                "Compound": compound,
                "SMILES": smiles,
                "Status": "Error",
                "Error": repr(e)
            },
            compound
        )

        # Restart browser
        start_browser()

        print(
            "Browser restarted."
        )

        # Continue with next compound
        continue


    # ========================================================
    # OTHER UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        print(
            "\nUnexpected error:",
            type(e).__name__,
            str(e)
        )

        safe = re.sub(
            r"[^A-Za-z0-9_-]",
            "_",
            compound
        )

        with open(
            os.path.join(
                RAW_FOLDER,
                f"{i+1:02d}_{safe}_ERROR.txt"
            ),
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"Compound: {compound}\n"
                f"SMILES: {smiles}\n\n"
                f"Error: {repr(e)}\n"
            )

        save_result(
            {
                "Compound": compound,
                "SMILES": smiles,
                "Status": "Error",
                "Error": repr(e)
            },
            compound
        )

  
