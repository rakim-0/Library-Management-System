#Library Management System
#Rakim Middya 12-B

import mysql.connector as mycon
from tabulate import tabulate
import pickle
import datetime as dt
import os
import csv
import pandas as pd
import sys




mydb = mycon.connect(host = "localhost",
port = 3205,
user="root",
password = "root",
database = "test")
mycursor = mydb.cursor(buffered=True)
mycursor.execute('use test;')

#the first thing seen by the user
def startscreen():
    print(' ===========================================')
    print("|              School Library               |")
    print(' ===========================================\n')
    
    print('Menu:\n—————\n')
    print('1. Login')
    print('2. Register')
    print('3. Admin Login')
    print('4. Exit\n')
    while True:
        choice = input("enter your choice(number): ")
        if choice == '1':
            login()
        elif choice == '2':
            register()
        elif choice == '3':
            adminlogin()
        elif choice == '4':
            print('Thank you for using the School Library!')
            exit()
        else:
            print('Please choose a number from 1,2,3,4\n')

#login/registration: sql based
def login():
    print('\nLogin:\n—————\n')
    global username 
    username = input("Username: ")
    password = input("Password: ") 
    mycursor.execute('use test;')
    mycursor.execute('select * from student_details;') 
    t1 = dict(mycursor.fetchall())
    if password == t1.get(username):
        print('\nHello,',username+'!')
        menu()
    else:
        choice = input('Either the username or the password is wrong\nWould you like to continue to try logging in?(Y or N): ')
        if choice.lower() == 'y':
            login()
        elif choice.lower() == 'n':
            startscreen()

def register():
    print('\nRegistration   \n————————————\n')
    while True:
        username = input('Enter desired Username: ')
        mycursor.execute('use test;')
        mycursor.execute('Select * from Student_Details;')
        if username in dict(mycursor.fetchall()):
            choice = input('Sorry but this username already exists in the database.Please contact the librarian for furthur help\nWould you like to go to login screen?(Y or N): ')
            if choice.lower() == 'y':
                login()
            elif choice.lower() == 'n':
                startscreen()

        password = input('Enter password: ')
        sql = "Insert into student_details (name,password) Values (%s,%s)"
        values = username,password
        mycursor.execute(sql, values)
        mydb.commit()
        print('Account', username,'is created successfully!')
        input("Press enter to continue")
        login()

def adminlogin():
    if os.path.isfile('admin.txt'):
        print('\nAdmin Login\n——————————\n')
        global username
        while True:
            username = input('enter username: ')
            password = input('enter password: ')
            with open('admin.txt','rb') as f:
                data = pickle.load(f)
                if username in data:
                    if data[username] == password:
                        adminmenu()
                if username not in data:
                    print('Either username or password is incorrect.\nWould you like to continue trying logging in?')
                    choice = input('Choice (y or n): ')
                    choice = choice[0]
                    while True:
                        if choice.lower() == 'n':
                            startscreen()
                        elif choice.lower() == 'y':
                            break
                        else:
                            print('Please either choose either y(es) or n(o).')
    else:
        adminregistration()

def adminregistration():
    fad = len('Admin Registration')*'—'
    print('\nAdmin Registration\n%s\n'%fad)
    global username
    username = input('enter username: ')
    password = input('enter password: ')
    dict1 = {}
    f = open('admin.txt','wb')
    dict1[username]=password
    pickle.dump(dict1,f)
    f.close()
    adminlogin()

def menu():
    global username
    while True:
        choice = input('\nWelcome to the school library\n1.Book List\n2.Issue a book\n3.Return a book\n4.Go back to the login screen\n5.Exit\nChoose a number(1,2,3,4,5): ')
        if choice == '1':
            showbooks()
        elif choice == '2':
            lendingdetails(username) 
        elif choice == '3':
            return_book(username)
        elif choice == '4':
            print("\n")
            startscreen()
        elif choice == '5':
            print('Thank you for using the school library!')
            exit()
        else:
            print('please input either 1 or 2 or 3 or 4 or 5')

def showbooks():
    choice = '0'
    while True:
        if choice == '0': 
            choice = input('\nWould you like to see-\n1) Only the available books for lending\nor\n2) All the books that our library has to offer\nChoice(1 or 2): ')
        if choice == '1':
            mycursor.execute('select book_name from booksavailable')
            print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
            break
        elif choice == '2':
            mycursor.execute('select * from book')
            print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
            break
        else:
            choice = input('Please choose either 1 or 2.')

    input('\npress enter to back to the menu\n')
    menu()

