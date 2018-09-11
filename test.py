# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 08:09:28 2018

@author: matev
"""

#Import Libraries
#---------------------------------------
import mysql.connector as linky 
import pandas as pd
import matplotlib.pyplot as plt
import random

#Connecting Server
#---------------------------------------
cnx = linky.connect(host='212.235.187.48',  user='pvtest', passwd='testpv123!', db='pvtest')
cursor = cnx.cursor(buffered=True)


#this snippet gives us all the tables avaliable to us
cursor.execute("USE pvtest")
cursor.execute("SHOW TABLES")    
tables = cursor.fetchall()  
print(tables)



#this part of the code retrieves all the data in the selected table
query = "SELECT * FROM view_results_all"
cursor.execute(query)
list_query = list()
for i in cursor:
    list_query.append(i)

print(len(list_query))

#To create the data frame we also need the column names      
cursor.execute("SHOW columns FROM view_results_all")
colNames = [column[0] for column in cursor]

cursor.close()



#Transforming to DataFrame
#---------------------------------------
df_query = pd.DataFrame(list_query,columns = colNames)

#this part of the code selects a random module
Modules = list(set(df_query.Module))
activeMod = random.choice(Modules)


resSet = list(set(df_query[df_query['Module']==activeMod].idResults))
resSet = random.choice(resSet)


cursor2 = cnx.cursor(buffered=True)
cursor2.callproc('GetIVCurve',[resSet,])

for result in cursor2.stored_results():
    temp_row = result.fetchall()
    
colNames = ['U','I']


#Close the server
#---------------------------------------

cursor2.close()
cnx.close()

df_query['fix'] = df_query['Pmpp']*1000/df_query['Irr']

df_ui = pd.DataFrame(temp_row,columns = colNames )
plt.plot(df_ui.U,df_ui.I)


####
linearizacija = df_query[df_query['Module']==activeMod].sort_values(by=['Tmodule'])
a = plt.figure()
ax1 = a.add_subplot(111)
ax1.scatter(linearizacija.Tmodule,linearizacija.fix)
plt.show()


x = linearizacija.Tmodule.values
y = linearizacija.fix.values

from sklearn import linear_model
regr = linear_model.LinearRegression()
regr.fit(x.reshape(-1, 1), y.reshape(-1, 1))

print("The euqation is y = " + str(regr.coef_[0]) + " *x +(" + str(regr.intercept_) + ")")

y_fit = list(map(lambda to : to * regr.coef_[0] + regr.intercept_,x))
ax1.plot(linearizacija.Tmodule,y_fit,'r')

import seaborn as sns
plt.figure()
sns.regplot('Tmodule','fix',data=linearizacija)


