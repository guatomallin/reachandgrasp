#Filter and thresholding function for likelihoods. This will generate cleaned data if desired.
import os
import re
from itertools import tee, islice, zip_longest

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, peak_prominences


class BatchLoader():

    def __init__(self, name):
        self.name = name
        pass
    def getFile(self, path):

        files = [file for file in os.listdir(path)]

        return files



class FilterandThresholds():

    def __init__(self, name):
        self.name = name
        pass

    def bodypart_selector(self, data, bodypart, likelihoodSelect):
        # https://stackoverflow.com/questions/18470323/selecting-columns-from-pandas-multiindex
        # https://stackoverflow.com/questions/22233488/pandas-drop-a-level-from-a-multi-level-column-index
        bodypartData = data.loc[:, ['bodyparts', bodypart]]
        bodypartData.columns = bodypartData.columns.droplevel()
        scale = 2.9
        #convert datatypes to int and float
        bodypartData['coords'] = bodypartData['coords'].astype(int)
        bodypartData['x'] = bodypartData['x'].astype(float)/scale
        bodypartData['y'] = bodypartData['y'].astype(float)/scale
        bodypartData['likelihood'] = bodypartData['likelihood'].astype(float)



        if likelihoodSelect is True:
            threshold = 0.5
            bodypartData = bodypartData[bodypartData['likelihood'] > threshold]

        # Because the likelihood threshold does not fill in the extracted rows, we need to create a new index.
        ####This is in place until we create a solution to fill in gaps in the data.
        bodypartData = bodypartData.reset_index()
        bodypartData = bodypartData.reset_index().set_index('coords')
        return bodypartData
        #Because the likelihood threshold does not fill in the extracted rows, we need to create a new index.



    def curveAligner(self, bodypartData):



        bodypartData['diff'] = np.nan * len(bodypartData)
        bodypartData['cumsum'] = np.nan * len(bodypartData)
    #The input to this function is body part specific data to which we will add additional information.
        pass

    def MultiIndexMaker(self, data):
        unwanted_label = []

        unwanted_label = [col for col in data.columns if 'scorer' in col]

        #print(unwanted_label)
        if unwanted_label == ['scorer']:
            #reasign the columns in the data
            data.columns = data.iloc[0]

            top_level = list(data.columns)

            #We can probably do this in one line.
            #top_level.extend(['Animal Infor'] * 4)
            top_level += 6 * ['Animal Infor']

            data.columns = data.iloc[1]
            data['ID'] = np.nan
            data['Condition'] = np.nan
            data['Reach Number'] = np.nan
            data['Limb'] = np.nan
            data['performance'] = np.nan


            #Here we convert frame index to seconds.
            time_saver = []
            fps = 300
            for f in range(len(data.iloc[1:, 0])):
                s = int(f) / fps
                time_saver.append(s)
            # Insert column headers to the data fits in the existing dataframe
            time_saver.insert(0, 's')
            data['Time'] = time_saver
            # time_saver = ((int(data.coords) / 30)*10)
            # time_saver.insert(0, 's')
            # data['Time'] = time_saver




            #Here we add a column for

            secondLev = data.columns

            #This creates duplicate rows with the same name, so we have to change that.

            #Here we reassign the data minus the duplicate column to the data.
            data = data.iloc[1:, :]
            #print('top level created')
        else:
            print('no scorer found')

        data.columns = pd.MultiIndex.from_arrays([top_level, secondLev])
        data = data.iloc[1:]





        return data

    def singleIndexMaker(self, data):



        top_level = list(data.columns)

        # We can probably do this in one line.
        # top_level.extend(['Animal Infor'] * 4)
        top_level += 6 * ['Animal Infor']

        data.columns = data.iloc[1]
        data['ID'] = np.nan
        data['Condition'] = np.nan
        data['Reach Number'] = np.nan
        data['Limb'] = np.nan
        data['performance'] = np.nan


        pass
    #This function takes the output of bodypart selector to further clean the signal.
    #This function separates the reach into extension and retraction and cleans around the edges.

    def splitter(self, signal, whichPlane):

        # First split at reach by whichPlane max. In coords plane

        #Get the min index
        minReachInd = np.argmin(signal[whichPlane])

        # Reset index
        #minReachIndReal = signal['level_0'].loc[minReachInd.item()]
        yMaxValue = signal[whichPlane].iloc[minReachInd]

        cleanSignal = signal[: minReachInd]

        # Here find the start of the reach based on velocity spikes.
        # This isolates the peak closest to the reach max.
        # velocityPeakArray = np.asarray(velocity_peaks)
        # new_velocityPeakArray = []

        # for peak in velocityPeakArray:
        #     if peak < minReachInd:
        #         new_velocityPeakArray.append(peak)
        # new_velocityPeakArray = np.asarray(new_velocityPeakArray)
        # print(new_velocityPeakArray)
        # #bool_newVel = bool(new_velocityPeakArray[0])
        # if new_velocityPeakArray.size > 0:
        #     idx = (np.abs(new_velocityPeakArray - minReachInd)).argmin()
        #     nearPeakToReachIndex = new_velocityPeakArray[idx]
        #     print('peak found, applied function')
        #     # Now we do the spliting to cleanSignal. Our index is in real index, but we need to swtich it to coord index.
        #     # coordIndex = cleanSignal.index[cleanSignal['level_0'] == nearPeakToReachIndex]
        #     # coordIndex = coordIndex[0]
        #     boolNeartoPeak = nearPeakToReachIndex - 0
        #     if boolNeartoPeak > 2:
        #         doubleCleanedSignal = cleanSignal[nearPeakToReachIndex - 2:minReachInd]
        #
        #     else:
        #         doubleCleanedSignal = cleanSignal
        #         print('signal not cut')
            # doubleCleanedSignal['Time_Aligend'] = np.arange(0, (0.0033 * len(doubleCleanedSignal.Time) - 1), 0.0033)


        # else:
        #     print('no peak found, applied a different function')
        #     doubleCleanedSignal = cleanSignal

        return cleanSignal, minReachInd

    #NEEDS TO BE REFACTOR OR ADD CONDITIONAL TO SEARCH DLC OR BORIS DATA
    def rexsearch(self, file, csv):

        csvs_animalNum = []

        #Search for animal number from te file name and put it in a new column
        csvs_animalNum = list([int(n) for n in re.findall(r'\d+', file) if len(n) == 5] * len(csv.index))

        #We import the file name and the multi-index csv to add new columns.
        csv['Animal Infor', 'Reach Number'] = [re.findall(r'_\d{1,2}_', str(file)).pop(0).lstrip('_').rstrip('_')] * len(csv.index)

        #Search through the file name to animal conditon.
        animalCond_blindBool = re.search(r'_blind_', str(file))
        animalCond_contBool = re.search(r'_control_', str(file))

        #... limb used
        animalCond_rightBool = re.search(r'_right_', str(file))
        animalCond_leftBool = re.search(r'_left_', str(file))

        #... whether the reach was successful or failure
        animalCond_succBool = re.search(r'_success_', str(file))
        animalCond_failBool = re.search(r'_fail_', str(file))

        #Now put it all together
        # Specify condition
        if animalCond_blindBool:
            csv['Animal Infor', 'Condition'] = list(['blind'] * len(csv.index))

        elif animalCond_contBool:
            csv['Animal Infor', 'Condition'] = list(['control'] * len(csv.index))

        # Specify limb used
        if animalCond_rightBool:
            csv['Animal Infor', 'Limb'] = list(['right'] * len(csv.index))

        elif animalCond_leftBool:
            csv['Animal Infor', 'Limb'] = list(['left'] * len(csv.index))

        # Specify whether the reach was successful or not.
        if animalCond_succBool:
            csv['Animal Infor', 'performance'] = list(['success'] * len(csv.index))

        elif animalCond_failBool:
            csv['Animal Infor', 'performance'] = list(['fail'] * len(csv.index))

        #Add animal number to each individual file
        csv['Animal Infor','ID'] = csvs_animalNum

        #return the csv and add it to the rest of the giant dataframe in a loop outside of this class file.
        return csv


