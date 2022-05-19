import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
import email_setup


class Month(QWidget):
    def __init__(self):
        super().__init__() #inherits from qwidget
        self.create_ui()   #creates ui

    def create_ui(self):
        self.label = QLabel('', self) #label for later
        self.button_save = QPushButton('Save Results')
        self.button_graph = QPushButton('View Line Graph') #creating buttons
        self.button_menu = QPushButton('Menu')

        horiz = QHBoxLayout() #horizontal box layout
        horiz.addStretch(2)
        horiz.addWidget(self.button_save)
        horiz.addWidget(self.button_graph) #adding buttons
        horiz.addWidget(self.button_menu)

        vert = QVBoxLayout() #vertical box layout
        vert.addStretch(2)
        vert.addLayout(horiz) #putting horiz layout into vertical box
        vert.addWidget(self.label) #adding label

        self.setLayout(vert) #sets main layout to finished box layout

        self.setGeometry(400,200,150,50)
        self.setWindowTitle('Results by Month') #titling, sizing, and showing window
        self.show()

        self.button_save.clicked.connect(self.save_file)
        self.button_graph.clicked.connect(self.show_graph) #functionality for buttons
        self.button_menu.clicked.connect(self.menu)
    
    def save_file(self):
        path, ok = QInputDialog.getText(self, 'File Path', 'Enter save location:') #option for saving to new file

        if ok:
            data.index = data['Date']
            by_month = data.resample('M').sum() #sampling data by month
            out = str(path)
            by_month.to_excel(out+'.xlsx', 
                                float_format='%.2f', header=True, index=True) #pandass to_excel method for saving to excel files
            self.label.setText('File Saved') #confirmation
            self.label.move(50,150)

    def show_graph(self):
        data.index = data['Date'] #group by date
        month_sort = data.resample('M').sum() #resample and sum by month
        months = month_sort.index
        costs = month_sort['Amount'] #setting variables for graph

        plt.figure(figsize=(15,8)) #creating figure for plotting graph
        plt.subplot(111) #111 is line graph
        plt.plot(months, costs)
        plt.suptitle('Monthly Spending Totals')
        plt.xticks(months) # x axis ticks by month
        plt.show()

        self.close()

    def menu(self):
        self.menu = Window() #open menu window
        self.menu.show()
        self.close() #close self

class Category(QWidget): #by category class
    def __init__(self):
        super().__init__()
        self.create_ui()
    
    def create_ui(self):
        self.label = QLabel('', self) #label for later
        self.button_save = QPushButton('Save Results')
        self.button_graph = QPushButton('View Bar Graph') #creating buttons
        self.button_menu = QPushButton('Menu')

        horiz = QHBoxLayout() #horizontal layout
        horiz.addStretch(2)
        horiz.addWidget(self.button_save)
        horiz.addWidget(self.button_graph) #adding button functions
        horiz.addWidget(self.button_menu)

        vert = QVBoxLayout() #vertical box
        vert.addStretch(2)
        vert.addLayout(horiz) #putting horiz layout into vertical box
        vert.addWidget(self.label) #adding label

        self.setLayout(vert) #sets main layout to finished box layout

        self.setGeometry(400,200,250,150)
        self.setWindowTitle('Results by Category') #setting title and showing window
        self.show()

        self.button_save.clicked.connect(self.save_file)
        self.button_graph.clicked.connect(self.show_graph) #adding button functionality
        self.button_menu.clicked.connect(self.menu)
    def save_file(self):
        path, ok = QInputDialog.getText(self, 'File Path', 'Enter save location:') # option for saving to new file

        if ok:
            by_category = data.groupby('Category').sum() #grouping and summing by category
            out = str(path)
            by_category.to_excel(out+'.xlsx',
                                float_format='%.2f', header=True, index=True) #to_excel method
            self.label.setText('File Saved') # save confirmation
            self.label.move(50,150)

    def show_graph(self):
        by_category = data.groupby('Category').sum() #group and sum by category
        x_labels = by_category.index
        y_labels = by_category['Amount'] # assinging variables for graph

        f, axis = plt.subplots(figsize=(15,8)) #plt subplot
        bars = axis.bar((np.arange(len(y_labels))), y_labels, 1.0, color='red') # plotting bar graph with sized and colored labels
        axis.set_title('Spending by Category')
        axis.set_xticks((np.arange(len(y_labels)))) # assigning spacing
        axis.set_xticklabels(x_labels)
        axis.set_ylabel('Amount')

        for bar in bars: #loop to label data
            h = round(bar.get_height(),2) #assigning bar height rounded to 2 decimals
            axis.annotate("{:.2f}".format(h), xy=(bar.get_x() + bar.get_width() / 2, h), #formats and offsets labels
            xytext=(0,3), textcoords = "offset points", ha='center',va='bottom' )
        
        plt.show() #showing graph
        self.close() #closing class ui

    def menu(self):
        self.menu= Window() # open and show menu window
        self.menu.show()
        self.close() # close self