def lendingdetails(name = 'abc'):
    if name == 'abc':
        name = input('Enter the name of the student: ')
    mycursor.execute("select * from lending where name ='%s';"%name)

    if len(mycursor.fetchall())!= 0:
        print('\nYou have already issued a book.')
        print('Please return it before trying to issue another.')
        input('Returning to the menu...(press enter to continue)')
        menu()
    print('Books Available\n---------------')
    mycursor.execute('Select book_name from booksavailable;')
    print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
    mycursor.execute("Select * from lending where name ='%s';"%name)
    book_name = input('Enter name of the book: ')
    mycursor.execute("Select * from booksavailable where book_name ='%s';"%book_name)
    if(len(mycursor.fetchall()) != 0):
        date = dt.datetime.now().strftime('%d'+'/'+'%m'+'/'+'%Y')
        values = date,name,book_name
        sql = "Insert into lending (date,name,book_name) Values (%s,%s,%s)"
        mycursor.execute(sql, values)
        print(name,'has taken',book_name,'on',date)
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%book_name)
        mydb.commit()
        input('\npress enter to back to the menu\n')
    else:
        mycursor.execute("Select * from book where book_name ='%s'"%book_name)
        if(len(mycursor.fetchall()) != 0):
            print("I am sorry but the book requested is currently lent out to someone. Please try at a later date.")
            input("Press enter to continue")
        else:
            print(book_name,"doesn't exist in our library. Please ask the Librarian if you would like it to be included.") 
            input("Press enter to continue")
    mydb.commit()
    menu()

def return_book(name = 'abc'):
    print('\nBook return\n-----------\n')
    if name == 'abc':
        name = input('enter your name/name of the student: ')
    
    mycursor.execute("Select book_name from lending where name='%s';"%name)
    data = mycursor.fetchall()
    if(len(data)==0):
        print("You haven't taken any book yet. Please issue a book before choosing three")
        input('Returning to menu....')
        menu()
    else:
        book_name = data[0][0]
        days = dayslent(name)
        if days < 7:
            choice = input('Would you like to return %s\nChoice(y(es) or n(o)): '%book_name)
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name[1:-1]:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s sucessfully'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
                mydb.commit()
                menu()
        else:
            print('You have incurred a fine of %s'%str((days-7)*2)+f" AED (2*({days}-7)) for not returning the book on time.\nYou are not allowed to take another book until you pay it. Please contact the librarian for furthur instruction.\n")
            input('Returning to the menu...(press enter to continue)')
            menu()


    


def adminmenu(foo=None):
    def menu():
            print('\n1. See pending books')
            print('2. Lend a book')
            print('3. Add a new book to the database')
            print('4. Edit info of Existing Books')
            print('5. Return a book')
            print('6. Go back to the Startscreen')
            print('7. Show books')
            print('8. Damaged Books')
            print('9. Delete Books')
            print('10. Exit\n')
            choice = input("enter your choice: ")
            if choice == '1':
                see_lent()
            elif choice == '2':
                adminlendingdetails()
            elif choice == '3':
                enterbookinfo()
            elif choice == '4':
                updatebookinfo()
            elif choice == '5':
                adminreturn_book()
            elif choice == '6':
                startscreen()
            elif choice == '7':
                adminshowbooks()
            elif choice == '8':
                damagedbooks()
            elif choice == '9':
                deletebooks()
            elif choice == '10':
                print('Thank you for using the school library!')
                exit()
            
            else:
                print("\nPlease choose a number from the following list- [1,2,3,4,5,6,7,8]: ")
                adminmenu('fdasfds')
    if foo == None:
        global username
        print('\nAdmin Menu\n——————————\n')
        print("Welcome",username)
        print('Choose a number')
        menu()
    else:
        print('\nAdmin Menu\n——————————\n')
        print('Choose a number')
        menu()

def see_lent():
    mycursor.execute("select * from lending;")
    data = mycursor.fetchall()
    if len(data) != 0:
        print(tabulate(data,headers=["Date","Name","Book Name"],tablefmt="grid"))
        input('Press enter to continue')
    else:
        print("There are no books pending!\n")
        input('Press enter to continue')
    adminmenu('x')