class simpleKinematics():

    def __init__(self, name):

        self.name = name

        pass
    #rename to peaks
    def curveExtractor(self, signal,trough_height, trough_width, peak_height, peak_width, prominences, gausFilter):
        #smooth with gauss filter
        if gausFilter is True:
            signal_gaussfilter = gaussian_filter1d(signal, sigma = 2)
        #find peaks and troughs in order to isolate curves.

            signal = signal.tolist()
            min_x_indx = signal.index(min(signal))

            #Before using this, consider using peak_prominences to better target what you need. For now, test the heights by guessing.
            #Note that the find_peak conditionals don't work if the signal is negative (DOn't know how to make it work for troughs).
            troughs, _ = find_peaks(-signal_gaussfilter, trough_height, trough_width)
            #We added a peak finding program section that uses the positive signal.
            peaks, properties  = find_peaks(signal_gaussfilter, peak_height, peak_width, prominences)

            prominences = peak_prominences(signal_gaussfilter, peaks)[0]
            signal = signal_gaussfilter
        else:
            peaks, _ = find_peaks(signal, peak_height, peak_width, prominences)
            troughs, _ =find_peaks(-signal, trough_height, trough_width)
            prominences = peak_prominences(signal, peaks)[0]

            min_x_indx = None


        return troughs, peaks, min_x_indx, signal, prominences



    def get_next(self, some_iterable, window=1):
        items, nexts = tee(some_iterable, 2)
        nexts = islice(nexts, window, None)
        return zip_longest(items, nexts)

    def time_interval(self, curve):
        #count the time elapsed between the start and end of the movement


        pass


    #Here we want to calculate the euclidean distance between two points over change in time.
    #We should import the entire dataset
    def velocity(self, signal, whichPlane):

        whichPlane = str(whichPlane)

        #Initialize new dataframe
        verticalCompL = pd.DataFrame(columns=[whichPlane, 'Time', 'velocity'])
        verticalCompL[whichPlane] = signal[whichPlane]
        verticalCompL['Time'] = signal['Time']

        #Calculate acceleration
        pos_diff = np.diff(verticalCompL[whichPlane])
        time_diff = np.diff(verticalCompL['Time'])
        # Velocity - we make it an absolute value for ease of use.
        constantAccVelocity = (pos_diff / time_diff)



        return constantAccVelocity







    def speed(self, data):

        pass
