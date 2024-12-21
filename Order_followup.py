# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.title('Daily Patient Pull Through Email Follow-up')
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
#         * email id

# show orders needing follow up
#     filter to user so only relavent orders show
#     filter to orders that havent had email in x days
#     sort by urgency, days on list
session = get_active_session()

query = session.sql("""select top 20 
                        max(e.send_date) as "Last Email Date", 
                        ord.order_number, 
                        ord.order_test_type_id_mrd,
                        ord.orderdimkey,
                        ord.order_mrn,
                        ord.order_created_by
                        from modeled_dev.edm.order_dim ord
                        join modeled_dev.edm.order_fact orf on orf.orderdimkey = ord.orderdimkey
                        join modeled_dev.edm.provider_dim pd on pd.providerdimkey = orf.providerdimkey
                        join modeled_dev.edm.patient_dim p on p.patientdimkey = orf.patientdimkey
                        join modeled_dev.edm.account_dim a on a.accountdimkey = orf.accountdimkey
                        join AI_SANDBOX.PUBLIC.ORDER_EMAIL_FOLLOW_UP e on e.email_subject = ord.order_number
                        where ord.order_classification = 'clonoSEQ - Clinical Testing'
                        group by ord.order_number, 
                        ord.order_test_type_id_mrd,
                        ord.orderdimkey,
                        ord.order_mrn,
                        ord.order_created_by;""")

df = query.to_pandas()
# st.dataframe(df)

# allow user to select order 
column_configuration = {
    "name": st.column_config.TextColumn(
        "Name", help="This is the help thing", max_chars=100, width = 'medium'
    )
}

select, email = st.tabs(['Select Orders', 'Email Provider'])

with select:
    st.header("All Orders")

    event = st.dataframe(
        df,
        on_select= 'rerun',
        selection_mode='single-row'
    )
    order_to_follow_up_row = event.selection.rows
    order_to_follow_up = df.iloc[order_to_follow_up_row].reset_index()
    

try:
    order_number = order_to_follow_up['ORDER_NUMBER'][0]
    if order_number:
        # show draft of email in window
        #      allow option to add orders with same follow-up amd same doc
        email_display_text = f"""Hello,\n\nWe regret to inform you that the ID Clonality test below is ployclonal, meaning no dominant sequences were identifited despite adequate speciment and quality control measures. 
        Unfortunately MRD Tracking test cannot be completed if no dominant sequences are identified for tracking.
        \n\nOrder: {order_number}
        \nTrial: Dana Farber Cancer Institute - 21-040
        \nSubject: SCR_047
        \n\nThe ID Clonality test can be re-tested with an alternate sample from a different collection date with disease burden of 5% or greater.
        Please advise as to whether you are able to send an alternate sample.
        A new ID Clonality test order will be required for the alternate sample.
        \n\nIf no alternate sample is available, we will cancel any pending MRD Tracking order(s) and return or discard the sample at your request.
        If there are pending MRD Tracking tests for this patient, please let us know how you wish to procede."""
    
        st.write(email_display_text)
        # clicking send sends email to doc
        #     writes to email table
        #     writes to order to email table
        #     removes order from current view

        # covert to url friendly version
        email_text = email_display_text.replace('\n', '%0D%0A%0D%0A')
        email_text = email_text.replace('\t','')
        email_insert_stmt = f"""insert into AI_SANDBOX.PUBLIC.ORDER_EMAIL_FOLLOW_UP
    (send_date, email_subject, recipient, follow_up_reason) values (current_timestamp, '"""+ order_number +"""', 'aoldre@adaptivebiotech', 'polyclonal id');"""
        
        email_url = """mailto: aoldre@adaptivebiotech.com; ?subject=ID was Unsuccessful, New ID Order Needed
        &body="""+email_text+"""https://app.snowflake.com/adaptivebiotech/corp/#/streamlit-apps/MODELED_DEV.ANALYSTSANDBOX.SGROKH9NUO7THOYL?ref=snowsight_shared"""
        
        # opens the email in outlook, but doesn't pass T/F to success and automatically writes to DB
        st.link_button('Open Outlook',email_url)
            
            #session.sql(email_insert_stmt).collect()
            
        
        # does not open url, but doesn't write to DB until pressed
        if st.button('Record Email in DB '):
            
            session.sql(email_insert_stmt).collect()
            st.success(f"Your Email was recorded",  icon="✅")


except KeyError:
    st.write('Select Order to Follow-Up')