def enterbookinfo():
    print('\nBook Info\n')
    while True:
        book_name = input('enter name of the book: ')
        mycursor.execute('Select * from book;')
        if book_name in dict(mycursor.fetchall()):
            print('This book already exists in the database.')
            def choice():
                choice = input("\nWould you like to try a different book?\nChoice(y,n)= ")
                if choice[0].lower() == 'y':
                    enterbookinfo()
                elif choice[0].lower() == 'n':
                    adminmenu()
                else:
                    print('please either y(es) or n(o): ')
                    choice()
        sql = "Insert into book(book_name) Values ('%s');"%book_name
        mycursor.execute(sql)
        mydb.commit()

        sql = "Insert into booksavailable(book_name) Values ('%s');"%book_name
        values = book_name
        mycursor.execute(sql, values)
        mydb.commit()

        print('The entry for',book_name,'has been successfully created.\n')
        choice = input('Would you like to\n1. Add another book\n2. Go back to the menu\nChoose an option(1 or 2): ')
        if choice == '1':
            continue 
        elif choice == '2':
            adminmenu()

def updatebookinfo():
    mycursor.execute('select * from book')
    print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
    id = input('enter book ID: ')
    mycursor.execute('select book_name from book where book_id =%s' %id) 
    if len(mycursor.fetchall()) == 0:
        print('The book id entered does not exist')
        choice = input("Would you like to retype the id?\nChoice (Y(es) or N(o)): ")
        if choice.lower()[0] == 'n':
            adminmenu()
            
    mycursor.execute('select book_name from book where book_id =%s' %id) 
    book_name = mycursor.fetchall()[0][0]
    newname = input('enter new name: ')
    val = (newname,id)
    query = "Update book set book_name='%s' where book_id =%s" %val+';'
    mycursor.execute(query)
    query = "Update booksavailable set book_name='%s' where book_id =%s" %val+';'
    mycursor.execute(query)
    l1 = [["Old Name","New Name"],[book_name,newname]]
    print(tabulate(l1,headers="firstrow",tablefmt="grid"))
    choice = input('Would you like to go forward with the name change shown above?\nChoice(yes or no): ')
    while True:
        if choice[0].lower() == 'y':
            mydb.commit()
            print('%s has been successfully changed to %s'%(book_name,newname))
            input("Going back to the menu...(press enter to continue)")
            adminmenu()
        elif choice[0].lower() == 'n':
            option = input('Do you want to try again?')
            while True:
                if option[0].lower == 'y':
                    updatebookinfo()
                elif option[0].lower == 'n':
                    input("Going back to the menu...(press enter to continue)")
                    adminmenu()
                else:
                    option = input('please type either yes or no: ')

        else:
            choice = input('please type either yes or no')

def adminlendingdetails():
    name = input('Enter the name of the student: ')
    mycursor.execute("select * from lending where name ='%s';"%name)
    if len(mycursor.fetchall())!= 0:
        print('\n%s has already issued a book.'%name)
        print('Please get him or her to return it.')
        input('Returning to the menu...(press enter to continue)')
        adminmenu()
    print('Books Available\n---------------')
    mycursor.execute('Select book_name from booksavailable;')
    print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
    mycursor.execute("Select * from lending where name ='%s';"%name)
    book_name = input('Enter name of the book: ')
    mycursor.execute("Select * from booksavailable where book_name ='%s';"%book_name)
    if(len(mycursor.fetchall()) != 0):
        date = dt.datetime.now().strftime('%d'+'/'+'%m'+'/'+'%Y')
        values = date,name,book_name
        sql = "Insert into lending (date,name,book_name) Values (%s,%s,%s)"
        mycursor.execute(sql, values)
        print(name,'has taken',book_name,'on',date)
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%book_name)
        mydb.commit()
        input('\npress enter to back to the menu\n')
    else:
        mycursor.execute("Select * from book where book_name ='%s'"%book_name)
        if(len(mycursor.fetchall()) != 0):
            print("I am sorry but the book requested is currently lent out to someone. Please try at a later date.")
            input("Press enter to continue")
        else:
            print(book_name,"doesn't exist in our library.")
            input("Press enter to continue")
    mydb.commit()
    adminmenu()

def adminshowbooks(choice = '0'):
    while True:
        if choice == '0': 
            choice = input('\nWould you like to see-\n1) Only the available books for lending\nor\n2) All the books that our library has to offer\nChoice(1 or 2): ')
        if choice == '1':
            mycursor.execute('select book_name from booksavailable')
            print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
            break
        elif choice == '2':
            mycursor.execute('select * from book')
            print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
            break
        else:
            print('Please choose either 1 or 2.')

    input('\npress enter to back to the menu\n')
    adminmenu()


