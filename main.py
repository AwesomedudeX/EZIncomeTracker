import streamlit as st

# Webpage Settings
st.set_page_config(page_title="EZ Income Tracker", layout="wide", initial_sidebar_state="expanded", page_icon="💵")

# Initializing constant variables
requiredlibraries = [
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "sklearn"
]
totaltitles = ["Total Revenue", "Total Expenses", "Total Tax", "Net Income"]
pages = ["Home", "Create Entry", "View Entries"]

# Importing libraries/modules
import os
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn

from sklearn.linear_model import LinearRegression as lreg

if ["userdata"] not in st.session_state:

    try:
        st.session_state.userdata = pd.read_csv("data.csv")

    except:
        
        st.session_state.userdata = pd.DataFrame()

        for title in totaltitles:
            st.session_state.userdata[title] = []

def isNum(num: str):
    
    try:
        num = float(num)
    
    except:
        
        try:
            num = int(num)

        except:
            return False
        
    return True

def cleanData(df):
    
    if "Unnamed: 0" in df.columns:
        df.drop("Unnamed: 0", axis='columns', inplace=True)

    return df

def addEntry(df, newvals: dict):

    data = {}

    for title in totaltitles:

        data[title] = []

        for val in df[title]:
            data[title].append(val)

        data[title].append(newvals[title][0])
    
    newdf = pd.DataFrame().from_dict(data)
    newdf = cleanData(newdf)

    write = str(newdf.to_csv())
    open("data.csv", "w").write(write)

def saveEntries(df):

    df = cleanData(df)

    write = str(df.to_csv())
    open("data.csv", "w").write(write)


sidebar = st.sidebar

st.sidebar.title(":green[EZ] Income Tracker")

page = st.sidebar.radio("**Navigation:**", pages)

if sidebar.button("Refresh Page"):
    sidebar.success("Page refreshed successfully!")

if page == "Home":

    st.title(":green[EZ] Income Tracker")
    st.write("Welcome to **:green[EZ] Income Tracker.** This website will help you with all of your income tracking needs, with data management, analysis, visualization and prediction features that make budgeting easy. Make sure to create entries **every month** for the best results. If you have used this app before, upload your `data.csv` file from your last session to the upload box below. If this is your first time, head to `Create Entry` to get started.")

    datafile = st.file_uploader("**Upload your data file below:**", accept_multiple_files=False, type=["csv"])

    if datafile and st.button("Upload File"):
        
        try:

            df = pd.read_csv(datafile)

            st.success("Data file uploaded successfully!")

            df = cleanData(df)
            st.session_state.userdata = df
            saveEntries(st.session_state.userdata)


        except:
            st.error("There was an issue in uploading your file. Please try again.")

else:
    
    st.title(page)

    download = sidebar.download_button("Download Data", st.session_state.userdata.to_csv(), file_name="data.csv")

    if page == "Create Entry":

        revenue = {}
        expenses = {}
        tax = {}

        revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=1)
        expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=1)

        if revenuecount > 0:
            
            st.write("---")
            st.header("Revenue Sources")

            c1, c2, c3 = st.columns(3)

            for i in range(revenuecount):

                name = c1.text_input(f"**Revenue Source {i+1}:**")

                revenue[name] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01)
                tax[name] = revenue[name] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                revenue[name] = round(revenue[name], 2)
                tax[name] = round(tax[name], 2)

        if expensecount > 0:
            
            st.write("---")
            st.header("Expenses")

            c1, c2 = st.columns(2)

            for i in range(expensecount):

                name = c1.text_input(f"**Expense {i+1}:**")

                expenses[name] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)
                expenses[name] = round(expenses[name], 2)

        st.write("---")

        totalrevenue = sum(revenue.values())
        totalexpenses = sum(expenses.values())
        totaltax = sum(tax.values())

        c1, c2, c3 = st.columns(3)

        netincome = totalrevenue - totalexpenses - totaltax


        revenuestr = f"{np.abs(round(totalrevenue, 2))}"

        if (len(revenuestr.split(".")[1]) == 1):
            revenuestr += "0"

        if (totalrevenue == 0):
            revenuestr = f"(0.00)"        

        if totalrevenue < 0:
            revenuestr = f"({revenuestr})"


        expensestr = f"{round(totalexpenses, 2)}"

        if (len(expensestr.split(".")[1]) == 1):
            expensestr += "0"

        if (totalexpenses == 0):
            expensestr = f"0.00"        


        taxstr = f"{round(totaltax, 2)}"

        if (len(taxstr.split(".")[1]) == 1):
            taxstr += "0"

        if (totaltax == 0):
            taxstr = f"0.00"        


        netincomestr = f"{np.abs(round(netincome, 2))}"

        if (len(netincomestr.split(".")[1]) == 1):
            netincomestr += "0"

        if netincome < 0:
            netincomestr = f"({netincomestr})"

        if (netincome == 0):
            netincomestr = f"(0.00)"        


        totalvals = {
        
            "Total Revenue": [totalrevenue],
            "Total Expenses": [totalexpenses],
            "Total Tax": [totaltax],
            "Net Income": [netincome]
        
        }

        totalvalsstr = {
        
            "Total Revenue": [f"$ {revenuestr}"],
            "Total Expenses": [f"$ ({expensestr})"],
            "Total Tax": [f"$ ({taxstr})"],
            "Net Income": [f"$ {netincomestr}"]
        
        }

        totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

        st.write("---")
        st.dataframe(totalvalsstr, hide_index=True)

        if sidebar.button("Save Entry"):

            addEntry(st.session_state.userdata, totalvals)
            st.session_state.userdata = pd.read_csv("data.csv")
            st.session_state.userdata = cleanData(st.session_state.userdata)

    elif page == "View Entries":

        showColsExpander = sidebar.expander("**Selected Columns**")
        showCols = []

        for title in totaltitles:
            
            if showColsExpander.checkbox(title, value=True):
                showCols.append(title)

        st.session_state.userdata = cleanData(st.session_state.userdata)

        if len(st.session_state.userdata) == 0:
            st.subheader("Please add an entry before attempting to view your entries.")            

        else:

            startentry = sidebar.number_input("Starting Entry Number", 1, len(st.session_state.userdata), value=1)-1
            endentry = sidebar.number_input("Ending Entry Number", startentry, len(st.session_state.userdata), value=len(st.session_state.userdata))

            if showCols == []:
                st.subheader("Please select a column to view.")

            else:
                st.dataframe(st.session_state.userdata[showCols].iloc[startentry:endentry], use_container_width=True, hide_index=True)

                if st.expander("**:red[DANGER ZONE]**").button("**:red[Clear ALL Entries]**", use_container_width=True):
                    
                    newdata = {}

                    for title in totaltitles:
                        newdata[title] = []

                    st.session_state.userdata = pd.DataFrame.from_dict(newdata)

                    saveEntries(st.session_state.userdata)
