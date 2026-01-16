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
defaultcols = ["Month No.", "Month", "Year", "Total Revenue", "Total Expenses", "Total Tax", "Net Income"]
pages = ["Home", "Create an Entry", "Your Income Data", "Edit Your Entries", "Analyze Your Data", "Plan Your Budget"]
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
from sklearn.model_selection import train_test_split as tts

pd.set_option("display.max_columns", None, "display.max_rows", None)

# General data checking/cleaning/conversion functions
def isNum(num: str):
    
    try:
        num = float(num)
    
    except:
        
        try:
            num = int(num)

        except:
            return False
        
    return True

def cleanDF(df: pd.DataFrame):
    
    try:

        for col in df.columns:
            if "Unnamed:" in col and "(Revenue)" not in col and "(Expense)" not in col and "(Tax)" not in col:
                df.drop(col, axis='columns', inplace=True)

        print(f"User {st.session_state.userid}'s data was cleaned successfully.")

    except:
        print(f"ERROR: Could not clean User {st.session_state.userid}'s data.")

    return df

def cleanData(data: dict):
    
    try:

        for col in data:
            if "Unnamed:" in col and "(Revenue)" not in col and "(Expense)" not in col and "(Tax)" not in col:
                del data[col]

        print(f"User {st.session_state.userid}'s data was cleaned successfully.")

    except:
        print(f"ERROR: Could not clean User {st.session_state.userid}'s data.")

    return data

def toDF(data: dict):
    return pd.DataFrame.from_dict(data)

# Program-specific functions
def saveEntries(df, id):

    df = cleanDF(df)

    try:

        write = str(df.to_csv())
        open(f"data_{id}.csv", "w").write(write)
        print(f"\nSaved User {id}'s data sucessfully.")

    except:
        print(f"\nERROR: Could not save User {id}'s data.")

def sortAccounts(df: pd.DataFrame):

    newdata = {}

    for col in df.columns:
        if col in defaultcols or col[-9:] == "(Revenue)" or col[-5:] == "(Tax)":
            newdata[col] = df[col]

    for col in df.columns:
        if col[-9:] == "(Expense)":
            newdata[col] = df[col]
    
    newdf = pd.DataFrame().from_dict(newdata)
    return cleanDF(newdf)

def colSelector(defaultval: bool = True):
    
    showCols = []

    selectall = st.checkbox("Select All", value=defaultval)

    for col in st.session_state.userdata.columns:
        
        if st.checkbox(col, value=selectall):
            showCols.append(col)

    return showCols

# Prediction function, used in multiple parts of the program, with cached outputs for better performance
@st.cache_data
def predict(data: dict, predmonths: list, startentry: int, endentry: int, returnasdf: bool = False):

    ycols = [c for c in data if c not in defaultcols[:3]]
    x = data["Month No."][startentry-1:endentry]
    y = data[ycols].iloc[startentry-1:endentry]

    xtrain, xtest, ytrain, ytest = tts(x, y, test_size=0.2, random_state=40)
    xtrain, xtest = xtrain.values.reshape(-1, 1), xtest.values.reshape(-1, 1)
    lr = lreg().fit(xtrain, ytrain)

    predmonthsfmt = [[m] for m in predmonths]
    pred = lr.predict(predmonthsfmt)
    preddict = {}

    preddict["Month No."] = predmonths
    preddict["Month"] = ["N/A" for i in range(len(predmonths))]
    preddict["Year"] = ["N/A" for i in range(len(predmonths))]

    for title in defaultcols:
        if title not in defaultcols[:3]:
            preddict[title] = 0                 

    for c in range(len(ycols)):

        predcol = []

        for i in range(len(pred)):
            predcol.append(round(pred[i][c], 2))

        preddict[ycols[c]] = predcol

    for col in [c for c in preddict if c not in defaultcols[:3]]:

        if type(preddict[col]) != list:
            preddict[col] = [preddict[col]]

        for i in range(len(preddict[col])):

            if col[-9:] == "(Revenue)":
                preddict["Total Revenue"][i] += preddict[col][i]

            if col[-9:] == "(Expense)":
                preddict["Total Expenses"][i] += preddict[col][i]
                
            if col[-5:] == "(Tax)":
                preddict["Total Tax"][i] += preddict[col][i]

    preddict["Net Income"] += (preddict["Total Revenue"][0] - preddict["Total Tax"][0] - preddict["Total Expenses"][0])
    
    if returnasdf:
        return toDF(preddict)
    else:
        return preddict

if "userdata" not in st.session_state or "userid" not in st.session_state or "currentids" not in st.session_state or "budgetdata" not in st.session_state or "uploadedbudgetfile" not in st.session_state:

    st.session_state.currentids = []

    try:
        st.session_state.userdata = pd.read_csv("data.csv")

    except:
        
        st.session_state.userdata = pd.DataFrame()

        for title in defaultcols:
            st.session_state.userdata[title] = []
            
    import users

    st.session_state.currentids = users.userids
    st.session_state.userid = st.session_state.currentids[-1] + 1

    st.session_state.budgetdata = {}
    st.session_state.budgetdata["Account"] = []
    st.session_state.budgetdata["Subaccount"] = []
    st.session_state.budgetdata["Amount ($)"] = []

    st.session_state.uploadedbudgetfile = False


sidebar = st.sidebar

# REMOVE AFTER RELEASE
if sidebar.button("Push to GitHub"):
    os.system("git add .")
    os.system("git commit -m \"Remote Update\"")
    os.system("git push origin main")        