def adminreturn_book(name = 'abc'):
    print('Book return\n-----------\n')
    if name == 'abc':
        name = input('enter the name of the student: ')
    mycursor.execute("Select book_name from lending where name='%s';"%name)
    data = mycursor.fetchall()
    if(len(data)==0):
        print("%s hasn't taken any book yet."%name)
        input('Returning to menu....')
        adminmenu()
    else:
        book_name = data[0][0]
        days = dayslent(name)
        if days < 7:
            choice = input('Is %s returning %s?\nChoice [Y(es)/n(o)]: '%(name,book_name))
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s\nAnd the database has been updated to reflect that'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
        else:
            choice = input('Has %s paid the fine of '%name+str((days-7)*2)+' AED?\nChoice [Y(es)/n(o)]:')
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
    mydb.commit()
    adminmenu()


#new stuff

def dayslent(name):
    mycursor.execute('select date from lending where name = "%s"'%name)
    lentdate = mycursor.fetchall()[0][0]
    date = dt.datetime.strptime(lentdate,'%d'+'/'+'%m'+'/'+'%Y') 
    difference = dt.datetime.now()-date #calculates the difference
    return int(difference.days)

def damagedbooks():
    print('\nDamaged Books\n----------------\n')
    print('1. Show damaged books')
    print('2. Add damaged books')
    print('3. Remove damaged books')
    print('4. Return to menu\n')
    choice = input('Enter choice: ')
    if choice == '1':
        displaycsvtable()
    if choice == '2':
        addbook()
    if choice == '3':
        deletebooksfromcsv()
    if choice == '4':
        adminmenu()

def displaycsvtable(x=None):
    print('\nDamaged Books\n-------------')
    filename = 'damaged_books.csv'
    data = []
    with open(filename,'r',newline='') as damaged_books:
        csvreader = csv.reader(damaged_books)
        for i in csvreader:
            data.append(i)
    print(tabulate(data,headers="firstrow",tablefmt='grid'))
    if x == None:
        input('\npress enter to back to the menu\n')
        damagedbooks()
    else:
        pass


def addbook():
    filename = 'damaged_books.csv'
    with open(filename,'a',newline='') as damaged_books:
        csvwriter = csv.writer(damaged_books)
        data = pd.read_csv(filename).to_numpy()
        bookname = input("Enter bookname: ")
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%bookname)
        mydb.commit()
        bookid =  data[-1][0]+1
        csvwriter.writerow([bookid,bookname])
    input('\npress enter to back to the menu\n')
    damagedbooks()




def deletebooksfromcsv():
    filename = 'damaged_books.csv'
    displaycsvtable(1)
    data = []
    name = input("Enter the book name: ")

    with open(filename,'r',newline='') as damaged_books:
        csvreader = csv.reader(damaged_books)
        for i in csvreader:
            data.append(i)
    for i in range(len(data)):
        if data[i][1] == name:
            del data[i]
            break

    with open(filename,'w',newline='') as damaged_books:
        csvwriter = csv.writer(damaged_books)
        header = ["Serial No.","Book Name"]
        csvwriter.writerow(header)
        for i in range(1,len(data)):
            bookname = data[i][1]
            bookid =  i
            csvwriter.writerow([bookid,bookname])
    mycursor.execute("Insert into booksavailable(book_name) Values('%s');"%name)
    mydb.commit()

            
    displaycsvtable()
    input('\npress enter to back to the menu\n')
    damagedbooks()


def deletebooks():
    mycursor.execute('select * from book')
    print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
    name = input("Enter book-name: ")
    mycursor.execute(f"Delete from booksavailable where book_name = '{name}'")
    mycursor.execute(f"Delete from book where book_name = '{name}'")
    mydb.commit()
    if mycursor.rowcount != 0:
        print(f"{name} has been deleted successfully.")
        input("\npress enter to continue")
        
        adminmenu()
    else:
        print(f"{name} was not found in the database.")
        input("\npress enter to continue")
        adminmenu()

startscreen()
exit()
#Library Management System
#Rakim Middya 12-B

import mysql.connector as mycon
from tabulate import tabulate
import pickle
import datetime as dt
import os
import csv
import pandas as pd
import sys




mydb = mycon.connect(host = "localhost",
port = 3205,
user="root",
password = "root",
database = "test")
mycursor = mydb.cursor(buffered=True)
mycursor.execute('use test;')

