#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

#########################
### Data Preparation ###
########################

# Read in data (DeviceCGM takes about 15 seconds)
DeviceCGM = pd.read_table("./study data/DeviceCGM.txt", encoding = 'UTF-16', sep = "|", parse_dates=['DeviceDtTm'])
VisitInfo = pd.read_table("./study data/VisitInfo.txt", encoding = 'UTF-16', sep = "|", parse_dates=['VisitDt'])
PtRoster = pd.read_table("./study data/PtRoster.txt", encoding = 'UTF-16', sep = "|")

# Makes dates usable in date format
DeviceCGM = DeviceCGM.query("RecordType == 'CGM'")
DeviceCGM['DeviceDtTm'] = DeviceCGM['DeviceDtTm'].dt.date
DeviceCGM = DeviceCGM[['PtID', 'DeviceDtTm']]

VisitInfo['VisitDt'] = VisitInfo['VisitDt'].dt.date

# Minimize datasets to only what we need, for simplicity (e.g. CGM patients only, 4/8/16/26-week visits only)
patients_CGM = PtRoster.query("TrtGroup == 'CGM'")['PtID']

patient_visit_dates = (VisitInfo
    .query("PtID in @patients_CGM")
    .query("Visit in ['4 week','8 week','16 week','26 week']")
    .sort_values(by = ['PtID'])[['PtID', 'Visit', 'VisitDt']]
)

DeviceCGM_min = DeviceCGM.query("PtID in @patients_CGM")

# Widen patient follow-up visit dates
patient_visit_dates_wide = (patient_visit_dates
    .pivot(index = 'PtID', columns = ['Visit'], values = ['VisitDt'])
    .reset_index('PtID')
)

patient_visit_dates_wide.columns = ['PtID', 'wk16', 'wk26', 'wk4', 'wk8']
patient_visit_dates_wide = patient_visit_dates_wide[['PtID', 'wk4', 'wk8', 'wk16', 'wk26']]

##############################
### Adherence Calculations ###
##############################

# Join visit dates onto each row of DeviceCGM data
DeviceCGM_min_visits = DeviceCGM_min.merge(patient_visit_dates_wide, on = 'PtID', how = 'left')

# If the date of the reading falls within 28 days of the wk X visit date, mark `wkX_check` as TRUE for that reading
DeviceCGM_min_visits['wk4_check'] = (DeviceCGM_min_visits['DeviceDtTm'] - DeviceCGM_min_visits['wk4']).dt.days.between(-28, -1)
DeviceCGM_min_visits['wk8_check'] = (DeviceCGM_min_visits['DeviceDtTm'] - DeviceCGM_min_visits['wk8']).dt.days.between(-28, -1)
DeviceCGM_min_visits['wk16_check'] = (DeviceCGM_min_visits['DeviceDtTm'] - DeviceCGM_min_visits['wk16']).dt.days.between(-28, -1)
DeviceCGM_min_visits['wk26_check'] = (DeviceCGM_min_visits['DeviceDtTm'] - DeviceCGM_min_visits['wk26']).dt.days.between(-28, -1)

# Calculation of visit-specific adherence
    # Count # of distinct dates with a CGM reading, per patient, that fall within the 28-day period before each f/u visit)

wk4_CGMdays_unique = (DeviceCGM_min_visits.query("wk4_check == True") # Sum only dates in 28-day window before f/u visit
    .groupby('PtID', as_index = False)
    .agg(days_adherent_perc = ('DeviceDtTm', lambda x: x.nunique() / 28))
)

wk8_CGMdays_unique = (DeviceCGM_min_visits.query("wk8_check == True")
    .groupby('PtID', as_index = False)
    .agg(days_adherent_perc = ('DeviceDtTm', lambda x: x.nunique() / 28))
)

wk16_CGMdays_unique = (DeviceCGM_min_visits.query("wk16_check == True")
    .groupby('PtID', as_index = False)
    .agg(days_adherent_perc = ('DeviceDtTm', lambda x: x.nunique() / 28))
)

wk26_CGMdays_unique = (DeviceCGM_min_visits.query("wk26_check == True")
    .groupby('PtID', as_index = False)
    .agg(days_adherent_perc = ('DeviceDtTm', lambda x: x.nunique() / 28))
)

# Join columns for each visit
CGMdays_unique_perc = (wk4_CGMdays_unique
    .merge(wk8_CGMdays_unique, on = 'PtID', how = 'outer')
    .merge(wk16_CGMdays_unique, on = 'PtID', how = 'outer')
    .merge(wk26_CGMdays_unique, on = 'PtID', how = 'outer')
    .sort_values(by = 'PtID')
)
CGMdays_unique_perc.columns = ["PtID", "wk4_adherence", "wk8_adherence", "wk16_adherence", "wk26_adherence"]

# Where nan in CGMdays_unique_perc, here is the breakdown:
  # PtIDs 156, 28, 65, and 134 legitimately had 0 days of adherence where it says nan (switch to 0)
  # PtIDs 31, 182 and 68 are actually missing a visit date, so no way of calculating adherence there (keep as nan)
# This was inspected informally with the following code:
  # sorted((DeviceCGM_min_visits.query("PtID == 68"))['DeviceDtTm'].unique())
  # patient_visit_dates.query("PtID == 68")
    
CGMdays_unique_perc.loc[CGMdays_unique_perc['PtID'] == 156, 'wk8_adherence'] = 0
CGMdays_unique_perc.loc[CGMdays_unique_perc['PtID'] == 28, 'wk26_adherence'] = 0
CGMdays_unique_perc.loc[CGMdays_unique_perc['PtID'] == 65, 'wk26_adherence'] = 0
CGMdays_unique_perc.loc[CGMdays_unique_perc['PtID'] == 134, 'wk26_adherence'] = 0
CGMdays_unique_perc.loc[CGMdays_unique_perc['PtID'] == 134, 'wk8_adherence'] = 0

# Calculate Final Average Adherence
CGMdays_unique_perc = (CGMdays_unique_perc
    .assign(final_adherence = CGMdays_unique_perc[['wk4_adherence', 'wk8_adherence', 'wk16_adherence', 'wk26_adherence']]
            .mean(axis = 1, skipna = True))
)

# Overall CGM Adherence Calculations to CSV
CGMdays_unique_perc.to_csv('Adherence-py.csv', index = False)