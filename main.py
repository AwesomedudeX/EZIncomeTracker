import streamlit as st

# Webpage Settings
st.set_page_config(page_title="Income Tracker", layout="wide", initial_sidebar_state="expanded")

requiredlibraries = [
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "sklearn"
]
totaltitles = ["Total Revenue", "Total Expenses", "Total Tax", "Net Income"]

# Importing libraries/modules
try:

    import os
    import time

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sn

    from sklearn.linear_model import LinearRegression as lreg

except:
    pass

# Session state variable initialization
if ["revenue", "expenses", "tax", "totalrevenue", "totalexpenses", "totaltax", "netincome", "totalvals", "userdata"] not in st.session_state:

    os.system("pip install --upgrade")

    for lib in requiredlibraries:
        os.system(f"pip install {lib}")
        
    import os
    import time

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sn

    from sklearn.linear_model import LinearRegression as lreg

    # Initializing dictionaries to hold income data
    st.session_state.revenue = {}
    st.session_state.expenses = {}
    st.session_state.tax = {}

    # Initializing values to hold income data totals
    st.session_state.totalrevenue = 0
    st.session_state.totalexpenses = 0
    st.session_state.totaltax = 0
    st.session_state.netincome = 0
    st.session_state.totalvals = {}
    st.session_state.totalvalsstr = {}

    st.session_state.userdata = pd.DataFrame()

    for title in totaltitles:
        st.session_state.totalvals[title] = []
        st.session_state.totalvalsstr[title] = []
        st.session_state.userdata[title] = []

    st.session_state.userdata.to_csv("data.csv")


# Defining methods
def savedata():
    for title in totaltitles:
        st.session_state.userdata[title] = list(st.session_state.userdata[title]).append(st.session_state.totalvals[title][0])


pages = ["Home", "Create Entry"]
sidebar = st.sidebar

st.sidebar.title(":green[EZ] Income Tracker")

page = st.sidebar.radio("**Navigation:**", pages)

if page == "Home":
    st.title("Income Tracker")

else:
    
    st.title(page)

    download = sidebar.download_button("Download Data", st.session_state.userdata.to_csv(), file_name="data.csv")

    if page == "Create Entry":

        revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=1)
        expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=1)

        if revenuecount > 0:
            
            st.write("---")
            st.header("Revenue Sources")

            c1, c2, c3 = st.columns(3)

            for i in range(revenuecount):

                name = c1.text_input(f"**Revenue Source {i+1}:**")

                st.session_state.revenue[name] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01)
                st.session_state.tax[name] = st.session_state.revenue[name] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01


        if expensecount > 0:
            
            st.write("---")
            st.header("Expenses")

            c1, c2 = st.columns(2)

            for i in range(expensecount):

                name = c1.text_input(f"**Expense {i+1}:**")

                st.session_state.expenses[name] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

        st.write("---")

        st.session_state.totalrevenue = sum(st.session_state.revenue.values())
        st.session_state.totalexpenses = sum(st.session_state.expenses.values())
        st.session_state.totaltax = sum(st.session_state.tax.values())

        c1, c2, c3 = st.columns(3)

        st.session_state.netincome = st.session_state.totalrevenue - st.session_state.totalexpenses - st.session_state.totaltax


        revenuestr = f"{np.abs(round(st.session_state.totalrevenue, 2))}"

        if (len(revenuestr.split(".")[1]) == 1):
            revenuestr += "0"

        if (st.session_state.totalrevenue == 0):
            revenuestr = f"(0.00)"        

        if st.session_state.totalrevenue < 0:
            revenuestr = f"({revenuestr})"


        expensestr = f"{round(st.session_state.totalexpenses, 2)}"

        if (len(expensestr.split(".")[1]) == 1):
            expensestr += "0"

        if (st.session_state.totalexpenses == 0):
            expensestr = f"0.00"        


        taxstr = f"{round(st.session_state.totaltax, 2)}"

        if (len(taxstr.split(".")[1]) == 1):
            taxstr += "0"

        if (st.session_state.totaltax == 0):
            taxstr = f"0.00"        


        netincomestr = f"{np.abs(round(st.session_state.netincome, 2))}"

        if (len(netincomestr.split(".")[1]) == 1):
            netincomestr += "0"

        if st.session_state.netincome < 0:
            netincomestr = f"({netincomestr})"

        if (st.session_state.netincome == 0):
            netincomestr = f"(0.00)"        


        st.session_state.totalvals = {
        
            "Total Revenue": [st.session_state.netincome],
            "Total Expenses": [st.session_state.netincome],
            "Total Tax": [st.session_state.totaltax],
            "Net Income": [st.session_state.netincome]
        
        }

        st.session_state.totalvalsstr = {
        
            "Total Revenue": [f"$ {revenuestr}"],
            "Total Expenses": [f"$ ({expensestr})"],
            "Total Tax": [f"$ ({taxstr})"],
            "Net Income": [f"$ {netincomestr}"]
        
        }

        st.session_state.totalvalsstr = pd.DataFrame().from_dict(st.session_state.totalvalsstr)

        st.write("---")
        st.dataframe(st.session_state.totalvalsstr, hide_index=True)

        if sidebar.button("Save Entry"):
            savedata()