#the first thing seen by the user
def startscreen():
    print(' ===========================================')
    print("|              School Library               |")
    print(' ===========================================\n')
    
    print('Menu:\n—————\n')
    print('1. Login')
    print('2. Register')
    print('3. Admin Login')
    print('4. Exit\n')
    while True:
        choice = input("enter your choice(number): ")
        if choice == '1':
            login()
        elif choice == '2':
            register()
        elif choice == '3':
            adminlogin()
        elif choice == '4':
            print('Thank you for using the School Library!')
            exit()
        else:
            print('Please choose a number from 1,2,3,4\n')

#login/registration: sql based
def login():
    print('\nLogin:\n—————\n')
    global username 
    username = input("Username: ")
    password = input("Password: ") 
    mycursor.execute('use test;')
    mycursor.execute('select * from student_details;') 
    t1 = dict(mycursor.fetchall())
    if password == t1.get(username):
        print('\nHello,',username+'!')
        menu()
    else:
        choice = input('Either the username or the password is wrong\nWould you like to continue to try logging in?(Y or N): ')
        if choice.lower() == 'y':
            login()
        elif choice.lower() == 'n':
            startscreen()

def register():
    print('\nRegistration   \n————————————\n')
    while True:
        username = input('Enter desired Username: ')
        mycursor.execute('use test;')
        mycursor.execute('Select * from Student_Details;')
        if username in dict(mycursor.fetchall()):
            choice = input('Sorry but this username already exists in the database.Please contact the librarian for furthur help\nWould you like to go to login screen?(Y or N): ')
            if choice.lower() == 'y':
                login()
            elif choice.lower() == 'n':
                startscreen()

        password = input('Enter password: ')
        sql = "Insert into student_details (name,password) Values (%s,%s)"
        values = username,password
        mycursor.execute(sql, values)
        mydb.commit()
        print('Account', username,'is created successfully!')
        input("Press enter to continue")
        login()

def adminlogin():
    if os.path.isfile('admin.txt'):
        print('\nAdmin Login\n——————————\n')
        global username
        while True:
            username = input('enter username: ')
            password = input('enter password: ')
            with open('admin.txt','rb') as f:
                data = pickle.load(f)
                if username in data:
                    if data[username] == password:
                        adminmenu()
                if username not in data:
                    print('Either username or password is incorrect.\nWould you like to continue trying logging in?')
                    choice = input('Choice (y or n): ')
                    choice = choice[0]
                    while True:
                        if choice.lower() == 'n':
                            startscreen()
                        elif choice.lower() == 'y':
                            break
                        else:
                            print('Please either choose either y(es) or n(o).')
    else:
        adminregistration()

def adminregistration():
    fad = len('Admin Registration')*'—'
    print('\nAdmin Registration\n%s\n'%fad)
    global username
    username = input('enter username: ')
    password = input('enter password: ')
    dict1 = {}
    f = open('admin.txt','wb')
    dict1[username]=password
    pickle.dump(dict1,f)
    f.close()
    adminlogin()

def menu():
    global username
    while True:
        choice = input('\nWelcome to the school library\n1.Book List\n2.Issue a book\n3.Return a book\n4.Go back to the login screen\n5.Exit\nChoose a number(1,2,3,4,5): ')
        if choice == '1':
            showbooks()
        elif choice == '2':
            lendingdetails(username) 
        elif choice == '3':
            return_book(username)
        elif choice == '4':
            print("\n")
            startscreen()
        elif choice == '5':
            print('Thank you for using the school library!')
            exit()
        else:
            print('please input either 1 or 2 or 3 or 4 or 5')

def showbooks():
    choice = '0'
    while True:
        if choice == '0': 
            choice = input('\nWould you like to see-\n1) Only the available books for lending\nor\n2) All the books that our library has to offer\nChoice(1 or 2): ')
        if choice == '1':
            mycursor.execute('select book_name from booksavailable')
            print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
            break
        elif choice == '2':
            mycursor.execute('select * from book')
            print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
            break
        else:
            choice = input('Please choose either 1 or 2.')

    input('\npress enter to back to the menu\n')
    menu()

