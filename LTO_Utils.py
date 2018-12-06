from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#from google.colab import auth
from oauth2client.client import GoogleCredentials
import os
import pandas as pd
import numpy as np

import bz2
import pickle

#ripped and modified from Utah project
def get_files(slug, files=False):
    """
    returns a list of files from a google drive folder, recurses down into sub-dirs
    Parameters:
        slug: id of the directory
        files: True => return file objects, False => return file names
    Returns:
        List of file names or file objects in the directory
    """
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        os.remove('mycreds.txt')
        gauth.LocalWebserverAuth()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    return list_folder(slug, drive, files=files)

def list_folder(parent, drive, is_top=True, files=False):
    try:
        file_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(
                parent)}).GetList()
        fids = []
        for f in file_list:
            if f['mimeType'] == 'application/vnd.google-apps.folder':
                fids = fids + list_folder(f['id'], drive, is_top=False, files=files)
            else:
                if files:
                    fids.append(f)
                else:
                    fids.append(f['title'])
        return (fids)

    except Exception as e:
        print(e)

def get_pickled_fft(fname, dFclip=None):
    """
    Returns a data frame from a file assumed to contain a pickled fft dataframe
    Parameters:
        fname: path to the pickled file
        dFclip: lower and upper limits for dF -- only records in this range are returned
    Returns:
        the fft dataframe
    """
    with bz2.BZ2File(fname, 'r') as sfile:
        df4 = pickle.load(sfile)

    # clip if necessary:
    if dFclip is not None:
        df4 = df4[(df4['dF'] >= dFclip[0])  & (df4['dF'] <= dFclip[1])]

    dt = pd.to_datetime(df4['YMD'] + ' ' + df4['HMS'])
    return pd.DataFrame({'dF': df4['dF'], 'dt':dt, 'PWR':df4['PWR'], 'PWR_dBm':df4['PWR_dBm']})


    return df4