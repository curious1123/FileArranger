import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from Arranger import Arranger
from PyQt5.QtCore import pyqtSlot

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("FileOrganizer.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)   
        self.arranger = Arranger()
        self.progressBar.setValue(0)

        self.srcButton.clicked.connect(self.srcButtonEvent)
        self.destButton.clicked.connect(self.destButtonEvent)
        self.startButton.clicked.connect(self.startButtonEvent)
        self.arranger.updateProgressSignal.connect(self.UpdateProgress) #객체에 대한 시그널 및 슬롯 설정.
        self.arranger.updateLogSignal.connect(self.UpdateLog) #객체에 대한 시그널 및 슬롯 설정.

    #Source 디렉토리 설정
    def srcButtonEvent(self) :
        self.srcdirname = QtWidgets.QFileDialog.getExistingDirectory()
        print(self.srcdirname)
        self.srcText.setText(self.srcdirname)

    #Destination 디렉토리 설정
    def destButtonEvent(self) :
        self.destdirname = QtWidgets.QFileDialog.getExistingDirectory()
        print(self.destdirname)
        self.destText.setText(self.destdirname)

    #Start 동작
    def startButtonEvent(self) :
        print('start')
        self.srcdirname = self.srcdirname.replace('/', '\\')
        #self.destdirname = self.destdirname.replace('/', '\\')

        files = self.arranger.searchWithSubDir(self.srcdirname)
    
        if files.__contains__ : 
            self.arranger.FileOrganize(files, self.destdirname)
        else :
            print("File is not found")

    #Progress bar update
    @pyqtSlot(int)
    def UpdateProgress(self, ratio) :
        print("Progress : {}%".format(ratio))
        self.progressBar.setValue(ratio)

        if ratio == -1 :
            message = 'Not find file'
        elif ratio > 0 and ratio < 100 : 
            message = 'Processing....'
        elif ratio >= 100 :
            message = 'Finish'
        else :
            message = 'ready'
            
        self.statusBar().showMessage(message)

    #Log 출력
    @pyqtSlot(str)
    def UpdateLog(self, log) :
        self.logText.append(log)

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()
    
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()