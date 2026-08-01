import os
import pandas as pd
import pdfplumber
import streamlit as st

# Set page configuration for mobile and desktop viewport
st.set_page_config(
    page_title="Census 2027 Malavalli Rural - Account Lookup",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Mobile-Friendly Responsive CSS with FLUID AUTO-SPACING, WHITE BACKGROUND & RED BUTTONS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* STRICTLY HIDE STREAMLIT DEFAULT HEADER, FOOTER, MENU & DEPLOY BUTTON */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}

    /* STRICTLY ENFORCE PURE WHITE BACKGROUND GLOBALLY */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* Enforce Dark Text for Streamlit Widgets/Labels */
    label[data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 1.05rem !important;
    }

    /* Enforce RED Background and WHITE Text for ALL Buttons (Touch-Friendly Height) */
    div.stButton > button, div.stButton > button:hover, div.stButton > button:focus, div.stButton > button:active {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        border: 1px solid #B91C1C !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        min-height: 44px !important;
    }

    /* Main Container with Auto Fluid Padding */
    .main {
        max-width: 720px;
        padding-top: 0.5rem;
        padding-left: clamp(0.5rem, 3vw, 1.5rem) !important;
        padding-right: clamp(0.5rem, 3vw, 1.5rem) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit default top spacing & enforce ample bottom spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        background-color: #FFFFFF !important;
    }

    /* Responsive Header Typography */
    .header-h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
        line-height: 1.25;
    }
    .header-h2 {
        font-size: 1.05rem;
        font-weight: 500;
        color: #475569;
        margin-bottom: 1.8rem;
        line-height: 1.45;
    }

    /* Mobile-Friendly Result Card with Fluid Auto-Padding */
    .result-card {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0;
        border-radius: 14px;
        padding: clamp(16px, 4vw, 24px) clamp(14px, 4vw, 20px);
        margin-top: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        position: relative;
        overflow: hidden;
    }
    .result-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: #DC2626;
    }
    
    /* SIDE-BY-SIDE INLINE LAYOUT WITH FLUID AUTO-SPACING (Label : Value) */
    .detail-row {
        display: flex;
        flex-direction: row;
        align-items: baseline;
        padding: clamp(8px, 2vw, 11px) 0;
        border-bottom: 1px solid #F1F5F9;
        font-size: 1.25rem;
        line-height: 1.45;
        gap: 8px; /* Automatic fluid spacing between label and value */
    }
    .detail-row:last-of-type {
        border-bottom: none;
    }
    .detail-label {
        font-weight: 600;
        color: #4B5563;
        flex: 0 0 clamp(105px, 34vw, 160px); /* Dynamically scales label width across any mobile viewport */
        font-size: 1.15rem;
    }
    .detail-value {
        font-weight: 500;
        color: #0F172A;
        flex: 1 1 auto;
        word-break: break-word;
    }

    /* Targeted Highlighting for Account No, IFSC Code, Bank Name & Branch Name */
    .highlight-box {
        font-weight: 700;
        color: #92400E;
        background-color: #FEF3C7;
        border: 1px solid #FDE68A;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
    }

    /* Interactive WhatsApp Correction Link Inside Card */
    .card-note {
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px dashed #E2E8F0;
        text-align: center;
        font-size: 0.95rem;
        color: #475569;
        font-weight: 500;
    }
    .whatsapp-btn {
        display: inline-block;
        margin-top: 8px;
        padding: 8px 18px;
        background-color: #25D366;
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 20px;
        text-decoration: none;
        box-shadow: 0 2px 6px rgba(37, 211, 102, 0.35);
        transition: background-color 0.2s ease-in-out;
    }
    .whatsapp-btn:hover {
        background-color: #1EBE5D;
        text-decoration: none;
    }

    /* Smartphone Breakpoint Optimizations (max-width: 480px) */
    @media (max-width: 480px) {
        .header-h1 {
            font-size: 1.55rem;
        }
        .header-h2 {
            font-size: 0.95rem;
            margin-bottom: 1.4rem;
        }
        .detail-row {
            font-size: 1.08rem;
            gap: 6px; /* Tightens auto-spacing gracefully on smaller screens */
        }
        .detail-label {
            font-size: 1rem;
        }
        .card-note {
            font-size: 0.88rem;
        }
    }

    /* Standard Professional Footer Credit with Generous Spacing */
    .standard-credit {
        margin-top: 4.5rem !important;
        margin-bottom: 2.5rem !important;
        padding-top: 1.8rem;
        padding-bottom: 1.5rem;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.8;
        background-color: #FFFFFF !important;
    }
    .credit-author {
        font-weight: 700;
        color: #0F172A;
    }
    .credit-sub {
        font-size: 0.85rem;
        color: #64748B;
    }
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
                    cleaned_row = [
                        str(cell).replace("\n", " ").strip() if cell else ""
                        for cell in row
                    ]

                    if headers is None and "Mobile Number" in cleaned_row:
                        headers = cleaned_row
                        continue

                    if "Mobile Number" in cleaned_row or "Role" in cleaned_row:
                        continue

                    if any(cleaned_row):
                        all_rows.append(cleaned_row)

    if not all_rows or headers is None:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows, columns=headers)
    df.columns = df.columns.str.strip()

    if "Circle No" in df.columns:
        df["Circle No"] = df["Circle No"].replace("", pd.NA).ffill()

    if "Mobile Number" in df.columns:
        df["Clean_Mobile"] = (
            df["Mobile Number"].str.replace(r"\D", "", regex=True).str[-10:]
        )

    return df