def lendingdetails(name = 'abc'):
    if name == 'abc':
        name = input('Enter the name of the student: ')
    mycursor.execute("select * from lending where name ='%s';"%name)

    if len(mycursor.fetchall())!= 0:
        print('\nYou have already issued a book.')
        print('Please return it before trying to issue another.')
        input('Returning to the menu...(press enter to continue)')
        menu()
    print('Books Available\n---------------')
    mycursor.execute('Select book_name from booksavailable;')
    print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
    mycursor.execute("Select * from lending where name ='%s';"%name)
    book_name = input('Enter name of the book: ')
    mycursor.execute("Select * from booksavailable where book_name ='%s';"%book_name)
    if(len(mycursor.fetchall()) != 0):
        date = dt.datetime.now().strftime('%d'+'/'+'%m'+'/'+'%Y')
        values = date,name,book_name
        sql = "Insert into lending (date,name,book_name) Values (%s,%s,%s)"
        mycursor.execute(sql, values)
        print(name,'has taken',book_name,'on',date)
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%book_name)
        mydb.commit()
        input('\npress enter to back to the menu\n')
    else:
        mycursor.execute("Select * from book where book_name ='%s'"%book_name)
        if(len(mycursor.fetchall()) != 0):
            print("I am sorry but the book requested is currently lent out to someone. Please try at a later date.")
            input("Press enter to continue")
        else:
            print(book_name,"doesn't exist in our library. Please ask the Librarian if you would like it to be included.") 
            input("Press enter to continue")
    mydb.commit()
    menu()

def return_book(name = 'abc'):
    print('\nBook return\n-----------\n')
    if name == 'abc':
        name = input('enter your name/name of the student: ')
    
    mycursor.execute("Select book_name from lending where name='%s';"%name)
    data = mycursor.fetchall()
    if(len(data)==0):
        print("You haven't taken any book yet. Please issue a book before choosing three")
        input('Returning to menu....')
        menu()
    else:
        book_name = data[0][0]
        days = dayslent(name)
        if days < 7:
            choice = input('Would you like to return %s\nChoice(y(es) or n(o)): '%book_name)
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name[1:-1]:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s sucessfully'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
                mydb.commit()
                menu()
        else:
            print('You have incurred a fine of %s'%str((days-7)*2)+f" AED (2*({days}-7)) for not returning the book on time.\nYou are not allowed to take another book until you pay it. Please contact the librarian for furthur instruction.\n")
            input('Returning to the menu...(press enter to continue)')
            menu()


    


def adminmenu(foo=None):
    def menu():
            print('\n1. See pending books')
            print('2. Lend a book')
            print('3. Add a new book to the database')
            print('4. Edit info of Existing Books')
            print('5. Return a book')
            print('6. Go back to the Startscreen')
            print('7. Show books')
            print('8. Damaged Books')
            print('9. Delete Books')
            print('10. Exit\n')
            choice = input("enter your choice: ")
            if choice == '1':
                see_lent()
            elif choice == '2':
                adminlendingdetails()
            elif choice == '3':
                enterbookinfo()
            elif choice == '4':
                updatebookinfo()
            elif choice == '5':
                adminreturn_book()
            elif choice == '6':
                startscreen()
            elif choice == '7':
                adminshowbooks()
            elif choice == '8':
                damagedbooks()
            elif choice == '9':
                deletebooks()
            elif choice == '10':
                print('Thank you for using the school library!')
                exit()
            
            else:
                print("\nPlease choose a number from the following list- [1,2,3,4,5,6,7,8]: ")
                adminmenu('fdasfds')
    if foo == None:
        global username
        print('\nAdmin Menu\n——————————\n')
        print("Welcome",username)
        print('Choose a number')
        menu()
    else:
        print('\nAdmin Menu\n——————————\n')
        print('Choose a number')
        menu()

def see_lent():
    mycursor.execute("select * from lending;")
    data = mycursor.fetchall()
    if len(data) != 0:
        print(tabulate(data,headers=["Date","Name","Book Name"],tablefmt="grid"))
        input('Press enter to continue')
    else:
        print("There are no books pending!\n")
        input('Press enter to continue')
    adminmenu('x')

def enterbookinfo():
    print('\nBook Info\n')
    while True:
        book_name = input('enter name of the book: ')
        mycursor.execute('Select * from book;')
        if book_name in dict(mycursor.fetchall()):
            print('This book already exists in the database.')
            def choice():
                choice = input("\nWould you like to try a different book?\nChoice(y,n)= ")
                if choice[0].lower() == 'y':
                    enterbookinfo()
                elif choice[0].lower() == 'n':
                    adminmenu()
                else:
                    print('please either y(es) or n(o): ')
                    choice()
        sql = "Insert into book(book_name) Values ('%s');"%book_name
        mycursor.execute(sql)
        mydb.commit()

        sql = "Insert into booksavailable(book_name) Values ('%s');"%book_name
        values = book_name
        mycursor.execute(sql, values)
        mydb.commit()

        print('The entry for',book_name,'has been successfully created.\n')
        choice = input('Would you like to\n1. Add another book\n2. Go back to the menu\nChoose an option(1 or 2): ')
        if choice == '1':
            continue 
        elif choice == '2':
            adminmenu()

