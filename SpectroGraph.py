
import numpy as np
import pandas as pd
#from LTO_Utils import *
from os import listdir
from os.path import isfile, join
import re
#from class1 import get_pickled_fft

import bz2
import pickle

class SpectroGraph:
    """
    Attributes and methods for a Time by Frequency spectrograph
    """
    def __init__(self, pname, dFclip=None, dTclip=None):
        """
        Creates a spectrograph object.
        Parameters: pname: string, directory containing pickled files
                    dFclip: tuple of reals, (low, high), values outside this range discarded
                    dTclip: tuple of (??), not yet implemented, don't specify a value
        """
        assert(dTclip is None)
        # store off the parameters
        self.path = pname
        self.dFclip = dFclip
        self.dTclip = dTclip
        
        # get a list of all of .pcl files in the data directory
        fftfiles = [f for f in listdir(self.path) if re.search('.*pcl$',f) ]
        
        # get the dataframe for each minute and concatenate into a long one:
        self.data = pd.concat([self.__get_pickled_fft(join(self.path,f),
                                         dFclip=dFclip) for f in fftfiles])
        
        self.times = self.data['dt'].unique()
        self.freqs = self.data['dF'].unique()
        
        #reshape to produce spectrograph (assuming incoming data is right order and no holes)
        self.pwr = np.array(self.data['PWR']).reshape(len(self.times), len(self.freqs)).T #transpose to row order

    def describe(self):
        print ('made from files in ' + self.path + ' directory')
        print ('pwr shape: '+ str(self.pwr.shape))
        print ('Frequency bins: %d, time slices: %d, rows in data: %d'%(len(self.freqs), len(self.times), len(self.data)))

    def __get_pickled_fft(self, fname, dFclip=None):
        """
        Class private function that returns a data frame from a file assumed to contain a pickled fft dataframe
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
