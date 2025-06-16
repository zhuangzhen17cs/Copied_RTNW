# === INTERFACE ===

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from quantile_dotplot import ntile_dotplot
from sandbox_openai import search_product_category
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="assets/logo.ico",  # .ico, .png, .jpg all work
    layout="wide"
)

st.image("assets/digikey_big_logo.png", width=300)

#st.title("Digikey App")
st.subheader("Manage Your Inventory With AI to Ride the Next Wave")

# Create HTML table function
def render_html_table(dataframe):
    html = '''
    <style>
        table, th, td {
                font-family: Arial, sans-serif;
            }
        .toggle-box { cursor: pointer; color: blue; text-decoration: underline; }
        .full-text { display: none; }
        .desc-cell { max-width: 400px; }
    </style>
    <script>
        function toggleDesc(id) {
            var short = document.getElementById("short_" + id);
            var full = document.getElementById("full_" + id);
            var link = document.getElementById("link_" + id);
            if (full.style.display === "none") {
                full.style.display = "inline";
                short.style.display = "none";
                link.innerText = "See less";
            } else {
                full.style.display = "none";
                short.style.display = "inline";
                link.innerText = "See more";
            }
        }
    </script>
    <div style="overflow-x: auto; width: 100%;border: 2px solid #eee; padding-bottom: 10px; 
    box-sizing: border-box;">
        <table style="border-collapse: collapse; width: max-content; min-width: 100%;">
            <thead><tr>
    '''

    for col in dataframe.columns:
        html += f'<th style="padding: 8px; background-color: #ffffff; border: 2px solid #eee;">{col}</th>'
    html += '</tr></thead><tbody>'

    for idx, row in dataframe.iterrows():
        html += '<tr>'
        for col, val in zip(dataframe.columns, row):
            if col == "Description" and isinstance(val, str) and len(val) > 60:
                short = val[:60].strip() + "..."
                full = val
                html += f'''
                <td class="desc-cell" style="padding: 8px;border:2px solid #eee;">
                    <span id="short_{idx}">{short}</span>
                    <span id="full_{idx}" class="full-text">{full}</span>
                    <span id="link_{idx}" class="toggle-box" onclick="toggleDesc({idx})">See more</span>
                </td>
                '''
            else:
                html += f'<td style="padding: 8px; border:2px solid #eee;">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# Create tabs
tab2, tab1 = st.tabs([ "Product Table", "Product Search & Analysis"])

with tab1:
    st.subheader("Product Search")
    df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')
    raw_df = df.copy()
    cat_list = df["Product Category"].unique().tolist()

    with st.expander("Search Product"):
        cat = st.selectbox(" ",
        sorted(cat_list), placeholder= "Plug Housings")

        if st.button("Search"):
            st.write("The Category Being Searched is:", cat)

        col1, col2 = st.columns(2)

        with col1:
            st.header("Quantile Dot Plot")
            st.image("figures/sfp_{}.png".format(cat.translate(str.maketrans(" /", "__"))))
     
        with col2:
            st.header("Summary")
            spinner_container = st.empty()
            with spinner_container:
                _, center_col, _ = st.columns([1, 2, 1])
                with center_col:
                    with st.spinner("Generating insights...", show_time=False):
                        result = search_product_category(cat)
            
            spinner_container.empty()
            st.write(result)

with tab2:
    st.subheader("Product Table")

    df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')

    df['Product Category'] = df.apply(
        lambda row: f'<a href="{row["Product url"]}" target="_blank">{row["Product Category"]}</a>',
        axis=1
    )
    df = df.drop(columns=['Product url'])
    df = df.drop(columns=['090_day_forecast'])
    df['90 Days Forecast'] = df['90 Days Forecast'].round()
    df = df.drop(df.columns[-1], axis=1)
    df = df.drop(df.columns[[4]], axis=1)

    for i in range(1, 4):  # Adjust range if you have more than 3 articles
        title_col = f'Article_{i}_Title'
        link_col = f'Article_{i}_Link'
        if title_col in df.columns and link_col in df.columns:
            df[title_col] = df.apply(
                lambda row: f'<a href="{row[link_col]}" target="_blank">{row[title_col]}</a>' 
                if pd.notna(row[link_col]) and pd.notna(row[title_col]) else '',
                axis=1
            )
            df = df.drop(columns=[link_col])

    df = df.fillna('')
    col1,col2 = st.columns([3, 1])

    with col1:
        selected_cat2 = st.selectbox(" ", sorted(cat_list), placeholder="Search here")

    with col2:
        new_df = raw_df[["Product Category", "Products", "90 Days Forecast", "Description", "Article_1_Score", "Article_1_Title","Article_2_Score","Article_2_Title","Article_3_Score","Article_3_Title"]].copy()
        csv = new_df.to_csv(index=False)
        st.write("") 
        st.write("") 
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="product_data.csv",
            mime="text/csv"
        )

    if selected_cat2:
        filtered_df = df[df["Product Category"].str.contains(selected_cat2, case=False, na=False)]
        if not filtered_df.empty:
            components.html(render_html_table(filtered_df), height=400, scrolling=True)
        else:
            st.warning("No matching category found.")