def updatebookinfo():
    mycursor.execute('select * from book')
    print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
    id = input('enter book ID: ')
    mycursor.execute('select book_name from book where book_id =%s' %id) 
    if len(mycursor.fetchall()) == 0:
        print('The book id entered does not exist')
        choice = input("Would you like to retype the id?\nChoice (Y(es) or N(o)): ")
        if choice.lower()[0] == 'n':
            adminmenu()
            
    mycursor.execute('select book_name from book where book_id =%s' %id) 
    book_name = mycursor.fetchall()[0][0]
    newname = input('enter new name: ')
    val = (newname,id)
    query = "Update book set book_name='%s' where book_id =%s" %val+';'
    mycursor.execute(query)
    query = "Update booksavailable set book_name='%s' where book_id =%s" %val+';'
    mycursor.execute(query)
    l1 = [["Old Name","New Name"],[book_name,newname]]
    print(tabulate(l1,headers="firstrow",tablefmt="grid"))
    choice = input('Would you like to go forward with the name change shown above?\nChoice(yes or no): ')
    while True:
        if choice[0].lower() == 'y':
            mydb.commit()
            print('%s has been successfully changed to %s'%(book_name,newname))
            input("Going back to the menu...(press enter to continue)")
            adminmenu()
        elif choice[0].lower() == 'n':
            option = input('Do you want to try again?')
            while True:
                if option[0].lower == 'y':
                    updatebookinfo()
                elif option[0].lower == 'n':
                    input("Going back to the menu...(press enter to continue)")
                    adminmenu()
                else:
                    option = input('please type either yes or no: ')

        else:
            choice = input('please type either yes or no')

def adminlendingdetails():
    name = input('Enter the name of the student: ')
    mycursor.execute("select * from lending where name ='%s';"%name)
    if len(mycursor.fetchall())!= 0:
        print('\n%s has already issued a book.'%name)
        print('Please get him or her to return it.')
        input('Returning to the menu...(press enter to continue)')
        adminmenu()
    print('Books Available\n---------------')
    mycursor.execute('Select book_name from booksavailable;')
    print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
    mycursor.execute("Select * from lending where name ='%s';"%name)
    book_name = input('Enter name of the book: ')
    mycursor.execute("Select * from booksavailable where book_name ='%s';"%book_name)
    if(len(mycursor.fetchall()) != 0):
        date = dt.datetime.now().strftime('%d'+'/'+'%m'+'/'+'%Y')
        values = date,name,book_name
        sql = "Insert into lending (date,name,book_name) Values (%s,%s,%s)"
        mycursor.execute(sql, values)
        print(name,'has taken',book_name,'on',date)
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%book_name)
        mydb.commit()
        input('\npress enter to back to the menu\n')
    else:
        mycursor.execute("Select * from book where book_name ='%s'"%book_name)
        if(len(mycursor.fetchall()) != 0):
            print("I am sorry but the book requested is currently lent out to someone. Please try at a later date.")
            input("Press enter to continue")
        else:
            print(book_name,"doesn't exist in our library.")
            input("Press enter to continue")
    mydb.commit()
    adminmenu()

def adminshowbooks(choice = '0'):
    while True:
        if choice == '0': 
            choice = input('\nWould you like to see-\n1) Only the available books for lending\nor\n2) All the books that our library has to offer\nChoice(1 or 2): ')
        if choice == '1':
            mycursor.execute('select book_name from booksavailable')
            print(tabulate(mycursor.fetchall(),headers=["Name"],tablefmt="grid"))
            break
        elif choice == '2':
            mycursor.execute('select * from book')
            print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
            break
        else:
            print('Please choose either 1 or 2.')

    input('\npress enter to back to the menu\n')
    adminmenu()


