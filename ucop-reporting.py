# ====================================================================
# ucop-reporting.py
# --------------------------------------------------------------------
#
# Produces a summary of RDS interactions with researchers over the
# last year in the form of a CSV file, for the purpose of UCOP
# reporting.
#
# The output, written to standard output, is a CSV file with columns:
#
#     Issue
#         Jira issue key, just for debugging/followup
#     Date
#         Ticket creation date
#     Type
#         Consultation, Curation, etc.
#     Requestor
#         Or depositor in the case of dataset curation
#     Position
#         Faculty, Staff, etc.
#     Affiliation
#         Primary department
#     Description
#         Often just the initial inquiry email received
#
# Prior to running this script, in Jira execute the following JQL
# query:
#
#     project = RDS
#     AND
#     issuetype IN (Consultation, Curation, "Education / Training", Engagement)
#     AND
#     created >= -52w
#
# (This query is saved in Jira as filter "RDS Interactions Last
# Year".)  Export the results as a CSV file.  Then run this script on
# that CSV file:
#
#     python ucop-reporting.py jira-output.csv
#
# The new CSV file is written to standard output.
#
# This script requires Pandas and the Python requests library.
#
# --------------------------------------------------------------------

import pandas as pd
import requests
import sys

# The only fields we care about, in the desired order, paired with new
# names for them.

fields = [
    ("Issue key", "Issue"),
    ("Created", "Date"),
    ("Issue Type", "Type"),
    ("Custom field (Requestor)", "Requestor"),
    ("Custom field (Depositor Name)", "Depositor"),
    ("Custom field (Position)", "Position"),
    ("Custom field (Affiliation)", "Affiliation"),
    ("Description", "Description"),
    ("Custom field (Dataset Name)", "Dataset")
]

df = pd.read_csv(sys.argv[1])
df = df[(f[0] for f in fields)].rename(columns=dict(fields)).set_index("Issue")
df.Date = pd.to_datetime(df.Date).apply(lambda d: d.date())
df.Requestor = df.Requestor.combine_first(df.Depositor)
df.loc[df.Type == "Curation", "Description"] = df.Dataset
df.drop(["Depositor", "Dataset"], axis=1, inplace=True)
df.to_csv(sys.stdout)