class Window(QWidget):
    def __init__(self):
        super().__init__() #inherits from qwidget
        self.create_ui()
    
    def create_ui(self):
        drop = QComboBox(self)
        drop.addItems(["View by Category", "View by Month"]) #drop down menu choices
        drop.move(60,60)

        drop.activated[str].connect(self.selection) #adding functionality to dropdown

        self.setGeometry(400,200,300,150)
        self.setWindowTitle("Feature Menu") #titling, sizing, and showing window
        self.show()
    
    def selection(self, select):
        if select == "View by Category": #simple if else for parsing dropdown box choice
            self.category = Category()
            self.category.show() #open and show category window
            self.close() #close Window display
        else:
            self.month = Month()
            self.month.show() #open and show month window
            self.close()

class Screen(QWidget): #setup data
    def __init__(self):
        super().__init__() #inherits from qwidget
        self.create_ui()

    def create_ui(self):
        label = QLabel('Continue with Budget.xlsx?') # prompt for default file
        label.move(20,10)

        self.button_cont = QPushButton('Continue')
        self.button_new = QPushButton('New File') # continue with default or enter new path

        horiz = QHBoxLayout() # horizontal box layout
        horiz.addWidget(label)
        horiz.addStretch(2)
        horiz.addWidget(self.button_cont) # adding buttons
        horiz.addWidget(self.button_new)

        vert = QVBoxLayout() # vertical box layout
        vert.addStretch(2)
        vert.addLayout(horiz) # adding horizontal to veritcal

        self.setLayout(vert)
        self.setGeometry(500,200,150,50)
        self.setWindowTitle('Budgeeto') # setting layout and labeling window 
        self.show()

        self.button_cont.clicked.connect(self.create_database) # adding functionality to buttons
        self.button_new.clicked.connect(self.create_new)

    def create_database(self):
        global data #global variable for dataframe
        data = pd.read_excel('Budget.xlsx', sheet_name='Data') # pandas exel reading method
        data['Date'] = pd.to_datetime(data['Date']) #converts dates to datetime
        self.update_data() #fetching and adding data from email
        self.menu = Window() 
        self.menu.show() # creating and showing first menu
        self.close()
        return data

    def create_new(self):
        global data
        fname,ok = QInputDialog.getText(self, 'File Path', 'Enter file path:') #input for new path

        if ok:
            data = str(fname) # if valid input read from new file
            data = pd.read_excel(data)
            data['Date'] = pd.to_datetime(data['Date']) # convert to datetime

            self.menu = Window() # go to next menu
            self.menu.show()
            self.close() #close self
            return data

    def update_data(self):
        #get data from email
        #apend data to dataframe, save to excel file
        #return new dataframe
        newest_mail = email_setup.get_new_emails()
        for m in newest_mail: #[date, place, description, category, amount]
            m = m.split(',')
            temp_dict = {'Date': m[0], 'Place':m[1], 'Description':m[2], 'Category':m[3],'Amount':m[4]}
            data.append(temp_dict, ignore_index=True) #for loop to append new data to dataframe
        return data



if __name__ == '__main__':
    main = QApplication(sys.argv) #app object
    Screen = Screen()  #starting window
    sys.exit(main.exec()) #ends if closed or exit called



