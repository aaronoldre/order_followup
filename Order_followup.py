import streamlit as st
import pandas as pd


# snowflake tables needed
#     mrd follow-up view
#         * order number
#         * reason for follow up
#         * last email date
#         * orderdimkey
#         * patient mrn
#         * previous order info
#         * created by email
#         * order test type
#         * order icd group
#         * spec arrv dt
#         * path activity 
#         * pr notes
#     email tracker
#         * id
#         * subject
#         * senddate
#         * recipient 
#     order to email
#         * orderdimkey
#          * email id

# show orders needing follow up
#     filter to user so only relavent orders show
#     filter to orders that havent had email in x days
#     sort by urgency, days on list

# allow user to select order 

# show draft of email in window
#      allow option to add orders with same follow-up amd same doc

# clicking send sends email to doc
#     writes to email table
#     writes to order to email table
#     removes order from current view
