from asyncio.windows_events import NULL
from logging import exception
import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS

from geopy.geocoders import Nominatim

from pprint import pprint as pp
from PyQt5.QtCore import  QObject, pyqtSignal
import datetime

class Arranger(QObject) :

    updateProgressSignal = pyqtSignal(int) #클래스 변수로 선언
    updateLogSignal = pyqtSignal(str) #클래스 변수로 선언

    # Image EXIF 정보 가져오기
    def GetExif(self, filePath) :
        img = Image.open(filePath)
        taglabel = {}

        try :
            info = img._getexif()
            #print("\n --- info begin ---\n {} \n --- info end ---\n".format(info))
            for tag, value in info.items() :
                decoded = TAGS.get(tag, tag)

                #print("decoded : {}".format(decoded))

                taglabel[decoded] = value

        except Exception as e :
            print('Exception : {}'.format(e))
        
        #pp(taglabel)

        return taglabel

    #EXIF 로부터 시간정보 얻어오기
    def GetTimeInfo(self, taglabel) :
    
        #시간정보 얻기
        if taglabel.get('DateTimeOriginal') != None :
            timeInfo = taglabel['DateTimeOriginal']

        elif taglabel.get('DateTimeDigitized') != None :
            timeInfo = taglabel['DateTimeDigitized']

        elif taglabel.get('DateTime') != None :
            timeInfo = taglabel['DateTime']

        elif taglabel.get('CreateDate') != None :
            timeInfo = taglabel['CreateDate']

        else:
            print('there is no information for time')
            timeInfo = 0
        
        #print("Date : {}".format(timeInfo))

        return timeInfo

    #EXIF에서 GPS정보 가져오기
    def GetGpsInfo(self, taglabel) :

        #위치정보 얻기
        if taglabel.get('GPSInfo') != None :
            gpsInfo = taglabel['GPSInfo']
        else :
            gpsInfo = 0
            print('there is no information for GPS')

        #print("GPSInfo : {}".format(gpsInfo))

        return gpsInfo

    #file 검색
    def searchFile(self, path) :
        files=os.listdir(path)

        return files

    #하위폴더 포함하여 전체 파일 검색
    def searchWithSubDir(self, path) : 
        fileArr = []

        for (path, dir, files) in os.walk(path):
            for filename in files:
                full_filename = os.path.join(path, filename)
                ext = os.path.splitext(filename)[-1]

                if ext == '.jpg' or ext == '.JPG' or ext == '.HEIC':
                    fileArr.append(full_filename)
                else :
                    print("{} is not imagefile".format(full_filename))

        return fileArr

    #GPS정보로부터 위경도 얻어오기
    def ConvertGPSToDegMinSec(self, latNS, latData, lonWE, lonData) :  
        latDeg = latData[0]
        latMin = latData[1]
        latSec = latData[2]
        print("location type : {}".format(type(latData)))
        print("lat N / S : {}".format(latNS))
        print("latData : {}".format(latData))
        print("latDeg : {}".format(latDeg))        
        print("latMin : {}".format(latMin))        
        print("latSec : {}".format(latSec))        

        lat = str(int(latDeg)) + "°" + str(int(latMin)) + "'" + str(latSec) + "\"" + latNS
        #print("latitude : {}".format(lat))
        
        lonDeg = lonData[0]
        lonMin = lonData[1]
        lonSec = lonData[2]
        print("lonData : {}".format(lonData))
        print("lon W / E : {}".format(lonWE))
        print("lonDeg : {}".format(lonDeg))        
        print("lonMin : {}".format(lonMin))        
        print("lonSec : {}".format(lonSec))        

        lon = str(int(lonDeg)) + "°" + str(int(lonMin)) + "'" + str(lonSec) + "\"" + lonWE        
        #print("Longitude  : {}".format(lon))

        return lat, lon

    #위경도 DECIMAL값 얻어오기
    def ConvertGPSToDec(self, latNS, latData, lonWE, lonData) :
        latDeg = latData[0]
        latMin = latData[1]
        latSec = latData[2]
        print("location type : {}".format(type(latData)))
        print("lat N / S : {}".format(latNS))
        print("latData : {}".format(latData))
        print("latDeg : {}".format(latDeg))        
        print("latMin : {}".format(latMin))        
        print("latSec : {}".format(latSec))  

        latDec = (latDeg + (latMin + latSec / 60.0) / 60.0)
        # If S, -1
        if latNS == 'S': latDec = latDec * -1    

        lonDeg = lonData[0]
        lonMin = lonData[1]
        lonSec = lonData[2]
        print("lonData : {}".format(lonData))
        print("lon W / E : {}".format(lonWE))
        print("lonDeg : {}".format(lonDeg))        
        print("lonMin : {}".format(lonMin))        
        print("lonSec : {}".format(lonSec))
        lonDec = (lonDeg + (lonMin + lonSec / 60.0) / 60.0)
        # If W, -1
        if lonWE == 'W': lonDec = lonDec * -1

        return latDec, lonDec

    #위경도를 가지고 주소 얻어오기
    def getAddress(self, latlong):
        geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
        address = geolocoder.reverse(latlong)
        #print(address)

        return address

    #시간정보로 파일명 만들기
    def getTimeString(self, time) :
        time = "{}".format(time)
        print("getTimeString : {}".format(time))
        timeStr = time.split(' ')
        print(timeStr)

        daystr = timeStr[0].split(':')
        hms = timeStr[1].split(':')

        print("Time From EXIF - day : {}, time : {}".format(daystr, hms))

        timename = "{}{}{}_{}{}{}".format(daystr[0], daystr[1], daystr[2], hms[0], hms[1], hms[2])

        return daystr, timename

    #주소로 파일명 만들기
    def getAddressName(self, address) : 
        addr = address.split(", ")
        addrname = "{}{}".format(addr[2], addr[1])

        return addrname

    #폴더 만들기
    def CreateDirectory(self, destdir, dir1, dir2) :
        dir1 = "{}/{}".format(destdir, dir1)
        print("dir : {}".format(dir1))
        try :
            if not os.path.exists(dir1):
                os.makedirs(dir1)
                print("create dir : {}".format(dir1))
            
            path = "{}{}".format(dir1, dir2)
            print("sub dir : {}".format(path))

            if not os.path.exists(path):
                os.makedirs(path)
                print("create sub dir : {}".format(path))

        except OSError :
            print("creating direction is failed")

    #EXIF 정보 없는 경우 file에서 생성날짜 또는 수정날짜 가져오기
    def GetTimeInfoFromFile(self, path) :
        
        mtime = os.path.getmtime(path)
        ctime = os.path.getctime(path)

        if mtime > ctime :
            print("Create time is selected")
            time = datetime.datetime.fromtimestamp(ctime)
        else :
            print("Modified time is selected")
            time = datetime.datetime.fromtimestamp(mtime)

        time = "{}".format(time)
        print(time)
        time = time.split(' ')
        daystr = time[0].split('-')
        hms = time[1].split(":")

        print("Modifile file info - day : {}, time : {}".format(daystr, hms))
        timename = "{}{}{}_{}{}{}".format(daystr[0], daystr[1], daystr[2], hms[0], hms[1], hms[2])

        return daystr, timename

    #동일한 파일이 있는지 체크
    def CheckFileRename(self, filename, index) :
        originName = filename

        while os.path.exists(filename) :
            index += 1
            filename = originName
            tempname = filename.split('.')
            filename = "{}{}.{}".format(tempname[0], index, tempname[1])

        return filename

    #파일정리 process
    def FileOrganize(self, files, destdir) :

        fileSize = len(files)
        numOfFinFile = 0

        if fileSize <= 0 :
            progressRatio = -1
            self.updateProgressSignal.emit(progressRatio) #customFunc 메서드 실행시 signal의 메서드 사용

        for name in files:
            i = 0

            print(name)
            ext = os.path.splitext(name)[-1]

            if(ext == '.JPG' or ext == '.jpg'):
                taglabel = self.GetExif(name)
                time = self.GetTimeInfo(taglabel)

                location = self.GetGpsInfo(taglabel)
            else :
                time = 0
                location = 0

            print("Time : {}".format(time))
            print("Location : {}".format(location))

            if time != 0:
                
                print("time from EXIF {}".format(time))
                daystr, timename = self.getTimeString(time)
                print("time from image {}".format(timename))
                rootDirName = "{}{}/".format(daystr[0], daystr[1])
                dirname = "{}/".format((timename.split("_"))[0])
            else :
                daystr, timename = self.GetTimeInfoFromFile(name)
                print("modified file time : ".format(timename))
                rootDirName = "m{}{}/".format(daystr[0], daystr[1])
                dirname = "{}/".format((timename.split("_"))[0])

            if location != 0 :
                latNS = location[1]
                latData = location[2]
                lonData = location[4]
                lonWE = location[3]        

                lat, lon = self.ConvertGPSToDegMinSec(latNS, latData, lonWE, lonData)
                print("latitude : {}".format(lat))
                print("Longitude  : {}".format(lon))

                latDec, lonDec = self.ConvertGPSToDec(latNS, latData, lonWE, lonData)
                print("latitude Decimal : {}".format(latDec))
                print("Longitude Decimal : {}".format(lonDec))

                address = self.getAddress("{}, {}".format(latDec, lonDec))
                print(address)
                addrname = self.getAddressName("{}".format(address))
                print(addrname)
            else : 
                addrname = 'unknown'
                print(addrname)

           
            filename = "{}/{}{}{}_{}{}".format(destdir,rootDirName, dirname, timename, addrname, ext)
                    
            self.CreateDirectory(destdir, rootDirName, dirname)

            filename = self.CheckFileRename(filename, i)

            try :
                os.rename(name, filename)
                print("{} --->> {}".format(name, filename))
            except : 
                
                i += 1
                tempname = filename.split('.')
                filename = "{}{}.{}".format(tempname[0], i, tempname[1])
                os.rename(name, filename)
                print("{} --->> {}".format(name, filename))

            numOfFinFile += 1

            progressRatio = (numOfFinFile / fileSize) * 100

            #print("Progress : {}%".format(progressRatio))
            self.updateProgressSignal.emit(progressRatio) #customFunc 메서드 실행시 signal의 메서드 사용
            self.updateLogSignal.emit("{} --->> {}".format(name, filename))

'''
if __name__ == "__main__" :
    
    #files = searchFile("D:\\Workspace\\Python_workspace\\fileTest")
    #if files.__contains__ : 
    #    FileOrganize(files)
    #else :
    #    print("File is not found")
    arranger = Arranger()
    files = arranger.searchWithSubDir("D:\\Workspace\\Python_workspace\\fileTest")
    destdir = 'D:/Workspace/Python_workspace/FileArranger'
    if files.__contains__ : 
            arranger.FileOrganize(files, destdir)
    else :
        print("File is not found")
'''