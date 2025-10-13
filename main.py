import streamlit as st

# Webpage Settings
st.set_page_config(page_title="EZ Income Tracker", layout="wide", initial_sidebar_state="expanded", page_icon="logo.png")

# Initializing constant variables
requiredlibraries = [
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "sklearn"
]
totaltitles = ["Month No.", "Month", "Year", "Total Revenue", "Total Expenses", "Total Tax", "Net Income"]
pages = ["Home", "Add an Entry", "Your Income Data", "Edit an Entry", "Visualize Your Data"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Importing libraries/modules
import os
import time
from datetime import datetime as dt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn

from sklearn.linear_model import LinearRegression as lreg

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
    
    try:

        for col in df.columns:
            if "Unnamed" in col:
                df.drop(col, axis='columns', inplace=True)

        print(f"User {st.session_state.userid}'s data was cleaned successfully.")

    except:
        print(f"ERROR: Could not clean User {st.session_state.userid}'s data.")

    return df

def saveEntries(df, id):

    df = cleanData(df)

    try:

        write = str(df.to_csv())
        open(f"data_{id}.csv", "w").write(write)
        print(f"\nSaved {st.session_state.userid}'s data sucessfully.")

    except:
        print(f"\nERROR: Could not save {st.session_state.userid}'s data.")

def addEntry(df, newvals: dict, id):

    try:
    
        data = {}

        for title in totaltitles:

            data[title] = []

            for val in df[title]:
                data[title].append(val)

            data[title].append(newvals[title][0])
        
        newdf = pd.DataFrame().from_dict(data)
        saveEntries(newdf, id)
        
        print(f"\nEntry created sucessfully for User {st.session_state.userid}.")

    except:
        print(f"\nERROR: Entry could not be created for User {st.session_state.userid}.")

if "userdata" not in st.session_state or "userid" not in st.session_state or "currentids" not in st.session_state:

    st.session_state.currentids = []

    try:
        st.session_state.userdata = pd.read_csv("data.csv")

    except:
        
        st.session_state.userdata = pd.DataFrame()

        for title in totaltitles:
            st.session_state.userdata[title] = []
            
    import users

    st.session_state.currentids = users.userids
    st.session_state.userid = st.session_state.currentids[-1] + 1


sidebar = st.sidebar

st.sidebar.title(":green[EZ] Income Tracker")

page = st.sidebar.radio("**Navigation:**", pages)

if sidebar.button("Refresh Page"):
    sidebar.success("Page refreshed successfully!")
    
if len(st.session_state.userdata) > 0:
    st.session_state.userdata = cleanData(st.session_state.userdata)
    download = sidebar.download_button("Download Data", st.session_state.userdata.to_csv(index=False), file_name="data.csv")

if page == "Home":

    st.title(":green[EZ] Income Tracker")
    st.write("Welcome to **:green[EZ] Income Tracker.** This website will help you with **all** of your income tracking needs, with **data management**, **analysis**, **visualization** and **prediction features** that make budgeting **quick**, **easy** and **secure**. Make sure to create entries **every month** for the **best** results.")
    st.write("**If you have used this website before**, upload your **`data.csv`** file from your **last session** to the box **below**. If this is your first time, head to the **`Add an Entry`** page to get started. Once you're done, make sure to **save your data** by hitting the **`Download Data`** button on the sidebar **to the left**.")

    datafile = st.file_uploader("**Upload your data file below:**", accept_multiple_files=False, type=["csv"])

    if datafile and st.button("Upload File"):
        
        try:

            df = pd.read_csv(datafile)

            st.success("Data file uploaded successfully!")

            df = cleanData(df)
            st.session_state.userdata = df
            saveEntries(st.session_state.userdata, st.session_state.userid)


        except:
            st.error("There was an issue in uploading your file. Please try again.")

else:

    st.title(page)
    
    now = dt.now()
    currentmonth = now.strftime("%B")
    currentyear = int(now.strftime("%Y"))
    monthindex = 0
    lendata = len(st.session_state.userdata)
    
    if lendata > 1:
        currentmonthno = list(st.session_state.userdata["Month No."])[-1]+1
    
    else:
        currentmonthno = 1

    if page == "Add an Entry":

        revenue = {}
        expenses = {}
        tax = {}

        revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=1)
        expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=1)

        st.write("---")
        st.header("Time of Entry")

        c1, c2, c3 = st.columns(3)
    
        try:
            monthno = c1.number_input("**Month No.**", min_value=currentmonthno, step=1)

        except:
            monthno = c1.number_input("**Month No.**", min_value=1, step=1)

        for m in range(len(months)):
                
            if currentmonth == months[m]:
                monthindex = m
                break

        month = c2.selectbox("**Month**", months, index=monthindex)
        year = c3.number_input("**Year**", currentyear, step=1)


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
        
            "Month No.": [monthno],
            "Month": [month],
            "Year": [str(year)],
            "Total Revenue": [totalrevenue],
            "Total Expenses": [totalexpenses],
            "Total Tax": [totaltax],
            "Net Income": [netincome]
        
        }

        totalvalsstr = {
        
            "Month No.": [monthno],
            "Month": [month],
            "Year": [str(year)],
            "Total Revenue": [f"$ {revenuestr}"],
            "Total Expenses": [f"$ ({expensestr})"],
            "Total Tax": [f"$ ({taxstr})"],
            "Net Income": [f"$ {netincomestr}"]
        
        }


        totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

        st.write("---")
        st.header("Entry Preview")
        st.dataframe(totalvalsstr, hide_index=True, use_container_width=True)

        if sidebar.button("Add an Entry"):

            addEntry(st.session_state.userdata, totalvals, st.session_state.userid)
            st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
            st.session_state.userdata = cleanData(st.session_state.userdata)

            sidebar.success("Entry created successfully.")

            if st.session_state.userid not in st.session_state.currentids and lendata > 0:

                import users

                st.session_state.currentids = users.userids
                st.session_state.userid = st.session_state.currentids[-1] + 1
                st.session_state.currentids.append(st.session_state.userid)
                write = f"userids = {st.session_state.currentids}"

                try:
                    open("users.py", "w").write(write)
                    print(f"\nAdded User {st.session_state.userid} successfully and saved IDs to file.")
                except:
                    print(f"\nCould not add User {st.session_State.userid}.")

    elif page == "Your Income Data":

        showColsExpander = sidebar.expander("**Selected Columns**")
        showCols = []


        for title in totaltitles:
            
            if showColsExpander.checkbox(title, value=True):
                showCols.append(title)

        st.session_state.userdata = cleanData(st.session_state.userdata)

        if lendata == 0:
            st.subheader("Please add an entry before attempting to view your entries.")            

        else:

            interpolationExpander = sidebar.expander("**Interpolate Missing Data**")

            interpolationExpander.write("Interpolate data for months that were missed in the recording process. Choose the month to interpolate, and we'll predict what the data would have been up to that month.")

            startentry = sidebar.number_input("Starting Entry Number", 1, lendata, value=1)-1
            endentry = sidebar.number_input("Ending Entry Number", startentry, lendata, value=lendata)

            if showCols == []:
                st.subheader("Please select a column to view.")

            else:

                st.dataframe(st.session_state.userdata[showCols].iloc[startentry:endentry], use_container_width=True, hide_index=True)

                if st.expander("**:red[DANGER ZONE]**").button("**:red[Clear ALL Entries]**", use_container_width=True):
                    
                    newdata = {}

                    for title in totaltitles:
                        newdata[title] = []

                    st.session_state.userdata = pd.DataFrame.from_dict(newdata)

                    saveEntries(st.session_state.userdata, st.session_state.userid)
                    st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                    st.session_state.userdata = cleanData(st.session_state.userdata)

    elif page == "Edit an Entry":

        if lendata == 0:
            st.subheader("Please add an entry before attempting to edit your entries.")            

        else:

            revenue = {}
            expenses = {}
            tax = {}

            entryno = sidebar.number_input("**Entry Number:**", min_value=1, max_value=lendata) - 1
            revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=1)
            expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=1)

            st.write("---")
            st.header("Time of Entry")

            c1, c2, c3 = st.columns(3)
        
            try:
                monthno = c1.number_input("**Month No.**", min_value=currentmonthno, step=1)

            except:
                monthno = c1.number_input("**Month No.**", min_value=1, step=1)

            for m in range(len(months)):
                
                if currentmonth == months[m]:
                    monthindex = m
                    break

            month = c2.selectbox("**Month**", months, index=monthindex)
            year = c3.number_input("**Year**", currentyear, step=1)

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

            currentvals = {
            
                "Month No.": [st.session_state.userdata["Month No."][entryno]],
                "Month": [st.session_state.userdata["Month"][entryno]],
                "Year": [st.session_state.userdata["Year"][entryno]],
                "Total Revenue": [st.session_state.userdata["Total Revenue"][entryno]],
                "Total Expenses": [st.session_state.userdata["Total Expenses"][entryno]],
                "Total Tax": [st.session_state.userdata["Total Tax"][entryno]],
                "Net Income": [st.session_state.userdata["Net Income"][entryno]]
            
            }

            totalvals = {
            
                "Month No.": [monthno],
                "Month": [month],
                "Year": [str(year)],
                "Total Revenue": [totalrevenue],
                "Total Expenses": [totalexpenses],
                "Total Tax": [totaltax],
                "Net Income": [netincome]
            
            }

            st.write("---")

            st.subheader("Current Entry:")
            st.dataframe(currentvals, hide_index=True, use_container_width=True)
            st.subheader("Edited Entry:")
            st.dataframe(totalvals, hide_index=True, use_container_width=True)

            st.write("---")

            st.expander("**Current Entries**").dataframe(st.session_state.userdata, use_container_width=True)

            if sidebar.button("Save Entry"):

                for title in totaltitles:
                    st.session_state.userdata[title][entryno] = totalvals[title][0]
                
                saveEntries(st.session_state.userdata, st.session_state.userid)

                sidebar.success("Entry saved successfully.")

    elif page == "Visualize Your Data":

        if lendata > 1:

            cols = [c for c in st.session_state.userdata.columns if c not in ["Month No.", "Month", "Year"]]
            selectedcol = sidebar.selectbox("Column to Plot:", cols)
            monthnos = [int(m) for m in st.session_state.userdata["Month No."]]

            gtypes = ["Scatter Plot", "Line Plot", "Linear Regression Plot", "Bar Plot"]
            gtype = sidebar.selectbox("**Graph Type:**", gtypes)
            startentry = sidebar.number_input("**Starting Entry:**", min_value=1, max_value=lendata-1)-1
            endentry = sidebar.number_input("**Ending Entry:**", min_value=startentry, max_value=lendata, value=lendata)

            x = list(st.session_state.userdata["Month No."])[startentry:endentry]
            y = list(st.session_state.userdata[selectedcol])[startentry:endentry]

            darkbg = sidebar.checkbox("Dark Mode", value=True)

            if darkbg:
                plt.style.use("dark_background")
            else:
                plt.style.use("classic")

            fig, ax = plt.subplots()
            ax.set_xticks(np.arange(0, np.max(monthnos)+1, 1))
            
            if gtype == "Scatter Plot":
                sn.scatterplot(x=x, y=y)

            elif gtype == "Line Plot":
                sn.lineplot(x=x, y=y)

            elif gtype == "Linear Regression Plot":
                sn.regplot(x=x, y=y)

            else:
                sn.barplot(x=x, y=y)
            
            st.pyplot(fig)

        else:
            st.subheader("Please enter more than one entry to plot a graph of your data.")