# Callback function to clear the search input box
def clear_input():
    st.session_state["phone_input"] = ""
    st.session_state["search_triggered"] = False


# Initialize session state variables
if "phone_input" not in st.session_state:
    st.session_state["phone_input"] = ""
if "search_triggered" not in st.session_state:
    st.session_state["search_triggered"] = False

# 1. Page Headers (H1 & Upgraded Grammatical H2)
st.markdown(
    """
    <div>
        <div class="header-h1">Census 2027 Malavalli Rural</div>
        <div class="header-h2">Bank Account Details of Enumerators and Supervisors for HLO Remuneration</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Load PDF Data
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

# 3. Mobile-Friendly Search Interface
if not df.empty:
    phone_input = st.text_input(
        "Mobile Number",
        max_chars=10,
        key="phone_input",
        placeholder="enter mobile number and click search",
        help="Please enter exactly 10 numeric digits.",
    )

    # Search and Clear buttons side by side (Both styled Red with White Text)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["search_triggered"] = True
    with col2:
        st.button(
            "Clear",
            on_click=clear_input,
            type="secondary",
            use_container_width=True,
        )

    # Trigger search on button click or when user presses Enter
    if st.session_state["search_triggered"] or (
        phone_input and len(phone_input) == 10
    ):
        search_term = "".join(filter(str.isdigit, phone_input))

        # Enforce exactly 10 digits
        if len(search_term) != 10:
            st.warning(
                "⚠️ Please enter exactly 10 digits for the mobile number."
            )
        else:
            results = df[df["Clean_Mobile"] == search_term]

            if not results.empty:
                st.success(f"Found {len(results)} matching record(s).")
                for _, row in results.iterrows():
                    # Prefilled WhatsApp URL for instant correction reporting
                    wa_url = "https://wa.me/919008737033?text=Hello%20Sir,%20I%20need%20a%20correction%20in%20my%20Census%202027%20account%20details."

                    # Fluid Auto-Spacing Side-by-Side Layout in exact PDF order with highlights & WhatsApp Link
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="detail-row">
                                <span class="detail-label">Circle No :</span>
                                <span class="detail-value">{row.get('Circle No', 'N/A')}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Name :</span>
                                <span class="detail-value"><strong>{row.get('Name', 'N/A')}</strong></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Role :</span>
                                <span class="detail-value">{row.get('Role', 'N/A')}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Mobile No :</span>
                                <span class="detail-value">{row.get('Mobile Number', row.get('Clean_Mobile', 'N/A'))}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Account No :</span>
                                <span class="detail-value"><span class="highlight-box">{row.get('Account No', 'N/A')}</span></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">IFSC Code :</span>
                                <span class="detail-value"><span class="highlight-box">{row.get('IFSC Code', 'N/A')}</span></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Bank Name :</span>
                                <span class="detail-value"><span class="highlight-box">{row.get('Bank Name', 'N/A')}</span></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Branch Name :</span>
                                <span class="detail-value"><span class="highlight-box">{row.get('Branch Name', 'N/A')}</span></span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Address :</span>
                                <span class="detail-value">{row.get('Supervior/Enumerator School/Office Address', 'N/A')}</span>
                            </div>
                            <div class="card-note">
                                <span>Need any correction in your details?</span><br>
                                <a href="{wa_url}" target="_blank" class="whatsapp-btn">
                                    💬 WhatsApp for Correction
                                </a>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.error(
                    "❌ No account details found for this mobile number. Please check the number and try again."
                )
else:
    st.info("Waiting for official PDF data to load.")

# 4. Standard Professional Footer Credit with Balanced Spacing
st.markdown(
    """
    <div class="standard-credit">
        Designed & Developed by <span class="credit-author">Gangadhar</span><br>
        <span class="credit-sub">Statistical Inspector, Taluk Office Malavalli</span>
    </div>
    """,
    unsafe_allow_html=True,
)
