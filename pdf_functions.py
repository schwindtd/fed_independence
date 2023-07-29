#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 21:19:11 2023

@author: danielschwindt
"""

from PyPDF2 import PdfFileReader, PdfFileMerger
import pandas as pd
import tabula as tb
import re

## Function to merge PDF files into one PDF file
def merge_pdfs(paths, output):
    merger = PdfFileMerger(strict=False)

    for path in paths:
        merger.append(PdfFileReader(open(path, 'rb')))
    
    merger.write(output)

## Function to convert calendar PDFs into raw dataframe
def pdf_to_df(pdf_file, area=[75,0,800,800], cols=[200,750], header=None, stream=True):
    reader = PdfFileReader(open(pdf_file, 'rb'))
    pdf_page_count = len(reader.pages)
    df = pd.DataFrame()
    for page in range(1,pdf_page_count+1):
        try:
            # Extract data into data table
            data = tb.read_pdf(pdf_file, pages = str(page), area = area,
                               columns=cols, pandas_options={'header': header},
                               stream=stream)[0]
            # Drop rows with all NAN
            data.dropna(how="all", inplace=True)
        except:
            pass
        df = pd.concat([df, data], ignore_index=True)
        return df

## Function to create dummy variable based on text patterns
def txt_pattern_indicator(df, pattern, new_var, old_var):
    df[new_var] = df.apply(lambda x: 1 if re.findall(pattern, str(x[old_var])) else 0, axis=1)
    return df

## Function to create running identifier variables
def id_create(df, new_var, old_var,  trans='cumsum'):
    df[new_var] = df[old_var].transform(trans)
    return df

## Function to combine rows based on condition
    