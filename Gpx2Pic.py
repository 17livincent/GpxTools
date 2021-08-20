'''
    Gpx2Pic.py
    Info: Creates a PNG photo of the trackpoints and color-coded elevation from a GPX file.
    Elevation color code is low (green, 0, 255, 0) -> medium (yellow, 255, 255, 0) -> high (red, 255, 0, 0).
'''

import numpy as np
from datetime import datetime
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps

IMAGEWIDTH = 500
IMAGEHEIGHT = 500

TRACKPOINT = {
    'time': '',
    'lat': 0,
    'long': 0
}

def readFile(xml_file):
    '''
        Reads the GPX/TCX file and returns an array of trackpoints.
    '''
    fileType = xml_file[xml_file.rfind('.') + 1: ].lower()
    trackPointList = []

    if(fileType == 'gpx'):
        print('File is GPX')

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # find trk        
        trkIndex = -1
        for i in range(0, len(root)):
            if(root[i].tag.rpartition('}')[2] == 'trk'):
                trkIndex = i
        assert(trkIndex >= 0)

        # find trkseg
        trksegIndex = -1
        for i in range(0, len(root[trkIndex])):
            if(root[trkIndex][i].tag.rpartition('}')[2] == 'trkseg'):
                trksegIndex = i
        assert(trksegIndex >= 0)

        # create a list of track points
        for i in root[trkIndex][trksegIndex]:
            trackPoint = TRACKPOINT.copy()
            trackPoint['lat'] = np.float64(i.attrib['lat'])
            trackPoint['lon'] = np.float64(i.attrib['lon'])
            trackPoint['time'] = datetime.strptime(i[1].text, '%Y-%m-%dT%H:%M:%S.000Z')
            trackPoint['elev'] = np.float64(i[0].text)
            trackPointList.append(trackPoint)
            #print(trackPoint)

        return trackPointList

    else:
        print('ERROR: Unsupported file type')


def getGpxSummary(trackPointList):
    # Find min and max values
    minElev = 0
    maxElev = 0
    minLon = 0
    maxLon = 0
    minLat = 0
    maxLat = 0

    first = True

    for i in trackPointList:
        if first or i['elev'] < minElev:
            minElev = i['elev']

        if first or i['elev'] > maxElev:
            maxElev = i['elev']

        if first or i['lon'] < minLon:
            minLon = i['lon']

        if first or i['lon'] > maxLon:
            maxLon = i['lon']

        if first or i['lat'] < minLat:
            minLat = i['lat']

        if first or i['lat'] > maxLat:
            maxLat = i['lat']

        first = False

    print('Summary:')
    print('Min elevation: ' + str(minElev))
    print('Max elevation: ' + str(maxElev))
    print('Min longitude: ' + str(minLon))
    print('Max longitude: ' + str(maxLon))
    print('Min latitude: ' + str(minLat))
    print('Max latitude: ' + str(maxLat))

    return {
        'minElev': minElev,
        'maxElev': maxElev,
        'minLon': minLon,
        'maxLon': maxLon,
        'minLat': minLat,
        'maxLat': maxLat
    }


def createImage(trackPointList, mm):
    '''
        Creates the route image with the track point list and min/max values.
    '''
    profile = Image.new(mode="RGB", size=(IMAGEWIDTH, IMAGEHEIGHT), color = 'black')
    
    for i in trackPointList:
        # normalize lon and lat between 0 and image dimension
        i['lon'] = (i['lon'] - mm['minLon']) / (mm['maxLon'] - mm['minLon']) * (IMAGEWIDTH - 1)
        i['lat'] = (i['lat'] - mm['minLat']) / (mm['maxLat'] - mm['minLat']) * (IMAGEHEIGHT - 1)
        # normalize elevation between 0 and 255*2
        i['elev'] = (i['elev'] - mm['minElev']) / (mm['maxElev'] - mm['minElev']) * (255 * 2)
    
    #getSummary(trackPointList)

    for i in trackPointList:
        green = 0
        red = 0
        if i['elev'] <= 255:
            red = red + i['elev']
            green = 255
        else:
            red = 255
            green = 255 - i['elev'] - 255

        profile.putpixel(
            (int(i['lon']), int(i['lat'])),
            (int(red), int(green), 0)
        )

    profile = ImageOps.flip(profile)
    profile.show()


def main():
    trackPointList = readFile('examples/Example2.gpx')
    print('Number of track points: ' + str(len(trackPointList)))
    mm = getGpxSummary(trackPointList)
    createImage(trackPointList, mm)


if __name__ == '__main__':
    main()