#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 12:46:35 2023

@author: danielschwindt
"""
import requests

def fraser_api_url_get(api_key, api_base_url, title):
    # Function to extract API URLs under a particular super title
    # Arguments:
        # 1. api_key: key needed for accessing FRASER API
        # 2. api_base_url: base api location
        # 3. title: base title under which additional titles are located
    # Output: 
        # List of API URLs for specific titles under the super title series
    headers = {'Accept': 'application/json',
               'X-API-Key': api_key}
    url = "/".join([api_base_url,'title', title, 'items'])
    response = requests.get(url, headers=headers)
    data = response.json()
    records = data['records']
    title_list = [d['location']['apiUrl'][0] for d in records]
    return title_list

def fraser_pdf_get(api_key, api_url, wkdir, subdir, limit):
    headers = {'Accept': 'application/json',
               'X-API-Key': api_key}
    params = {'limit': limit}
    url = "/".join([api_url,'items'])
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    records = data['records']
    # Iterate over each record in series and save PDF
    for record in records:
        pdf_url = record['location']['pdfUrl'][0]
        pdf_name = pdf_url.split('/')[-1]
        print("Downloading: ", pdf_name)
        pdf_response = requests.get(pdf_url)
        with open("/".join([wkdir,subdir,pdf_name]), "wb") as f:
            f.write(pdf_response.content)


    