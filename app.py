import os
import pandas as pd
import pdfplumber
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Census Account Lookup", page_icon="🔍", layout="centered"
)

# Minimalist custom styling
st.markdown(
    """
    <style>
    .main { max-width: 700px; padding-top: 1.5rem; }
    .stTextInput > div > div > input { font-size: 1.1rem; padding: 10px; }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Extracting and processing PDF data...")
def load_and_parse_pdf(pdf_source):
    all_rows = []
    headers = None

    with pdfplumber.open(pdf_source) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Clean line breaks and whitespace within cells
                    cleaned_row = [
                        str(cell).replace("\n", " ").strip() if cell else ""
                        for cell in row
                    ]

                    # Identify the table header row
                    if headers is None and "Mobile Number" in cleaned_row:
                        headers = cleaned_row
                        continue

                    # Skip repeated headers on subsequent pages
                    if "Mobile Number" in cleaned_row or "Role" in cleaned_row:
                        continue

                    # Append rows containing valid data
                    if any(cleaned_row):
                        all_rows.append(cleaned_row)

    if not all_rows or headers is None:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows, columns=headers)

    # Clean up column names
    df.columns = df.columns.str.strip()

    # Forward-fill 'Circle No' across rows where cells were merged or blank
    if "Circle No" in df.columns:
        df["Circle No"] = df["Circle No"].replace("", pd.NA).ffill()

    # Standardize mobile numbers to exactly 10 digits for accurate matching
    if "Mobile Number" in df.columns:
        df["Clean_Mobile"] = (
            df["Mobile Number"].str.replace(r"\D", "", regex=True).str[-10:]
        )

    return df


# Header
st.title("🔍 Account Details Lookup")
st.caption(
    "Enter a 10-digit phone number to check census bank account details."
)

# 1. Load PDF Data (Checks for local repository file first, then fallback uploader)
pdf_filename = "Census Bank Details Final.pdf"
df = pd.DataFrame()

if os.path.exists(pdf_filename):
    df = load_and_parse_pdf(pdf_filename)
else:
    uploaded_file = st.file_uploader(
        "Upload 'Census Bank Details Final.pdf'",
        type=["pdf"],
        help="Upload the official census bank details PDF document.",
    )
    if uploaded_file is not None:
        df = load_and_parse_pdf(uploaded_file)

# 2. Search Interface
if not df.empty:
    phone_input = st.text_input(
        "Mobile Number",
        placeholder="e.g., 9845926078",
        max_chars=15,
        help="Type the mobile number to search",
    )

    search_term = (
        "".join(filter(str.isdigit, phone_input))[-10:] if phone_input else ""
    )

    if phone_input:
        if len(search_term) < 10:
            st.warning("Please enter a valid 10-digit mobile number.")
        else:
            results = df[df["Clean_Mobile"] == search_term]

            if not results.empty:
                st.success(f"Found {len(results)} matching record(s).")
                for _, row in results.iterrows():
                    st.markdown(
                        f"""
                    ---
                    ### 👤 {row.get('Name', 'N/A')}
                    **Role:** {row.get('Role', 'N/A')} | **Circle:** {row.get('Circle No', 'N/A')}
                    
                    * **Account Number:** `{row.get('Account No', 'N/A')}`
                    * **IFSC Code:** `{row.get('IFSC Code', 'N/A')}`
                    * **Bank Name:** {row.get('Bank Name', 'N/A')}
                    * **Branch Name:** {row.get('Branch Name', 'N/A')}
                    * **Office / School Address:** {row.get('Supervior/Enumerator School/Office Address', 'N/A')}
                    """
                    )
            else:
                st.error("No account record found for this mobile number.")
else:
    st.info("Waiting for PDF data. Please ensure the PDF file is available.")
  
