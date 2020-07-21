from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import numpy as np
import sys
import os


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount
        super(MainWindow, self).__init__(*args, **kwargs)

        day = Temp = Vmin = np.array([])
        dayplot = Temp_avg = Vmin_avg = np.array([])

        #Load the UI Page
        uic.loadUi(r"C:\Users\adekunlea\Documents\Programming\BiosensorProgram\Scripts\Analyzermainwindow.ui", self)

        self.setWindowTitle("Data Summarizing Application")

        self.loadButton.clicked.connect(self.on_load_button_clicked)

        self.plotButton.clicked.connect(self.on_plot_button_clicked)

        self.saveButton.clicked.connect(self.on_save_button_clicked)

        self.deleteButton.clicked.connect(self.on_delete_button_clicked)

        self.plotBox1.currentIndexChanged.connect(self.check_box1)
        self.plotBox2.currentIndexChanged.connect(self.check_box2)

        self.dateCheck.stateChanged.connect(self.check_date_view)
        self.date_check = False


        color = self.palette().color(QtGui.QPalette.Window)  # Get the default window background,
        self.graphWidget.setBackground(color)
        # Add Title
        self.graphWidget.setTitle("Daily Averages Summary Plot", color="k", size="12pt")
        # Add Axis Labels
        styles = {"color": "k", "font-size": "8pt"}
        # Making plot's axis lines black
        pen = pg.mkPen(color='k')
        self.graphWidget.plotItem.getAxis('left').setPen(pen)
        self.graphWidget.plotItem.getAxis('right').setPen(pen)
        self.graphWidget.plotItem.getAxis('bottom').setPen(pen)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        #self.graphWidget.setXRange(0, 10, padding=0)
        #self.graphWidget.setYRange(20, 55, padding=0)
        self.plotBox1.addItem("Left Y Axis Variable")
        self.plotBox2.addItem("Right Y Axis Variable")


    def on_load_button_clicked(self):
        global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount, headerlist, file
        index = 0

        file, _ = QFileDialog.getOpenFileName(self,"Open Data File", "","Text Files (*.txt)") # Retrieves the name of selected file
        if file: # If a file was picked, TxtRead runs, else nothing happens
            TxtRead(file) # Passes name of file for TxtRead to open

            self.tabulate()

            for index in range(len(headerlist)):
                if headerlist[index] == 'Date ':
                    headerlist = np.delete(headerlist, index)
                    break
                else: index += 1

            self.plotBox1.addItems(headerlist)
            self.plotBox2.addItems(headerlist)


    def on_plot_button_clicked(self):
        #global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount, headerlist, file
        try:
            if file:
                styles = {"color": "k", "font-size": "8pt"}
                self.graphWidget.clear()
                pen1 = pg.mkPen(color='r', width=5)
                pen2 = pg.mkPen(color='b', width=5)
                self.stringaxis = pg.AxisItem(orientation='bottom')

                if self.date_check == True:
                    self.x = dict(enumerate(daytab))
                    self.stringaxis.setTicks([self.x.items()])
                    self.graphWidget.plotItem.setAxisItems(axisItems = {'bottom' : self.stringaxis})
                    self.x = list(self.x.keys())

                else:
                    #self.stringaxis.setTicks(None)
                    self.graphWidget.plotItem.setAxisItems(axisItems = {'bottom' : self.stringaxis})
                    self.x = dayplot

                if(self.plotBox1.currentText() != 'Left Y Axis Variable' and self.plotBox2.currentText() != 'Right Y Axis Variable'):
                    self.graphWidget.plot(self.x, self.y1, name=self.varname1, pen=pen1)
                    self.graphWidget.plot(self.x, self.y2, name=self.varname2, pen=pen2)
                    self.graphWidget.setLabel("bottom", "Time, days", **styles)
                    self.graphWidget.setLabel("left", self.varname1, **styles)
                    self.graphWidget.setLabel("right", self.varname2, **styles)

        except NameError:
            pass


    def on_save_button_clicked(self):
        #global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount, header, file

        try:
            if file:
                savefile, _ = QFileDialog.getSaveFileName(self, "Save Data File", "","Text FIles (*.txt)")
                if len(savefile) == 0:
                    pass
                else:
                    f = open(savefile,"w")
                    f.write(header+'\n')
                    for i in range(daycount): #increments for the number of days in data
                        f.write("%s " % daytab[i])
                        f.write("%f " % Vmax_Est_avg[i])
                        f.write("%f " % Area_avg[i])
                        f.write("%f " % OCV_time_avg[i])
                        f.write("%f " % Tolerance_avg[i])
                        f.write("%f " % Vmin_avg[i])
                        f.write("%f " % alpha1_avg[i])
                        f.write("%f " % Vmin_Est_avg[i])
                        f.write("%f " % prev_discharge_time_avg[i])
                        f.write("%f " % DischargeArea_avg[i])
                        f.write("%f\n" % Temp_avg[i])

                f.close()

        except NameError:
            pass


    def on_delete_button_clicked(self):
        try:
            print("click!")

        except NameError:
            pass

    def check_date_view(self, s):
        try:
            if file:
                if s == 2: # If the box is checked
                    self.date_check = True
                else:
                    self.date_check = False

        except NameError:
            pass

    def check_box1(self):
        index = self.plotBox1.currentIndex() # Index will be subtracted by 1 in order to account for default Items in combo box (left/right variable)

        try:
            if headerlist[index-1] == 'Vmax_Est ':
                self.y1 = Vmax_Est_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'Area ':
                self.y1 = Area_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'OCV_time(s) ':
                self.y1 = OCV_time_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'Tolerance ':
                self.y1 = Tolerance_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'Vmin ':
                self.y1 = Vmin_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'alpha1 ':
                self.y1 = alpha1_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'Vmin_Est ':
                self.y1 = Vmin_Est_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'prev_discharge_time ':
                self.y1 = prev_discharge_time_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'DischargeArea ':
                self.y1 = DischargeArea_avg
                self.varname1 = headerlist[index-1]
            elif headerlist[index-1] == 'Ambient_Temperature ':
                self.y1 = Temp_avg
                self.varname1 = headerlist[index-1]
            else:
                print("Problem!")

        except NameError:
            pass


    def check_box2(self):
        index = self.plotBox2.currentIndex() # Index will be subtracted by 1 in order to account for default Items in combo box (left/right variable)

        try:
            if headerlist[index-1] == 'Vmax_Est ':
                self.y2 = Vmax_Est_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'Area ':
                self.y2 = Area_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'OCV_time(s) ':
                self.y2 = OCV_time_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'Tolerance ':
                self.y2 = Tolerance_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'Vmin ':
                self.y2 = Vmin_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'alpha1 ':
                self.y2 = alpha1_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'Vmin_Est ':
                self.y2 = Vmin_Est_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'prev_discharge_time ':
                self.y2 = prev_discharge_time_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'DischargeArea ':
                self.y2 = DischargeArea_avg
                self.varname2 = headerlist[index-1]
            elif headerlist[index-1] == 'Ambient_Temperature ':
                self.y2 = Temp_avg
                self.varname2 = headerlist[index-1]
            else:
                print("Problem!")

        except NameError:
            pass


    def tabulate(self):
        global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount, headerlist

        self.tableWidget.setRowCount(len(Temp_avg))
        self.tableWidget.setColumnCount(len(headerlist))
        self.tableWidget.setHorizontalHeaderLabels(headerlist)

        for row_ind in range(len(Temp_avg)):
            self.tableWidget.setItem(row_ind, 0, QTableWidgetItem(str(daytab[row_ind])))
            self.tableWidget.setItem(row_ind, 1, QTableWidgetItem(str(Vmax_Est_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 2, QTableWidgetItem(str(Area_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 3, QTableWidgetItem(str(OCV_time_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 4, QTableWidgetItem(str(Tolerance_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 5, QTableWidgetItem(str(Vmin_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 6, QTableWidgetItem(str(alpha1_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 7, QTableWidgetItem(str(Vmin_Est_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 8, QTableWidgetItem(str(prev_discharge_time_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 9, QTableWidgetItem(str(DischargeArea_avg[row_ind])))
            self.tableWidget.setItem(row_ind, 10, QTableWidgetItem(str(Temp_avg[row_ind])))


def TxtRead(file):
    global Vmax_Est_avg, Area_avg, OCV_time_avg, Tolerance_avg, Vmin_avg, alpha1_avg, Vmin_Est_avg, prev_discharge_time_avg, DischargeArea_avg, Temp_avg, daytab, dayplot, daycount, header, headerlist
    f = open(file)
    line = f.readline()

    day = Time = Vmax_Est = Area = OCV_time = Tolerance = Vmin = alpha1 = Vmin_Est = prev_discharge_time = DischargeArea = Temp = np.array([])
    Vmax_Est_avg = Area_avg = OCV_time_avg = Tolerance_avg = Vmin_avg = alpha1_avg = Vmin_Est_avg = prev_discharge_time_avg = DischargeArea_avg = Temp_avg = np.array([])
    dayplot = daytab = np.array([])
    daycount = 0

    fields = line.split(' ')
    n_cols = 13 #number of columns from which to extract data
    headerlist = np.array([]) #list of header titles taken from data file
    for i in range(0, n_cols-1):
        if str(fields[i].split()[0]) != 'Time':
            headerlist = np.append(headerlist, "%s " % str(fields[i].split()[0]))
    header = ''.join(headerlist) #makes header titles into single line for txt file writing

    while line:
        fields = line.split(' ') #splits each row into columns
        if 'Date' in line: #if there is "Date" in the row, indicates header row and will be skipped
            line = f.readline() #this will skip the line
            continue
        #hoping to find way to automate this - generate names from headerlist strings, piggyback on n_cols iteration?
        day = np.append(day, str(fields[0].split()[0]))

        if len(day) == 1: #will fill value of daysave on iteration before next if loop
            daysave = fields[0].split()[0]

        if day[len(day)-1] != daysave: #check if day has changed
            Vmax_Est_avg = np.append(Vmax_Est_avg, np.mean(Vmax_Est))
            Area_avg = np.append(Area_avg, np.mean(Area))
            OCV_time_avg = np.append(OCV_time_avg, np.mean(OCV_time))
            Tolerance_avg = np.append(Tolerance_avg, np.mean(Tolerance))
            Vmin_avg = np.append(Vmin_avg, np.mean(Vmin))
            alpha1_avg = np.append(alpha1_avg, np.mean(alpha1))
            Vmin_Est_avg = np.append(Vmin_Est_avg, np.mean(Vmin_Est))
            prev_discharge_time_avg = np.append(prev_discharge_time_avg, np.mean(prev_discharge_time))
            DischargeArea_avg = np.append(DischargeArea_avg, np.mean(DischargeArea))
            Temp_avg = np.append(Temp_avg, np.mean(Temp))
            daytab = np.append(daytab, daysave) #saves day in yyyy-mm-dd format for storage text file
            dayplot = np.append(dayplot, daycount) #saves the day number, used for plotting
            Vmax_Est = Area = OCV_time = Tolerance = Vmin = alpha1 = Vmin_Est = prev_discharge_time = DischargeArea = Temp = np.array([]) #clears array; only keeps values for one day
            daycount += 1

        Vmax_Est = np.append(Vmax_Est, float(fields[2].split()[0]))
        Area = np.append(OCV_time, float(fields[3].split()[0]))
        OCV_time = np.append(OCV_time, float(fields[4].split()[0]))
        Tolerance = np.append(Tolerance, float(fields[5].split()[0]))
        Vmin = np.append(Vmin, float(fields[6].split()[0]))
        alpha1 = np.append(alpha1, float(fields[7].split()[0]))
        Vmin_Est = np.append(Vmin_Est, float(fields[8].split()[0]))
        prev_discharge_time = np.append(prev_discharge_time, float(fields[9].split()[0]))
        DischargeArea = np.append(DischargeArea, float(fields[10].split()[0]))
        Temp = np.append(Temp, float(fields[11].split()[0]))

        daysave = day[len(day)-1]
        line = f.readline() #reads next line of text file, does above code for each line of the file

    Vmax_Est_avg = np.append(Vmax_Est_avg, np.mean(Vmax_Est))
    Area_avg = np.append(Area_avg, np.mean(Area))
    OCV_time_avg = np.append(OCV_time_avg, np.mean(OCV_time))
    Tolerance_avg = np.append(Tolerance_avg, np.mean(Tolerance))
    Vmin_avg = np.append(Vmin_avg, np.mean(Vmin))
    alpha1_avg = np.append(alpha1_avg, np.mean(alpha1))
    Vmin_Est_avg = np.append(Vmin_Est_avg, np.mean(Vmin_Est))
    prev_discharge_time_avg = np.append(prev_discharge_time_avg, np.mean(prev_discharge_time))
    DischargeArea_avg = np.append(DischargeArea_avg, np.mean(DischargeArea))
    Temp_avg = np.append(Temp_avg, np.mean(Temp))
    daytab = np.append(daytab, daysave) #saves day in yyyy-mm-dd format for storage text file
    dayplot = np.append(dayplot, daycount) #saves the day number, used for plotting
    Vmax_Est = Area = OCV_time = Tolerance = Vmin = alpha1 = Vmin_Est = prev_discharge_time = DischargeArea = Temp = np.array([]) #clears array; only keeps values for one day
    daycount += 1
    f.close()


app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec_()
