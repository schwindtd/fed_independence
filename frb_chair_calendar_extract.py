#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:45:51 2023

@author: danielschwindt
"""

# Import packages
import os
import glob
import tabula as tb
import pandas as pd
import re
import calendar
from PyPDF2 import PdfFileReader

# Set working directory
wd = "/Users/danielschwindt/Documents/research_projects/fed_independence/raw_schedules"
sub_dirs = 'powell'
os.chdir("/".join([wd, sub_dirs]))

# List of PDF files to process
pattern = r"powell_\d{4}\.pdf"
pdf_files = []

# Iterate over files in the working directory
for filename in os.listdir():
    if re.match(pattern, filename):
        pdf_files.append(filename)
pdf_files.sort()
# Pre-create day and month names for text search
month_names = list(calendar.month_name)[1:]  # Exclude the empty first element
day_names = list(calendar.day_name)

schedule = pd.DataFrame()
# Loop over PDF files
for pdf_file in pdf_files:
    reader = PdfFileReader(open(pdf_file, 'rb'))
    pdf_page_count = len(reader.pages)
    year = pdf_file.split("_")[1].split(".")[0]
    # Loop over PDF file pages
    df = pd.DataFrame()
    for page in range(1,pdf_page_count+1):
        try:
            # Extract data into data table
            data = tb.read_pdf(pdf_file, pages = str(page), area = (75, 0, 800, 800),
                               columns=[200,750], pandas_options={'header': None},
                               stream=True)[0]
            # Drop rows with all NAN
            data.dropna(how="all", inplace=True)
        except:
            pass
        df = pd.concat([df, data], ignore_index=True)
        
    # Create indicator variable for new day entries
    # Correct occasional issues with wrong punctuation in day entries
    pattern = r'(\b[A-Za-z]+\s+\d+)\.\s+([A-Za-z]+\b)|(\b[A-Za-z]+\s+\d+)\.\s+(\d{4}\b)'
    df[0] = df[0].str.replace(pattern, lambda m: f'{m.group(1) or m.group(3)}, {m.group(2) or m.group(4)}')
    # New days in the calendar are indicated by headers in format: "January 25, Tuesday"
    day_pattern = r"^\b({}) \d{{1,2}}*".format("|".join(month_names))
    # Create dummy variable for rows matching above pattern --- rows will become borders
    df['day_border'] = df.apply(lambda x: 1 if re.findall(day_pattern,
                                                          str(x[0])) else 0, axis=1)
    df['day_id'] = df['day_border'].transform('cumsum')
    
    # Create indicator variable for new meeting entries
    mtg_pattern = r"^\d{1,2}:\d{2}\s*[AaPp]\.?[Mm]\.?|^All Day"
    # Create dummy variable for rows matching above pattern --- rows will become borders
    df['mtg_border'] = df.apply(lambda x: 1 if re.findall(mtg_pattern,
                                                          str(x[0])) else 0, axis=1)
    df['meeting_id'] = df['mtg_border'].transform('cumsum')
    
    # Separate days into different data set
    days = df[df['day_border'] == 1][[0, 'day_id']]
    days[['date', 'day_of_week']] = days[0].str.split(',', n=1, expand=True)
    days['date'] = days['date'] + ', ' + year
    
    # Convert the 'Date' column to datetime format
    days['date'] = pd.to_datetime(days['date'], format='%B %d, %Y')
    
    # Drop initial column
    days = days.drop(0,axis=1)
    days = days[['date', 'day_id', 'day_of_week']]
    
    # Clean meetings dataset
    meetings = df.query('day_border==0')
    meetings = meetings.rename(columns={0: 'time',1: 'meeting'})
    
    # Combine split rows for meeting variable
    meetings['split_meeting'] = (meetings['meeting_id'] == \
                                 meetings['meeting_id'].shift(-1)) & \
        ~meetings['meeting'].shift(-1).isna()
    meetings.loc[meetings['split_meeting']==True,'meeting'] = \
        meetings['meeting'] + ' ' + meetings['meeting'].shift(-1)
    meetings = meetings.dropna(subset='time')
    
    # Combine split rows for time variable
    meetings['split_time'] = (meetings['meeting_id'] == meetings['meeting_id'].shift(-1)) \
        & ~meetings['time'].str.contains('^a.m*$|^p.m*$').shift(-1).fillna(False)
    meetings.loc[meetings['split_time']==True, 'time'] = meetings['time'] + \
        ' ' + meetings['time'].shift(-1).fillna('')
    meetings = meetings[~((meetings['time'] == 'a.m.') | (meetings['time'] == 'p.m.'))]
    
    # Merge days dfset and meetings dataset on day variable
    tmp = pd.merge(days, meetings, on="day_id")
    keep_cols = ['date', 'time', 'meeting', 'meeting_id']
    tmp = tmp[keep_cols]
    schedule = pd.concat([schedule, tmp], ignore_index=True)

schedule.to_csv("../../data/yellen_schedules.csv", index=False)