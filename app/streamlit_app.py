import streamlit as st
import pandas as pd
from sqlalchemy import select

from database import engine, table_store
from encoder import store_table_data, read_table_data
from project_logic import normalize_with_project, denormalize_with_project
from utils import generate_hash_index, generate_diff

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(layout="wide")
st.title("Reusable Project-Aware Template Storage")

# -------------------------------------------------
# PROJECT NUMBER (MANDATORY FOR STORE)
# -------------------------------------------------
project_no = st.text_input(
    "Project Number (required for storing)",
    placeholder="e.g. W24123"
)

# -------------------------------------------------
# INPUT METHOD
# -------------------------------------------------
st.subheader("1️⃣ Input Data")

input_mode = st.radio(
    "Choose input method:",
    ["Manual Table Entry", "Upload CSV"],
    horizontal=True
)

table_rows = None

# -------------------------------------------------
# MANUAL ENTRY
# -------------------------------------------------
if input_mode == "Manual Table Entry":
    df = pd.DataFrame(
        [
            ["W011105B0J2AW24123", "SUBASSEMBLY FOR BOILER, W24123", "1.0"],
            ["25-140-1108118", "C3L BOILER MOUNTINGS", "1.0"],
        ],
        columns=["Code", "Description", "Qty"]
    )

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )
    table_rows = edited_df.astype(str).values.tolist()

# -------------------------------------------------
# CSV UPLOAD
# -------------------------------------------------
else:
    file = st.file_uploader("Upload CSV (3 columns)", type=["csv"])
    if file:
        csv_df = pd.read_csv(file)
        st.dataframe(csv_df, use_container_width=True)
        table_rows = csv_df.astype(str).values.tolist()

# -------------------------------------------------
# STORE LOGIC (HASH-BASED, DUPLICATE-SAFE)
# -------------------------------------------------
st.divider()
st.subheader("2️⃣ Analyze & Store")

if table_rows and st.button("💾 Analyze & Store Template"):

    if not project_no:
        st.error("Project Number is mandatory before storing")
        st.stop()

    # Step 1: Normalize project number → {PROJECT_NO}
    normalized_rows = normalize_with_project(table_rows, project_no)

    # Step 2: Encode normalized table
    encoded_data = store_table_data(normalized_rows)

    # Step 3: Generate deterministic hash index
    template_index = generate_hash_index(encoded_data)

    # Step 4: Check for duplicate
    with engine.connect() as conn:
        existing = conn.execute(
            select(table_store.c.encoded_data)
            .where(table_store.c.store_index == template_index)
        ).fetchone()

    if existing:
        st.warning("⚠️ Duplicate template detected (same content hash)")

        diff = generate_diff(existing[0], encoded_data)

        if diff.strip():
            st.subheader("🧾 What Changed Compared to Existing Template")
            st.code(diff)

            if st.button("✅ Save as Modified Template"):
                with engine.begin() as conn:
                    conn.execute(
                        table_store.insert().values(
                            store_index=template_index + "-MOD",
                            encoded_data=encoded_data
                        )
                    )
                st.success("Modified template saved")
        else:
            st.info("No changes detected. Save skipped.")
    else:
        with engine.begin() as conn:
            conn.execute(
                table_store.insert().values(
                    store_index=template_index,
                    encoded_data=encoded_data
                )
            )

        st.success(f"Stored Successfully | Index = {template_index}")

        st.subheader("🔐 Encoded Template Stored")
        st.code(encoded_data)

# -------------------------------------------------
# VIEW ALL DATA (RAW DB VIEW)
# -------------------------------------------------
st.divider()
st.subheader("📋 View All Stored Templates (As Stored)")

with engine.connect() as conn:
    rows = conn.execute(
        select(table_store.c.store_index, table_store.c.encoded_data)
    ).fetchall()

if rows:
    st.dataframe(
        pd.DataFrame(rows, columns=["Template Index", "Encoded Template"]),
        use_container_width=True
    )
else:
    st.info("Database is empty")

# -------------------------------------------------
# RETRIEVE & RECONSTRUCT
# -------------------------------------------------
st.divider()
st.subheader("3️⃣ Retrieve & Reconstruct")

search_index = st.text_input("Template Index")
retrieve_project_no = st.text_input(
    "Project Number for Reconstruction (optional)",
    placeholder="e.g. W25001"
)

if st.button("🔍 Retrieve"):
    with engine.connect() as conn:
        row = conn.execute(
            select(table_store.c.encoded_data)
            .where(table_store.c.store_index == search_index)
        ).fetchone()

    if not row:
        st.error("Template not found")
    else:
        # Decode template
        decoded_rows = read_table_data(row[0])

        # Reapply project number (if provided)
        final_rows = denormalize_with_project(
            decoded_rows,
            retrieve_project_no
        )

        st.subheader("📦 Encoded Template")
        st.code(row[0])

        st.subheader("📊 Reconstructed Table")
        st.dataframe(
            pd.DataFrame(final_rows, columns=["Code", "Description", "Qty"]),
            use_container_width=True
        )
