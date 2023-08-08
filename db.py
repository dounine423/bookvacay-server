import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB_DATABASE')
HOST=os.getenv('DB_HOST')

def getAllDataFromDB(query):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    mycursor = mydb.cursor()


    mycursor.execute(query)

    myresult = mycursor.fetchall()

    results = []
    for x in myresult:
        results.append(x)

    return results

def getOneDataFromDB(query):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    mycursor = mydb.cursor()


    mycursor.execute(query)

    myresult = mycursor.fetchone()

    
    return myresult

def selectQuery(select,table,where=None,orderBy=None,direction=None,limit=None,offset=None,groupBy=None):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    if where==None:
        query=f"select {select} from {table}"
    else:
        query=f"select {select} from {table} where {where}"
    if groupBy!=None:
        query +=f" Group By {groupBy}"
    if orderBy!=None:
        query+=f" order by {orderBy}"
    if direction!=None:
        query+=f" {direction}"
    if limit !=None:
        query+=f" limit {limit}"
    if offset!=None:
        query +=f" offset {offset}"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    result=mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return result

def updateQuery(table,update,where):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    query=f"Update {table} set {update} where {where}"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()
    mycursor.close()
    mydb.close()

def insertQuery(table,fields,values):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    query=f"insert into {table} ( {fields} ) values ( {values} )"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()
    mycursor.close()
    mydb.close()

def insertQueryWithRetValue(table,fields,values):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    query=f"insert into {table} ( {fields} ) values ( {values} )"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()
    result=mycursor.lastrowid
    mycursor.close()
    mydb.close()
    return result

def ExecuteQuery(query):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    mycursor = mydb.cursor()
    mycursor.execute(query)
    mydb.commit()
    mycursor.close()
    mydb.close()

def InsertData(query):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user=USER,
        password=PASSWORD,
        database=DB,
    )
    mycursor = mydb.cursor()
    result = False
    try:
        mycursor.execute(query)
        result = True
    except Exception as e:
        print(e)  
    mydb.commit()      
    return result

