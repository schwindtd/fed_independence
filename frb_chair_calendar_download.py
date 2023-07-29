#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program to download and merge PDF Calendar records from FRASER
Created on Wed Jun 28 22:21:47 2023

@author: danielschwindt
"""

import os
import requests
import glob
#from pypdf import PdfMerger
from PyPDF2 import PdfFileReader, PdfFileWriter

# Set working directory
base_dir = "/Users/danielschwindt/Documents/research_projects/fed_independence/raw_schedules"
os.chdir("/Users/danielschwindt/Documents/research_projects/fed_independence/code/")
wkdir = os.getcwd()
from fraser_functions import fraser_api_url_get, fraser_pdf_get
from pdf_functions import merge_pdfs

# Set API super-title query for Fed Chair Calendars
api_key = os.getenv("API_KEY")
api_base_url = 'https://fraser.stlouisfed.org/api'
super_title = '5183'
limit = 200

# Get titles under Fed Chair calendar super category
titles = fraser_api_url_get(api_key, api_base_url, super_title)
# Remove Hamlin records
titles = titles[1:]

# Create sub directories for each Fed Chair
sub_dirs = ['martin', 'volcker', 'greenspan', 'bernanke',
           'yellen', 'powell']
new_dirs = [base_dir + "/" + d for d in sub_dirs]
for d in new_dirs:
    if not os.path.exists(d):
        os.makedirs(d)

# Loop through each title and download all PDFs
for title, sub_dir in zip(titles, sub_dirs):
    fraser_pdf_get(api_key, title, base_dir, sub_dir, limit)

# Delete corrupted Powell PDF: 2021-04-01
# Pending fix by FRASER team
corrupt_pdf = "/".join([base_dir, "powell", "chair-powell-calendar-20210401.pdf"])
try:
    os.remove(corrupt_pdf)
except OSError:
    pass
    
# Combine monthly PDFs into annual PDFs
# Martin
os.chdir("/".join([base_dir, "martin"]))
pdf_list = glob.glob("*.pdf")
pdf_list.sort()
pdf_list = pdf_list[6:]
year_list = [i.split("_")[2] for i in pdf_list]
year_set = set(year_list)
for year in year_set:
    year_pdf_list = glob.glob("".join(["*_",year, "*.pdf"]))
    year_pdf_list.sort()
    output_file = "".join(["martin_", year, ".pdf"])
    merge_pdfs(year_pdf_list, output_file)
    # merger = PdfMerger()
    # for pdf in year_pdf_list:
    #     merger.append(pdf)
    # merger.write("".join(["martin_", year, ".pdf"]))
    # merger.close()

# Yellen & Powell
for s in ["yellen", "powell"]:
    os.chdir("/".join([base_dir, s]))
    pdf_list = glob.glob("*.pdf")
    pdf_list.sort()
    year_list = [i.split("_")[1].split(".")[0][0:4] for i in pdf_list]
    year_set = set(year_list)
    for year in year_set:
        year_pdf_list = glob.glob("".join(["*_",year, "*.pdf"]))
        year_pdf_list.sort()
        output_file = "".join([s,"_", year, ".pdf"])
        merge_pdfs(year_pdf_list, output_file)
        # merger = PdfMerger()
        # for pdf in year_pdf_list:
        #     merger.append(pdf)
        # merger.write("".join([s,"_", year, ".pdf"]))
        # merger.close()
