import mysql.connector as mycon
import csv
mydb = mycon.connect(host = "localhost", 
port = 3205,
user = "root",
password = "root")
mycursor = mydb.cursor(buffered=True)

print('setup')
mycursor.execute("show databases")
db = ('test',)
if db not in mycursor.fetchall():
    mycursor.execute("create database test;")
    print("database 'test' has been created")
else:
    print('database test already exists')
    
mycursor.execute("use test")

mycursor.execute('show tables;')
db = ('student_details',)
if db not in mycursor.fetchall():
    mycursor.execute("create table student_details (name VARCHAR(255), password VARCHAR(255))")
    mycursor.execute("show tables")
else:
    print('table student_details already exists')

    
mycursor.execute('use test;')
mycursor.execute('show tables;')
db = ('book',)
if db not in mycursor.fetchall():
    mycursor.execute("create table book (book_id int AUTO_INCREMENT Primary Key, book_name VARCHAR(255));")
    print("table 'book' has been created")
else:
    print('table book already exists')


mycursor.execute('use test;')
mycursor.execute('show tables;')
db = ('booksavailable',)
if db not in mycursor.fetchall():
    mycursor.execute("create table booksavailable (book_id int AUTO_INCREMENT Primary Key, book_name VARCHAR(255));")
    print("table 'booksavailable' has been created")
else:
    print('table booksavailable already exists')

mycursor.execute('use test;')
mycursor.execute('show tables;')
db = ('lending',)
if db not in mycursor.fetchall():
    mycursor.execute("create table lending (date VARCHAR(255),name VARCHAR(255),book_name VARCHAR(255))")
    print("table 'lending' has been created")
else:
    print('table lending already exists')


book = ["The Hobbit","The Wheel of Time","No Longer Human","Born a Crime"]
mycursor.execute('select * from book;')
a = len(mycursor.fetchall())
if a == 0:
    for i in book:
        sql = "Insert into book(book_name) Values('%s');"%i
        mycursor.execute(sql)
        sql = "Insert into booksavailable(book_name) Values ('%s');"%i
        mycursor.execute(sql)
        mydb.commit()
print(mycursor.rowcount)

filename = 'damaged_books.csv'
header = ["Book-ID","Book Name"]
with open(filename,'w',newline='') as damaged_books:
    csvwriter = csv.writer(damaged_books)
    csvwriter.writerow(header)
    csvwriter.writerows([[1,"Cat's Road"],[2,"Blank Canvas"]])


"""mycursor.execute('select * from booksavailable;')
b = mycursor.fetchall()
if a != None and a != b:
    for i in range(a):
        print()
        idnum = i[0]
        book_name = i[1]
        sql = "Insert into booksavailable (book_id,book_name) Values (%s,%s)"
        values = idnum,book_name
        print(sql,values)
        mycursor.execute(sql,values)
        mydb.commit()"""