st.sidebar.title(":green[EZ] Income Tracker")

page = st.sidebar.radio("**Navigation:**", pages)

if sidebar.button("Refresh Page"):
    sidebar.success("Page refreshed successfully!")
    
if len(st.session_state.userdata) > 0:

    if type(st.session_state.userdata) == dict:
        st.session_state.userdata = pd.DataFrame().from_dict(st.session_state.userdata)

    st.session_state.userdata = cleanDF(st.session_state.userdata)
    download = sidebar.download_button("Download Data", st.session_state.userdata.to_csv(index=False), file_name="data.csv")

if page == "Home":

    st.title(":green[EZ] Income Tracker")
    st.write("Welcome to **:green[EZ] Income Tracker.** This website will help you with **all** of your income tracking needs, with **data management**, **analysis**, **visualization** and **prediction features** that make budgeting **quick**, **easy** and **secure**. Make sure to create entries **every month** for the **best** results.")
    st.write("**If you have used this website before**, upload your **`data.csv`** file from your **last session** to the box **below**. If this is your first time, head to the **`Add an Entry`** page to get started. Once you're done, make sure to **save your data** by hitting the **`Download Data`** button on the sidebar **to the left**.")

    datafile = st.file_uploader("**Upload your data file below:**", accept_multiple_files=False, type=["csv"])

    if datafile and st.button("Upload File"):
        
        try:

            df = pd.read_csv(datafile)
            lendata = len(st.session_state.userdata)

            st.success("Your data file was uploaded successfully!")

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
                    print(f"\nCould not add User {st.session_state.userid}.")

            df = cleanDF(df)
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

    for m in range(len(months)):
            
        if currentmonth == months[m]:
            monthindex = m
            break

    st.session_state.userdata = sortAccounts(st.session_state.userdata)    

    if lendata > 0:
        currentmonthno = list(st.session_state.userdata["Month No."])[-1]+1
    
    else:
        currentmonthno = 1

    if page == "Create an Entry":

        st.write(":grey[**Note:** For the month number to update, you may need to refresh the page after adding an entry if you plan on adding multiple entries.]")

        existingrevs = []
        existingexps = []
        existingtaxes = []

        for col in st.session_state.userdata.columns:

            if "(Revenue)" == col[-9:]:
                existingrevs.append(col)

            elif "(Expense)" == col[-9:]:
                existingexps.append(col)

            elif "(Tax)" == col[-5:]:
                existingtaxes.append(col)

        revenue = {}
        expenses = {}
        tax = {}

        revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=len(existingrevs), min_value=0)
        expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=len(existingexps), min_value=0)

        st.write("---")
        st.header("Time of Entry")

        c1, c2, c3 = st.columns(3)
    
        try:
            monthno = c1.number_input("**Month No.**", min_value=currentmonthno, step=1)

        except:
            monthno = c1.number_input("**Month No.**", min_value=1, step=1)


        month = c2.selectbox("**Month**", months, index=monthindex)
        year = c3.number_input("**Year**", currentyear, step=1)

        if revenuecount == 0 and expensecount == 0:
            st.write("---")
            st.subheader("**Use the sidebar on the left to add accounts.**")

        if revenuecount > 0:
            
            st.write("---")
            st.header("Revenue Sources")
            
            unnamedaccounts = 0

            for i in range(revenuecount):

                c1, c2, c3 = st.columns(3)
    
                accname = ""

                if (i < len(existingrevs)):
                    accname = existingrevs[i][:-10]

                if accname[:23] == "Unnamed Revenue Account":
                    unnamedaccounts += 1

                name = c1.text_input(f"**Revenue Source {i+1}:**", value=accname)

                if name == "":
                    
                    unnamedaccounts += 1
                    revenuecol = f"Unnamed Revenue Account {unnamedaccounts} (Revenue)"
                    taxcol = f"Unnamed Revenue Account {unnamedaccounts} (Tax)"

                else:
                    revenuecol = f"{name} (Revenue)"
                    taxcol = f"{name} (Tax)"

                if revenuecol in revenue:
                    revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                else:
                    revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                if taxcol in tax:
                    tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                else:
                    tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                revenue[revenuecol] = round(revenue[revenuecol], 2)
                tax[taxcol] = round(tax[taxcol], 2)

        if expensecount > 0:
            
            st.write("---")
            st.header("Expenses")

            unnamedaccounts = 0

            for i in range(expensecount):

                c1, c2 = st.columns(2)

                accname = ""

                if (i < len(existingexps)):
                    accname = existingexps[i][:-10]
                
                if accname[:23] == "Unnamed Expense Account":
                    unnamedaccounts += 1

                name = c1.text_input(f"**Expense {i+1}:**", value=accname)

                if name == "":
                    unnamedaccounts += 1
                    expensecol = f"Unnamed Expense Account {unnamedaccounts} (Expense)"

                else:
                    expensecol = f"{name} (Expense)"
                    
                if expensecol in expenses:
                    expenses[expensecol] += c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                else:
                    expenses[expensecol] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=0.)

                expenses[expensecol] = round(expenses[expensecol], 2)


        totalrevenue = sum(revenue.values())
        totalexpenses = sum(expenses.values())
        totaltax = sum(tax.values())

        c1, c2, c3 = st.columns(3)

        netincome = totalrevenue - totalexpenses - totaltax


        revenuestr = f"{round(totalrevenue, 2)}"

        if ("." in revenuestr and len(revenuestr) > 1 and len(revenuestr.split(".")[1]) == "1"):
            revenuestr += "0"

        if (totalrevenue == 0):
            revenuestr = f"(0.00)"

        expensestr = f"{round(totalexpenses, 2)}"

        if ("." in expensestr and len(expensestr) > 1 and len(expensestr.split(".")[1]) == "1"):
            expensestr += "0"

        if (totalexpenses == 0):
            expensestr = f"0.00"        


        taxstr = f"{round(totaltax, 2)}"

        if (len(taxstr) > 1 and len(taxstr.split(".")[1]) == "1"):
            taxstr += "0"

        if (totaltax == 0):
            taxstr = f"0.00"        


        netincomestr = f"{np.abs(round(netincome, 2))}"

        if ("." in netincomestr and len(netincomestr.split(".")[1]) == 1):
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

        for revenueacc, taxacc in zip(revenue.keys(), tax.keys()):

            totalvals[revenueacc] = [revenue[revenueacc]]
            totalvals[taxacc] = [tax[taxacc]]

            revenuestr = f"{round(revenue[revenueacc], 2)}"

            if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                revenuestr += "0"

            if (totalrevenue == 0):
                revenuestr = f"(0.00)"

            taxstr = f"{round(tax[taxacc], 2)}"

            if ("." in taxstr and len(taxstr.split(".")[1]) == 1):
                taxstr += "0"

            if (tax[taxacc] == 0):
                taxstr = f"0.00"
            
            totalvalsstr[revenueacc] = [f"$ {revenuestr}"]
            totalvalsstr[taxacc] = [f"$ ({taxstr})"]

        for acc in expenses:

            expensestr = f"{round(expenses[acc], 2)}"

            if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                expensestr += "0"

            if (expenses[acc] == 0):
                expensestr = f"0.00"

            totalvals[acc] = [expenses[acc]]
            totalvalsstr[acc] = [f"$ ({expensestr})"]

        totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

        st.write("---")
        st.header("Entry Preview")
        st.dataframe(totalvalsstr, hide_index=True, use_container_width=True)

        if sidebar.button("Add an Entry"):
                
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
                    print(f"\nCould not add User {st.session_state.userid}.")

            try:
            
                data = {}

                for col in st.session_state.userdata.columns:

                    data[col] = []

                    for val in st.session_state.userdata[col]:
                        data[col].append(val)

                    if col not in totalvals:
                        data[col].append(0)

                for acc in totalvals:
                        
                    if acc not in data:
                        if len(data["Month No."]) > 1:
                            data[acc] = [0 for i in range(len(data["Month No."])-1)]
                        else:
                            data[acc] = []
                
                    data[acc].append(totalvals[acc][0])

                data = cleanData(data)
                newdf = pd.DataFrame().from_dict(data)
                saveEntries(newdf, st.session_state.userid)

                print(f"\nEntry created sucessfully for User {st.session_state.userid}.")

            except:
                print(f"\nERROR: Entry could not be created for User {st.session_state.userid}.")

            st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
            st.session_state.userdata = cleanDF(st.session_state.userdata)

            sidebar.success("Entry created successfully.")

    elif page == "Your Income Data":

        if lendata == 0:
            st.subheader("Please add an entry before attempting to view your entries.")            

        else:

            showColsExpander = sidebar.expander("**Selected Columns**")

            with showColsExpander:
                showCols = colSelector()

            st.session_state.userdata = cleanDF(st.session_state.userdata)

            interpolationExpander = sidebar.expander("**Interpolate Missing Data**")

            with interpolationExpander:

                st.write("Interpolate data for months that were missed in the recording process. Choose the month to interpolate, and we'll predict what the values for that month could have been based on your previous and following entry.")

                intmonths = list(st.session_state.userdata["Month No."].astype(int))
                maxval = max(intmonths)
                missingmonths = []

                for num in range(1, maxval):
                    if num not in intmonths:
                        missingmonths.append(num)

                if len(missingmonths) == 0:
                    st.success("**You don't have any missing data!**")

                else:

                    targetmonth = st.selectbox("**Target Month:**", missingmonths)

                    previndex = 0
                    nextindex = 0

                    prevmonth = 1
                    nextmonth = maxval

                    newvals = {}
                    cols = [c for c in st.session_state.userdata.columns]

                    newvals["Month"] = st.selectbox("**Month**", months, index=monthindex)
                    newvals["Year"] = st.number_input("**Year**", currentyear, step=1)

                    for i in range(len(st.session_state.userdata)):

                        val = int(st.session_state.userdata.iloc[i, 0])
                        
                        if val < targetmonth:
                            previndex = i
                            prevmonth = st.session_state.userdata.iloc[previndex, 0]

                        if val > targetmonth and nextmonth != 0:
                            nextindex = i
                            nextmonth = st.session_state.userdata.iloc[nextindex, 0]

                    prevgap = targetmonth - prevmonth
                    nextgap = nextmonth - targetmonth
                    totalgap = prevgap + nextgap

                    newvals["Month No."] = targetmonth

                    for c in range(3, len(cols)):

                        if cols[c][-5:] == "(Tax)" or cols[c] == "Total Tax":

                            prevtax = float(st.session_state.userdata.iloc[previndex, c])
                            nexttax = float(st.session_state.userdata.iloc[nextindex, c])

                            if cols[c][-5:] == "(Tax)":
                                revcol = cols[c][:-5]+"(Revenue)"
                            else:
                                revcol = "Total Revenue"

                            prevrev = st.session_state.userdata.loc[previndex, revcol]
                            nextrev = st.session_state.userdata.loc[nextindex, revcol]

                            if prevrev != 0:
                                prevtaxrate = prevtax / prevrev

                            else:
                                prevtaxrate = 0

                            if nextrev != 0:
                                nexttaxrate = nexttax / nextrev
                            else:
                                nexttaxrate = 0

                            newtaxrate = prevtaxrate + ( (nexttaxrate - prevtaxrate) / totalgap * prevgap )
                            newrev = newvals[revcol]
                            newval = newvals[revcol] * newtaxrate

                        else:

                            prevval = float(st.session_state.userdata.iloc[previndex, c])
                            nextval = float(st.session_state.userdata.iloc[nextindex, c])

                            newval = prevval + ( (nextval - prevval) / totalgap * prevgap )

                        if isNum(str(newval)):
                            newval = round(newval, 2)

                        newvals[cols[c]] = newval

                    data = {}

                    for col in st.session_state.userdata:

                        data[col] = [val for val in st.session_state.userdata[col]]
                        data[col].insert(nextindex, newvals[col])
                    
                    if st.button("Add Interpolated Data"):

                        newdf = pd.DataFrame()

                        for col in data:
                            newdf[col] = data[col]

                        saveEntries(newdf, st.session_state.userid)

                        st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                        st.session_state.userdata = cleanDF(st.session_state.userdata)
                    
                        lendata = len(st.session_state.userdata)

                        st.success("Interpolated data added successfully. You may have to refresh the page for your data to update.")

            if showCols == []:
                st.subheader("Please select a column to view.")

            else:

                startentry = sidebar.number_input("Starting Entry Number", 1, lendata, value=1)-1
                endentry = sidebar.number_input("Ending Entry Number", startentry, lendata, value=lendata)
                
                displaydf = pd.DataFrame()

                displaydf["Entry No."] = [i+1 for i in range(endentry-startentry)]

                for col in showCols:
                    displaydf[col] = st.session_state.userdata[col].iloc[startentry:endentry]                    

                st.dataframe(displaydf, use_container_width=True, hide_index=True)

                if st.expander("**:red[DANGER ZONE]**").button("**:red[Clear ALL Entries]**", use_container_width=True):
                    
                    newdata = {}

                    for title in defaultcols:
                        newdata[title] = []

                    st.session_state.userdata = toDF(newdata)

                    saveEntries(st.session_state.userdata, st.session_state.userid)
                    st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                    st.session_state.userdata = cleanDF(st.session_state.userdata)

    elif page == "Edit Your Entries":

        if lendata == 0:
            st.subheader("Please add an entry before attempting to edit your entries.")

        else:

            existingrevs = []
            existingexps = []
            existingtaxes = []

            for col in st.session_state.userdata.columns:

                if "(Revenue)" == col[-9:]:
                    existingrevs.append(col)

                elif "(Expense)" == col[-9:]:
                    existingexps.append(col)

                elif "(Tax)" == col[-5:]:
                    existingtaxes.append(col)

            revenue = {}
            expenses = {}
            tax = {}

            revenuecount = sidebar.number_input("**Number of Revenue Accounts:**", step=1, value=len(existingrevs), min_value=0)
            expensecount = sidebar.number_input("**Number of Expense Accounts:**", step=1, value=len(existingexps), min_value=0)

            st.write("---")
            st.header("Time of Entry")

            c1, c2, c3 = st.columns(3)
        
            for m in range(len(months)):
                    
                if currentmonth == months[m]:
                    monthindex = m
                    break

            monthno = c1.selectbox("**Editing Entry (Month No.):**", st.session_state.userdata["Month No."], index=lendata-1)
            month = c2.selectbox("**Month**", months, index=monthindex)
            year = c3.number_input("**Year**", currentyear, step=1)

            selectedindex = -1

            for i in range(len(st.session_state.userdata["Month No."])):
                if monthno == st.session_state.userdata["Month No."][i]:
                    selectedindex = i
                    break

            if revenuecount > 0:
                
                st.write("---")
                st.header("Revenue Sources")

                c1, c2, c3 = st.columns(3)
                
                unnamedaccounts = 0

                for i in range(revenuecount):

                    accname = ""

                    if (i < len(existingrevs)):
                        accname = existingrevs[i][:-10]

                    if accname[:23] == "Unnamed Revenue Account":
                        unnamedaccounts += 1

                    name = c1.text_input(f"**Revenue Source {i+1}:**", value=accname)

                    if name == "":
                        
                        unnamedaccounts += 1
                        revenuecol = f"Unnamed Revenue Account {unnamedaccounts} (Revenue)"
                        taxcol = f"Unnamed Revenue Account {unnamedaccounts} (Tax)"

                        if revenuecol in revenue:
                            revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                        else:
                            revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                        if taxcol in tax:
                            tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                        else:
                            tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                    else:

                        revenuecol = f"{name} (Revenue)"
                        taxcol = f"{name} (Tax)"

                        if revenuecol in revenue:
                            revenue[revenuecol] += c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)
                        else:
                            revenue[revenuecol] = c2.number_input(f"**Revenue Amount {i+1} ($):**", step=0.01, min_value=0.)

                        if taxcol in tax:
                            tax[taxcol] += revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01
                        else:
                            tax[taxcol] = revenue[revenuecol] * c3.number_input(f"**Tax Percent {i+1} (%):**", step=0.01, min_value=0.) * 0.01

                    revenue[revenuecol] = round(revenue[revenuecol], 2)
                    tax[taxcol] = round(tax[taxcol], 2)

            if expensecount > 0:
                
                st.write("---")
                st.header("Expenses")

                c1, c2 = st.columns(2)

                unnamedaccounts = 0

                for i in range(expensecount):

                    accname = ""
                    initialamt = 0.

                    if (i < len(existingexps)):
                        accname = existingexps[i][:-10]
                        initialamt = st.session_state.userdata[existingexps[i]][selectedindex]

                    name = c1.text_input(f"**Expense {i+1}:**", value=accname)

                    if accname[:23] == "Unnamed Expense Account":
                        unnamedaccounts += 1

                    if name == "":
                        unnamedaccounts += 1
                        expensecol = f"Unnamed Expense Account {unnamedaccounts} (Expense)"

                    else:
                        expensecol = f"{name} (Expense)"

                    if expensecol in expenses:
                        expenses[expensecol] += c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=initialamt)

                    else:
                        expenses[expensecol] = c2.number_input(f"**Expense Amount {i+1} ($):**", step=0.01, min_value=initialamt)

                    expenses[expensecol] = round(expenses[expensecol], 2)


            totalrevenue = sum(revenue.values())
            totalexpenses = sum(expenses.values())
            totaltax = sum(tax.values())

            c1, c2, c3 = st.columns(3)

            netincome = totalrevenue - totalexpenses - totaltax


            revenuestr = f"{round(totalrevenue, 2)}"

            if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                revenuestr += "0"

            if (totalrevenue == 0):
                revenuestr = f"(0.00)"

            expensestr = f"{round(totalexpenses, 2)}"

            if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                expensestr += "0"

            if (totalexpenses == 0):
                expensestr = f"0.00"        


            taxstr = f"{round(totaltax, 2)}"

            if (len(taxstr.split(".")[1]) == 1):
                taxstr += "0"

            if (totaltax == 0):
                taxstr = f"0.00"        


            netincomestr = f"{np.abs(round(netincome, 2))}"

            if ("." in netincomestr and len(netincomestr.split(".")[1]) == 1):
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

            for revenueacc, taxacc in zip(revenue.keys(), tax.keys()):

                totalvals[revenueacc] = [revenue[revenueacc]]
                totalvals[taxacc] = [tax[taxacc]]

                revenuestr = f"{round(revenue[revenueacc], 2)}"

                if ("." in revenuestr and len(revenuestr.split(".")[1]) == 1):
                    revenuestr += "0"

                if (totalrevenue == 0):
                    revenuestr = f"(0.00)"

                taxstr = f"{round(tax[taxacc], 2)}"

                if ("." in taxstr and len(taxstr.split(".")[1]) == 1):
                    taxstr += "0"

                if (tax[taxacc] == 0):
                    taxstr = f"0.00"
                
                totalvalsstr[revenueacc] = [f"$ {revenuestr}"]
                totalvalsstr[taxacc] = [f"$ ({taxstr})"]

            for acc in expenses:

                expensestr = f"{round(expenses[acc], 2)}"

                if ("." in expensestr and len(expensestr.split(".")[1]) == 1):
                    expensestr += "0"

                if (expenses[acc] == 0):
                    expensestr = f"0.00"

                totalvals[acc] = [expenses[acc]]
                totalvalsstr[acc] = [f"$ ({expensestr})"]

            totalvalsstr = pd.DataFrame().from_dict(totalvalsstr)

            st.write("---")
            st.header("Before:")

            #FIX

            st.dataframe(st.session_state.userdata[st.session_state.userdata.columns][selectedindex], hide_index=True, use_container_width=True)
            st.header("After:")
            st.dataframe(totalvalsstr, hide_index=True, use_container_width=True)

            if sidebar.button("Save Entry"):
                    
                try:
                
                    data = {}

                    for col in st.session_state.userdata.columns:

                        data[col] = []

                        for val in st.session_state.userdata[col]:
                            data[col].append(val)

                    for acc in totalvals:
                            
                        if acc not in data:
                            if len(data["Month No."]) > 1:
                                data[acc] = [0 for i in range(len(data["Month No."])-1)]
                            else:
                                data[acc] = []
                    
                        data[acc][selectedindex] = totalvals[acc][0]

                    data = cleanData(data)
                    newdf = pd.DataFrame().from_dict(data)
                    saveEntries(newdf, st.session_state.userid)

                    st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                    st.session_state.userdata = cleanDF(st.session_state.userdata)

                    st.success(f"\nSaved the entry successfully.")

                except:
                    st.error(f"\nERROR: Entry could not be saved for User {st.session_state.userid}.")

    elif page == "Analyze Your Data":

        st.write("Here, you can generate **graphs**, make **predictions**, view **trends**, and look at your data **as a whole**. Before you begin, it's **highly recommended** that you ensure there is **no missing data**, or any missing data has been **interpolated** on the **Your Income Data** page. To get started, just select what you want to do **below**:")

        userchoice = st.radio("**What do you want to do?**", ["Generate Graphs", "Predict Data"])
        layout = st.radio("**Viewing Layout:**", ["Vertical", "Horizontal"])

        st.write("---")
        
        if lendata > 1:

            if layout == "Vertical":

                c1 = False
                c2 = False

            else:

                c1, c2, c3 = st.columns([10, 80, 10])

                c2.subheader("Divider Position (% towards the right side of the screen)")
                divamount = c2.slider("Divider Position", min_value=10, max_value=90, value=50, label_visibility="collapsed")

                if divamount < 10:
                    divamount = 10

                if divamount > 90:
                    divamount = 90

                st.write("---")

                c1, c2 = st.columns([divamount, 100-divamount])

            showColsExpander = sidebar.expander("**Dataset Columns to Show**")

            with showColsExpander:
                showCols = colSelector()

            displaydata = pd.DataFrame()
            displaydata["Entry No."] = [i+1 for i in range(len(st.session_state.userdata["Month No."]))]

            for col in showCols:
                displaydata[col] = st.session_state.userdata[col]

            if c1:
                c1.header("Your Data")
                c1.dataframe(displaydata, use_container_width=True, hide_index=True)
            else:
                st.header("Your Data")
                st.dataframe(st.session_state.userdata[showCols], use_container_width=True, hide_index=True)                
        
            ycols = [col for col in st.session_state.userdata.columns if col not in defaultcols[:3]]

            if userchoice == "Generate Graphs":

                if len(ycols) < 10:
                    maxcols = len(ycols)
                else:
                    maxcols = 10

                gtypes = ["Scatter Plot", "Line Plot", "Linear Regression Plot", "Bar Plot"]
                graphsettings = sidebar.expander("**Graph Settings**")

                with graphsettings:

                    darkbg = st.checkbox("Graph Dark Mode", value=True)
                    predictdata = st.checkbox("Graph Predicted Data", value=False)

                    if darkbg:
                        plt.style.use("dark_background")
                    else:
                        plt.style.use("classic")

                    gtype = st.selectbox("**Graph Type:**", gtypes)
                    numcols = st.number_input("**Number of Columns to Plot:**", min_value=1, max_value=maxcols)

                    startentry = st.number_input("**Starting Entry to Plot:**", min_value=1, max_value=lendata-1)
                    endentry = st.number_input("**Ending Entry to Plot:**", min_value=startentry, max_value=lendata, value=lendata)

                plt.xlabel("Month No.")
                plt.ylabel(f"Amount ($)")

                selectedcols = []
                predmonths = 0

                x = st.session_state.userdata["Month No."][startentry-1:endentry]
                y = st.session_state.userdata[ycols].iloc[startentry-1:endentry]

                if predictdata and len(ycols) == 0:
                    st.subheader("Please add accounts to your entries to predict account data.")

                elif predictdata:
                    
                    predmonthamount = graphsettings.number_input("**Number of Months to Predict:**", min_value=1, step=1, max_value=12)
                    predmonths = [i+1+endentry for i in range(predmonthamount)]

                    preddict = predict(st.session_state.userdata, predmonths, startentry, endentry)
                    preddf = toDF(preddict)


                    if c1:
                        c1.subheader("Predicted Data")
                        c1.dataframe(preddf[[col for col in preddf.columns if col not in defaultcols[1:3]]], use_container_width=True, hide_index=True)

                    else:
                        st.subheader("Predicted Data")
                        st.dataframe(preddf[[col for col in preddf.columns if col not in defaultcols[1:3]]], use_container_width=True, hide_index=True)

                                                    
                    data = {}

                    for col in st.session_state.userdata.columns:

                        data[col] = []

                        for val in st.session_state.userdata[col]:
                            data[col].append(val)

                        for val in preddict[col]:

                            if isNum(val):
                                newval = round(val, 2)
                            else:
                                newval = val

                            data[col].append(newval)


                    data = cleanData(data)
                    y = pd.DataFrame().from_dict(data)

                    endentry += predmonthamount
                    x = y["Month No."].iloc[startentry-1:endentry]

                plotcols = sidebar.expander("**Columns to :green[Plot]**")

                fig, ax = plt.subplots()
                ax.set_xticks(np.arange(0, np.max(x)+1, 1))

                for i in range(numcols):

                    selectedcol = plotcols.selectbox(f"**Column {i+1}:**", [col for col in ycols if col not in selectedcols and col not in defaultcols[:3]])
                    ycol = y[selectedcol].iloc[startentry-1:endentry]

                    selectedcols.append(selectedcol)

                    if gtype == "Scatter Plot":
                        sn.scatterplot(x=x, y=ycol)

                    elif gtype == "Line Plot":
                        sn.lineplot(x=x, y=ycol)

                    elif gtype == "Linear Regression Plot":
                        sn.regplot(x=x, y=ycol)

                    elif gtype == "Bar Plot":
                        sn.barplot(x=x, y=ycol)
                
                if c2:
                    c2.header("Graph Display")
                    c2.pyplot(fig)
                else:
                    st.header("Graph Display")
                    st.pyplot(fig)

            else:
                
                if len(ycols) == 0:
                    st.subheader("Please add accounts to your entries to predict account data.")

                else:

                    predsettings = sidebar.expander("**Prediction Settings:**", expanded=True)
                    startentry = predsettings.number_input("**Starting Entry to Use For Prediction:**", min_value=1, max_value=len(displaydata["Entry No."])-1, step=1)
                    endentry = predsettings.number_input("**Ending Entry to Use For Prediction:**", min_value=startentry+1, max_value=len(displaydata["Entry No."]), value=len(displaydata["Entry No."]), step=1)
                    predmonth = predsettings.number_input("**Month to Predict:**", min_value=st.session_state.userdata["Month No."].iloc[-1]+1, step=1)

                    preddict = predict(st.session_state.userdata, [predmonth], startentry, endentry)
                    preddf = toDF(preddict)

                    if c2:
                        c2.header("Data Prediction")
                        c2.dataframe(preddf, use_container_width=True, hide_index=True)

                    else:
                        st.header("Data Prediction")
                        st.dataframe(preddf, use_container_width=True, hide_index=True)

                    if sidebar.button("Add Predicted Entry"):
                            
                        try:
                        
                            data = {}

                            for col in st.session_state.userdata.columns:

                                data[col] = []

                                for val in st.session_state.userdata[col]:
                                    data[col].append(val)

                                if isNum(preddict[col][0]):
                                    newval = round(preddict[col][0], 2)
                                else:
                                    newval = preddict[col][0]

                                data[col].append(newval)


                            data = cleanData(data)
                            newdf = pd.DataFrame().from_dict(data)
                            saveEntries(newdf, st.session_state.userid)

                            print(f"\nEntry created sucessfully for User {st.session_state.userid}.")

                        except:
                            print(f"\nERROR: Entry could not be created for User {st.session_state.userid}.")

                        st.session_state.userdata = pd.read_csv(f"data_{st.session_state.userid}.csv")
                        st.session_state.userdata = cleanDF(st.session_state.userdata)

                        sidebar.success("Entry created successfully.")


        else:
            st.subheader("Please enter more than one entry to analyze your data.")

    elif page == "Plan Your Budget":
        
        st.write("Here, you can create your **own** budget plan for **each month**. To get started, start entering values, or just **upload** your current budget file to pick up where you left off. It is highly recommended to include **all** fixed-value accounts (accounts with values remain unchanged between months) - as well as any variable accounts (accounts with changing values) - in your plan for the most **accurate** budget planning.")
        st.write(":grey[**Note: You may only use accounts that are present in your income data.**]")

        if lendata > 0 and list(st.session_state.userdata.keys()) != defaultcols:
        
            budgetfileuploadexp = sidebar.expander("**:green[Upload] Your Budgeting File**")
            datafile = budgetfileuploadexp.file_uploader("**Upload your budget file below:**", accept_multiple_files=False, type=["csv"])

            if datafile:
                
                try:
                    
                    if budgetfileuploadexp.button("Upload File"):

                        budgetdf = pd.read_csv(datafile)

                        if list(budgetdf.columns) == ["Account", "Subaccount", "Amount ($)"]:
                            
                            validdata = True
                            
                            st.session_state.budgetdata = {}
                            
                            for col in budgetdf.columns:

                                st.session_state.budgetdata[col] = list(budgetdf[col])

                                if col in "Amount ($)":

                                    for val in st.session_state.budgetdata[col]:
                                        
                                        if not isNum(val):
                                            validdata = False
                                            break

                                
                            if validdata:
                                st.session_state.uploadedbudgetfile = True
                                budgetfileuploadexp.success("Your budget file was uploaded successfully!")
                            
                            else:
                                budgetfileuploadexp.error("Please upload a valid budget file - all amount values must be numerical.")

                        else:
                            budgetfileuploadexp.error("Please upload a valid budget file - the file should only have the columns \"Account\", \"Subaccount\" and \"Amount ($)\".")

                except:
                    st.error("There was an issue in uploading your file. Please try again.")

            else:
                st.session_state.uploadedbudgetfile = False

            sidebar.header("Settings:")

            monthnos = list(st.session_state.userdata["Month No."])
            monthno = sidebar.number_input("**Month Number:**", step=1, min_value=max(monthnos)+1)

            if st.session_state.uploadedbudgetfile:
                suggestvalues = False
            else:
                suggestvalues = sidebar.checkbox("**Suggest Budget Values**", value=True)

            revaccounts = []
            taxaccounts = []
            expaccounts = []

            for col in st.session_state.userdata.columns:

                if "(Revenue)" == col[-9:]:
                    revaccounts.append(col)

                elif "(Tax)" == col[-5:]:
                    taxaccounts.append(col)

                elif "(Expense)" == col[-9:]:
                    expaccounts.append(col)

            accselectionex = sidebar.expander("**Selected Accounts**")
            selectedrevaccs = []
            selectedexpaccs = []

            if len(revaccounts) > 0:
    
                accselectionex.subheader("Revenue/Tax Accounts")
    
                for revacc in revaccounts:

                    if accselectionex.checkbox(revacc[:-10], True):

                        selectedrevaccs.append(revacc)

            if len(expaccounts) > 0:
    
                accselectionex.subheader("Expense Accounts")
    
                for expacc in expaccounts:
                    
                    if accselectionex.checkbox(expacc[:-10], True):
                        selectedexpaccs.append(expacc)

            subaccnumex = sidebar.expander("**Number of Subaccounts**")

            budgetdata = {}
            budgetdata["Account"] = []
            budgetdata["Subaccount"] = []
            budgetdata["Amount ($)"] = []

            if suggestvalues:
                recommendedvals = predict(st.session_state.userdata, [max(st.session_state.userdata["Month No."])+1], 1, len(st.session_state.userdata))

            if len(selectedrevaccs) > 0:

                st.write("---")
                st.header("Revenue/Tax Accounts")
                st.write("---")

                subaccnumex.header("Revenue/Tax Accounts")

                for revaccname in revaccounts:

                    existingsubaccs = []
                    existingsubamts = []
                    existingsubtax = []
                    subaccindices = []
                    taxaccname = revaccname[:-9]+"(Tax)"
                    
                    if revaccname in selectedrevaccs:

                        initialsubaccnum = 1

                        st.subheader(revaccname[:-10])

                        if st.session_state.uploadedbudgetfile:
                                
                            initialsubaccnum = 0
                            
                            for i in range(len(st.session_state.budgetdata["Account"])):
                                
                                if revaccname[:-10] == st.session_state.budgetdata["Account"][i] and st.session_state.budgetdata["Subaccount"][i][-9:] == "(Revenue)":
                                    
                                    initialsubaccnum += 1
                                    subaccindices.append(i)
                                    existingsubaccs.append(revaccname[:-10])
                                    existingsubamts.append(st.session_state.budgetdata["Amount ($)"][i])

                                    if (i+1 < len(st.session_state.budgetdata["Account"]) and st.session_state.budgetdata["Subaccount"][i+1][-5:] == "(Tax)"):

                                        if st.session_state.budgetdata["Amount ($)"][i] != 0:
                                            existingsubtax.append(st.session_state.budgetdata["Amount ($)"][i+1] / st.session_state.budgetdata["Amount ($)"][i] * 100)
                                        else:
                                            existingsubtax.append(0)                                            

                                    else:
                                        existingsubtax.append(0)


                        subaccnum = subaccnumex.number_input("**"+revaccname[:-10]+"**:", step=1, min_value=1, value=initialsubaccnum)

                        for i in range(subaccnum):
    
                            c1, c2, c3 = st.columns(3)

                            initialsubaccname = f"Unnamed Subaccount {i+1}"

                            initialamt = 0.
                            initialtax = 0.

                            if i < len(existingsubaccs):
                                initialsubaccname = existingsubaccs[i]
                                initialamt = existingsubamts[i]
                                initialtax = existingsubtax[i]

                            elif suggestvalues and revaccname in recommendedvals:
                                
                                initialsubaccname = "Total"
                                initialamt = recommendedvals[revaccname][0]

                                if initialamt > 0 and taxaccname in recommendedvals:
                                    initialtax = recommendedvals[taxaccname][0] / initialamt * 100
                                else:
                                    initialtax = 0.

                                if not isNum(initialamt):
                                    initialamt = 0.

                                if not isNum(initialtax):
                                    initialtax = 0.

                            subaccname = c1.text_input(f"**{revaccname[:-10]} - Subaccount {i+1}:**", value=initialsubaccname)
                            subaccamt = c2.number_input(f"**{revaccname[:-10]} - Amount {i+1} ($):**", min_value=0., value=initialamt)
                            subacctax = c3.number_input(f"**{revaccname[:-10]} - Tax Percent {i+1} (%):**", min_value=0., value=initialtax)


                            budgetdata["Account"].append(revaccname[:-10])
                            budgetdata["Subaccount"].append(subaccname+" (Revenue)")
                            budgetdata["Amount ($)"].append(subaccamt)

                            budgetdata["Account"].append(revaccname[:-10])
                            budgetdata["Subaccount"].append(subaccname+" (Tax)")
                            budgetdata["Amount ($)"].append(subaccamt*subacctax/100)
                    

            if len(selectedexpaccs) > 0:

                if len(selectedexpaccs) > 0:
                    subaccnumex.write("---")

                st.write("---")
                st.header("Expense Accounts")
                st.write("---")

                subaccnumex.header("Expense Accounts")

                for expaccname in expaccounts:
                    
                    existingsubaccs = []
                    existingsubamts = []
                    subaccindices = []
                    
                    if expaccname in selectedexpaccs:

                        initialsubaccnum = 1

                        st.subheader(expaccname[:-10])

                        if st.session_state.uploadedbudgetfile:
                                
                            initialsubaccnum = 0
                            
                            for i in range(len(st.session_state.budgetdata["Account"])):
                                
                                if expaccname[:-10] == st.session_state.budgetdata["Account"][i] and st.session_state.budgetdata["Subaccount"][i][-9:] == "(Expense)":
                                    
                                    initialsubaccnum += 1
                                    subaccindices.append(i)
                                    existingsubaccs.append(expaccname[:-10])
                                    existingsubamts.append(st.session_state.budgetdata["Amount ($)"][i])


                        subaccnum = subaccnumex.number_input("**"+expaccname[:-10]+"**:", step=1, min_value=1, value=initialsubaccnum)

                        for i in range(subaccnum):
    
                            c1, c2 = st.columns(2)

                            initialsubaccname = f"Unnamed Subaccount {i+1}"

                            initialamt = 0.

                            if i < len(existingsubaccs):
                                initialsubaccname = existingsubaccs[i]
                                initialamt = existingsubamts[i]
                            
                            elif suggestvalues and expaccname in recommendedvals:
                                
                                initialsubaccname = "Total"
                                initialamt = recommendedvals[expaccname][0]

                                if not isNum(initialamt):
                                    initialamt = 0

                            subaccname = c1.text_input(f"**{expaccname[:-10]} - Subaccount {i+1}:**", value=initialsubaccname)
                            subaccamt = c2.number_input(f"**{expaccname[:-10]} - Amount {i+1} ($):**", min_value=0., value=initialamt)

                            budgetdata["Account"].append(expaccname[:-10])
                            budgetdata["Subaccount"].append(subaccname+" (Expense)")
                            budgetdata["Amount ($)"].append(subaccamt)
                    
            
            budgetdf = pd.DataFrame().from_dict(budgetdata)
 
            st.write("---")
            st.dataframe(budgetdf, use_container_width=True, hide_index=True)
            
            download = sidebar.download_button("**:green[Download] Budget File**", budgetdf.to_csv(index=False), file_name="budget.csv")

        else:
            st.subheader("Please add at least one entry (with at least one account) to budget with your accounts.")