def adminreturn_book(name = 'abc'):
    print('Book return\n-----------\n')
    if name == 'abc':
        name = input('enter the name of the student: ')
    mycursor.execute("Select book_name from lending where name='%s';"%name)
    data = mycursor.fetchall()
    if(len(data)==0):
        print("%s hasn't taken any book yet."%name)
        input('Returning to menu....')
        adminmenu()
    else:
        book_name = data[0][0]
        days = dayslent(name)
        if days < 7:
            choice = input('Is %s returning %s?\nChoice [Y(es)/n(o)]: '%(name,book_name))
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s\nAnd the database has been updated to reflect that'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
        else:
            choice = input('Has %s paid the fine of '%name+str((days-7)*2)+' AED?\nChoice [Y(es)/n(o)]:')
            if choice[0].lower() == 'y':
                sql = "DELETE FROM lending WHERE name = '%s'" %name
                mycursor.execute(sql)
                sql = "Insert into booksavailable(book_id,book_name) Values (%s,%s)"
                mycursor.execute("select * from book;")
                books = dict(mycursor.fetchall())
                id_num = 0
                for i in books:
                    if books[i] == book_name:
                        id_num = i
                val = (id_num,book_name)
                mycursor.execute(sql,val)
                mydb.commit()
                print('%s has returned book %s'%(name,book_name))
                input('Returning to the menu...(press enter to continue)')
    mydb.commit()
    adminmenu()


#new stuff

def dayslent(name):
    mycursor.execute('select date from lending where name = "%s"'%name)
    lentdate = mycursor.fetchall()[0][0]
    date = dt.datetime.strptime(lentdate,'%d'+'/'+'%m'+'/'+'%Y') 
    difference = dt.datetime.now()-date #calculates the difference
    return int(difference.days)

def damagedbooks():
    print('\nDamaged Books\n----------------\n')
    print('1. Show damaged books')
    print('2. Add damaged books')
    print('3. Remove damaged books')
    print('4. Return to menu\n')
    choice = input('Enter choice: ')
    if choice == '1':
        displaycsvtable()
    if choice == '2':
        addbook()
    if choice == '3':
        deletebooksfromcsv()
    if choice == '4':
        adminmenu()

def displaycsvtable(x=None):
    print('\nDamaged Books\n-------------')
    filename = 'damaged_books.csv'
    data = []
    with open(filename,'r',newline='') as damaged_books:
        csvreader = csv.reader(damaged_books)
        for i in csvreader:
            data.append(i)
    print(tabulate(data,headers="firstrow",tablefmt='grid'))
    if x == None:
        input('\npress enter to back to the menu\n')
        damagedbooks()
    else:
        pass


def addbook():
    filename = 'damaged_books.csv'
    with open(filename,'a',newline='') as damaged_books:
        csvwriter = csv.writer(damaged_books)
        data = pd.read_csv(filename).to_numpy()
        bookname = input("Enter bookname: ")
        mycursor.execute("Delete from booksavailable where book_name ='%s'"%bookname)
        mydb.commit()
        bookid =  data[-1][0]+1
        csvwriter.writerow([bookid,bookname])
    input('\npress enter to back to the menu\n')
    damagedbooks()




def deletebooksfromcsv():
    filename = 'damaged_books.csv'
    displaycsvtable(1)
    data = []
    name = input("Enter the book name: ")

    with open(filename,'r',newline='') as damaged_books:
        csvreader = csv.reader(damaged_books)
        for i in csvreader:
            data.append(i)
    for i in range(len(data)):
        if data[i][1] == name:
            del data[i]
            break

    with open(filename,'w',newline='') as damaged_books:
        csvwriter = csv.writer(damaged_books)
        header = ["Serial No.","Book Name"]
        csvwriter.writerow(header)
        for i in range(1,len(data)):
            bookname = data[i][1]
            bookid =  i
            csvwriter.writerow([bookid,bookname])
    mycursor.execute("Insert into booksavailable(book_name) Values('%s');"%name)
    mydb.commit()

            
    displaycsvtable()
    input('\npress enter to back to the menu\n')
    damagedbooks()


def deletebooks():
    mycursor.execute('select * from book')
    print(tabulate(mycursor.fetchall(),headers=["Book ID","Name"],tablefmt="grid"))
    name = input("Enter book-name: ")
    mycursor.execute(f"Delete from booksavailable where book_name = '{name}'")
    mycursor.execute(f"Delete from book where book_name = '{name}'")
    mydb.commit()
    if mycursor.rowcount != 0:
        print(f"{name} has been deleted successfully.")
        input("\npress enter to continue")
        
        adminmenu()
    else:
        print(f"{name} was not found in the database.")
        input("\npress enter to continue")
        adminmenu()

startscreen()
exit()


