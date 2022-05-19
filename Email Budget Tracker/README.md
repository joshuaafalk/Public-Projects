# Email Budget Tracker - Budgeeto  
### This folder contains four files:  
- Budget.xlsx
-  ebudget.py 
-  email_setup.py   
-  README.md
 
**Budget.xlsx:**  
  A sample Excel spreadsheet containing data in the correct format for the program.
  
  
**ebudget.py:**  
This file is used to connect to a mail service and retrieve emails with the subject line "Budget.Program". Once it has collected and decoded these emails, it returns
them as a list that is added to the data frame and saved into the spreadsheet.
  

**ebudget.py:**  
  This file contains the main function of this program. It uses the PyQt5 library to create a UI for viewing budgeting data both by Category and by Month. It holds data in a pandas data frame, which is pulled from and saved into
  an Excel spreadsheet. edbudget uses the NumPy and matplotlib libraries to graph data.
  
 ## Walk-through:  
 #### Upon running the __main__ function in the file 'ebudget.py', a prompt for file selection is shown:  
 <p align="center">
  <img 
    src="https://user-images.githubusercontent.com/98131317/168129593-4d3fd5e2-7d69-4592-97c0-af040c61d6d1.png"
  > 
</p>  
Budget.xlsx will always be the default file, to use another select 'New File' and enter the file path.
  
#### **Once a file has been chosen, the view type must be selected:**    
<p align="center">
  <img 
    src="https://user-images.githubusercontent.com/98131317/168132628-878a0cc3-3162-42db-b8f9-a56b6958856a.png"
  >
</p>  

#### Both choices lead to a final menu:  
<p align="center"> 
  <img
    src="https://user-images.githubusercontent.com/98131317/168138580-7ae6369c-c409-4f69-8a42-2220710b9700.png">    
</p>

<p align="center">
  <img
    src="https://user-images.githubusercontent.com/98131317/168138777-d1340bd9-ac03-4151-9f85-407d947c1225.png">  
</p>


#### Bar Graph for Spending by Category:  
<p align="center"> 
  <img
    src="https://user-images.githubusercontent.com/98131317/168896415-ac4dee80-1f6c-4fb2-bffd-969840ed3a2e.png" width="600">    
</p>  

#### Line Graph for Monthly Spending:  
<p align="center"> 
  <img
    src="https://user-images.githubusercontent.com/98131317/168895721-e5ddd518-38d4-448a-9a15-11f1c0f13f4e.png" width="600">    
</p>  
  
  The graphs can be saved as a png or viewed and closed to return to the previous menu window.  
  
  ## Under the Hood  
  The data is held in a pandas data frame during runtime, which allows for easy manipulation of data in a two-dimensional setting. The data frame for the default file is created by the 
create_database method belonging to the Screen class.   
  
![Screenshot (178)](https://user-images.githubusercontent.com/98131317/168905890-edcbbf4d-4060-4341-8e35-cd98d7f872b5.png)  

  Because the data variable is not going to be modified beyond this point, it can safely be implemented as a global variable. Additionally, the update_data function invokes the email_setup file.
    
![Screenshot (186)](https://user-images.githubusercontent.com/98131317/169119034-a0c5b018-beb4-4b4f-aa7b-45963d2d74d8.png)

 The main packages used to connect and interact with the email server are IMAP4_SSL from the imaplib library and the email library. IMAP4_SSL creates an encrypted connection to a server while the email library converts email contents from bytes into a usable object.
  
    
    
![Screenshot (182)](https://user-images.githubusercontent.com/98131317/168909571-7e3beef3-2884-48d7-ae15-99ab7b092323.png)
  
  Once an IMAP4_SSL connection has been created and a uid list of emails sent in the last day is fetched, a loop walks through each new email and retrieves its contents using the
  IMAP4_SSL object. After its contents have been fetched, the message must be parsed so attachments do not cause issues and text can be extracted from any HTML formatting. Finally, the message
  is decoded and stripped of carriage returns and newline characters.  
   
    
![Screenshot (184)](https://user-images.githubusercontent.com/98131317/168910225-8114cb28-5805-4b01-ad34-d80cfd433a9a.png)


The graphs are created using NumPy and matplotlib. The data is grouped by category or by month, depending on which is selected. Once the data is in the correct format, it is graphed and labeled. The Category data is graphed using a matplotlib bar graph while the Month data is graphed using a matplotlib line graph. 

#### By Category:  

![Screenshot (188)](https://user-images.githubusercontent.com/98131317/169121268-4ec1b405-e02c-449d-bdf1-ac19153c46d0.png)

#### By Month:  

![Screenshot (190)](https://user-images.githubusercontent.com/98131317/169126013-28fe668a-97fd-4979-8ad1-fbecb4961cd1.png)


