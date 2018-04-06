import re
import random
import cx_Oracle
import time


class DBOperations:

    def __init__(self):
        self.conn = cx_Oracle.connect('tanishk/12345@127.0.0.1/xe')
        self.cur = self.conn.cursor()

    def getCol(self, tableName, columnName, ID):
        query = "SELECT " + columnName + " FROM " + tableName + " WHERE ID='" + str(ID) + "'"
        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def getRow(self, tableName, ID):
        query = "SELECT * FROM " + tableName + " WHERE ID='" + str(ID) + "'"
        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def setCol(self, tableName, colName1, colVal1, ID):
        query = "UPDATE " + tableName + " SET " + colName1 + "='" + str(colVal1) + "' WHERE ID='" + str(ID) + "'"
        self.cur.execute(query)
        self.conn.commit()

    def setRow(self,tableName, values):
        strVal = ",".join(values)
        query = "INSERT INTO "+tableName+" VALUES ("+strVal+")"
        self.cur.execute(query)
        self.conn.commit()

    def removeRow(self,tableName, ID):
        query = "DELETE FROM "+tableName+" WHERE ID='"+str(ID)+"'"
        self.cur.execute(query)
        self.conn.commit()

class SignIn:
    def findID(self, tableName, id1):
        db = DBOperations()
        k = db.getCol(tableName,'ID',id1)
        if k == [] or not id1 == k[0][0]:
            db.conn.close()
            return 0
        else:
            db.conn.close()
            return 1

    def checkPassword(self, tableName, id1, password):
        db = DBOperations()
        k = db.getCol(tableName,'PASSWORD',id1)
        if not password == k[0][0]:
            db.conn.close()
            return 0
        else:
            db.conn.close()
            return 1

    def lockAccount(self, tableName, id1):
        db = DBOperations()
        db.setCol(tableName,'IS_LOCKED','Yes',id1)
        db.conn.close()

    def isLocked(self, tableName, id1):
        db = DBOperations()
        k = (db.getCol(tableName, 'IS_LOCKED', id1))[0][0]
        if k == 'Yes':
            db.conn.close()
            return True
        else:
            db.conn.close()
            return False


class SignUp:
    def __init__(self):
        self.newCust = dict()

    def addCust(self):
        db = DBOperations()
        try:
            db.cur.execute('INSERT INTO CUST_ACCOUNTS VALUES(:p1,:p2,:p3,:p4,:p5)', (
            self.newCust['cust_id'], self.newCust['password'], self.newCust['acType'], self.newCust['minBalance'],
            self.newCust['isLocked']))
            db.cur.execute('INSERT INTO CUST_INFO VALUES(:p1,:p2,:p3,:p4,:p5,:p6,:p7,:p8)', (
            self.newCust['cust_id'], self.newCust['fname'], self.newCust['lname'], self.newCust['adrLine1'],
            self.newCust['adrLine2'], self.newCust['city'], self.newCust['state'], self.newCust['pincode'],))
            db.conn.commit()
            db.conn.close()
            print('Registration Successful!')
        except:
            print('Error in inserting to database...')
            db.conn.close()

    def verifyPassword(self, password):
        if len(password) < 8:
            return -1
        # password must be combo of both numerals and letters
        if re.search('[a-zA-Z]+', password) and re.search('[0-9]+', password):
            return 1
        else:
            return 0

    def checkPincode(self, pincode):
        if len(pincode) == 6:
            if re.search('\D', pincode):
                return 0
            else:
                return 1
        else:
            return 0

    def getRandomNum(self, digits):
        lower = 10 ** (digits - 1)
        upper = 10 ** digits - 1
        return random.randint(lower, upper)

    def genIdAcNo(self):
        # GENERATE CUSTOMER ID(& ACCOUNT NUMBER)
        # NOTE: ACCOUNT NUMBER IS SAME AS CUSTOMER ID
        # CHECK IF GENERATED IS UNIQUE IN TABLE
        temp = self.getRandomNum(10)
        db = DBOperations()
        cur = db.conn.cursor()
        cur.execute('SELECT ID FROM CUST_ACCOUNTS')
        all_ids = cur.fetchall()
        cur.execute('SELECT ID FROM CLOSED_ACCOUNTS')
        all_ids.append(cur.fetchall())
        while temp in all_ids:
            temp = self.getRandomNum(10)
        db.conn.close()
        return temp
        # Note: one customer can have only one account.

    def getAccountType(self):
        print('\tAccount Type')
        print('1. Savings Account')
        print('2. Current Account')
        while True:
            try:
                choice = int(input('\nChoice: '))
                if choice not in range(1, 3):
                    print('Invalid choice, Re-Enter choice...')
                else:
                    return choice
            except:
                print('Invalid Input')

    def blankFields(self):
        for entries in self.newCust.values():
            if type(entries) == type('') and len(entries) == 0:
                print('You left a field blank. Closing Session...')
                return 1
        return 0

    def newCustDetails(self):
        print('\n\tSign Up')
        print('Enter details:')
        self.newCust['fname'] = input('Firstname: ')
        self.newCust['lname'] = input('Lastname: ')
        print('Address:\n')
        self.newCust['adrLine1'] = input('Line 1: ')
        self.newCust['adrLine2'] = input('Line 2: ')
        self.newCust['city'] = input('City: ')
        self.newCust['state'] = input('State: ')
        temp = input('Pincode: ')
        while self.checkPincode(temp) == 0:
            print('Invalid Pincode. Re-Enter Pincode...')
            temp = input('Pincode')
        self.newCust['pincode'] = int(temp)
        self.newCust['minBalance'] = 0
        actype = int(self.getAccountType())
        if actype == 1:
            self.newCust['acType'] = 'Savings'
        elif actype == 2:
            self.newCust['acType'] = 'Current'
            self.newCust['minBalance'] = 5000
        flag = 1
        if self.newCust['acType'] == 'Current':
            received = input('Minimum balance (5000) received? Y/N: ')
            if received is not 'Y':
                print('Minimum balance not received. Closing session... ')
                flag = 0
            else:
                pass
        if flag is not 0:
            ####DISPLAY AUTO GENERATED CUST-ID AND ACCOUNT NO.
            self.newCust['cust_id'] = self.genIdAcNo()
            print('Customer ID (auto-generated): ', self.newCust['cust_id'])
            print('Account Number (auto-generated): ', self.newCust['cust_id'])
            temp = input('New Password: ')
            while (self.verifyPassword(temp) is not 1):
                print('Invalid Password, Re-Enter Password...')
                temp = input('New Password: ')
            self.newCust['password'] = temp
            self.newCust['isLocked'] = 'No'
            if self.blankFields() == 0:
                self.addCust()


class AdminSignIn(SignIn):
    def __init__(self):
        self.admin_id = 0
        self.loginAttempts = 3

    def promptUser(self):
        print('\n\tAdministrator Sign In')
        proceed = 'OK'
        try:
            admin_id = input('Admin-ID: ')
        except:
            print('Invalid Admin-ID. Closing Session...')
            return
        if len(str(admin_id)) is not 12:
            print('Invalid Admin-ID. Closing Session...')
            proceed = 'NO'
        else:
            flag = super().findID('ADMIN_INFO', admin_id)
            if flag == 0:
                print('Admin-ID is incorrect. Closing Session...')
                proceed = 'NO'
            else:
                if super().isLocked('ADMIN_INFO', admin_id):
                    print('Your Account has been locked due to 3 consecutive failed attempts...')
                    proceed = 'NO'

        if proceed == 'OK':
            while True:
                if self.loginAttempts == 0:
                    print('Account being locked due to 3 consecutive failed attempts...')
                    super().lockAccount('ADMIN_INFO', admin_id)
                    break


                password = input('Password: ')
                flag = super().checkPassword('ADMIN_INFO', admin_id, password)
                if flag == 1:
                    print('Sign-In Successful.\nWelcome...')
                    self.admin_id = admin_id
                    # SIGNED IN FUNCTION CALL
                    self.signedIn()
                    break
                else:
                    self.loginAttempts = self.loginAttempts - 1
                    print('Wrong Password')
                    print('You have ', self.loginAttempts, ' more attempts left.')
                    if self.loginAttempts > 0:
                        key = input("Press any key to retry, 'q' to quit:  ")
                        if key == 'q' or key == 'Q':
                            break

    def signedIn(self):
        admin = AdminLoggedIn(self.admin_id)
        while True:
            choice = admin.showMenu()
            if choice == 1:
                db = DBOperations()
                db.cur.execute('SELECT * FROM CLOSED_ACCOUNTS')
                print("Account No.\t\tDate Closed")
                [print("-", end="") for i in range(28)]
                print("")
                for l in db.cur.fetchall():
                    print(l[0], "\t\t", ((str(l[1])).split())[0])
                db.conn.close()

            elif choice == 2:
                print('Logging out...')
                break


class CustomerSignIn(SignIn):
    def __init__(self):
        self.cust_id = 0
        self.loginAttempts = 3

    def promptUser(self):
        print('\n\tCustomer Sign In')
        proceed = 'OK'
        try:
            cust_id = int(input('Customer-ID: '))
        except:
            print('Invalid Customer-ID. Closing Session...')
            return

        if len(str(cust_id)) < 10:
            print('Invalid Customer-ID. Closing Session...')
            proceed = 'NO'
        else:
            flag = super().findID('CUST_ACCOUNTS', cust_id)
            if flag == 0:
                print('Customer-ID not found. Closing Session...')
                proceed = 'NO'
            else:
                if super().isLocked('CUST_ACCOUNTS', cust_id):
                    print('Your Account has been locked due to 3 consecutive failed attempts...')
                    proceed = 'NO'

        if proceed == 'OK':
            while True:
                if self.loginAttempts == 0:
                    print('Account being locked due to 3 consecutive failed attempts...')
                    super().lockAccount('CUST_ACCOUNTS', cust_id)
                    break

                password = input('Password: ')
                flag = super().checkPassword('CUST_ACCOUNTS', cust_id, password)
                if flag == 1:
                    print('Sign-In Successful.\nWelcome...')
                    self.cust_id = cust_id
                    # SIGNED IN FUNCTION CALL
                    self.signedIn()
                    break
                else:
                    self.loginAttempts = self.loginAttempts - 1
                    print('Wrong Password')
                    print('You have ', self.loginAttempts, ' more attempts left.')
                    if self.loginAttempts > 0:
                        key = input("Press any key to retry, 'q' to quit:  ")
                        if key == 'q' or key == 'Q':
                            break

    def signedIn(self):
        customer = CustomerLoggedIn(self.cust_id)
        while True:
            choice = customer.showMenu()
            if choice == 1:
                print('\n\tAddress Change')
                ad = DBOperations()
                adrL1 = ad.getCol('CUST_INFO', 'ADRLINE1', self.cust_id)[0][0]
                adrL2 = ad.getCol('CUST_INFO', 'ADRLINE2', self.cust_id)[0][0]
                print('Current Address:')
                print('Line 1: ' + adrL1)
                print('Line 2: ' + adrL2)
                print('New Address:')
                adrL1 = input('Line 1: ')
                adrL2 = input('Line 2: ')
                if adrL1 == '' or adrL2 == '':
                    print('You left a field blank...')
                    continue
                proceed = self.confirm()
                if proceed == 'Y' or proceed == 'y':
                    customer.adrChange(adrL1, adrL2)
            elif choice == 2:
                try:
                    if int(self.getCustId()) == self.cust_id:
                        amt = int(input('Enter amount: '))
                    else:
                        print('Invalid Account Number. Closing Session...')
                        continue
                except:
                    print('E: Invalid Input')
                proceed = self.confirm()
                if proceed == 'Y' or proceed == 'y':
                    customer.moneyDeposit(amt)
            elif choice == 3:
                try:
                    if int(self.getCustId()) == self.cust_id:
                        amt = int(input('Enter amount: '))
                    else:
                        print('Invalid Account Number. Closing Session...')
                        continue
                except:
                    print('E: Invalid Input')
                proceed = self.confirm()
                if proceed == 'Y' or proceed == 'y':
                    customer.moneyWithdraw(amt)
            elif choice == 4:
                if int(self.getCustId()) == self.cust_id:
                    d1 = self.getDate('From')
                    dateFrom = d1.split('-')
                    if len(dateFrom) is not 3:
                        print('Invalid Date. Closing Session...')
                        continue
                    d2 = self.getDate('To')
                    dateTo = d2.split('-')
                    if len(dateTo) is not 3:
                        print('Invalid Date. Closing Session...')
                        continue
                    D1 = int(dateFrom[0])
                    D2 = int(dateTo[0])
                    M1 = int(dateFrom[1])
                    M2 = int(dateTo[1])
                    Y1 = int(dateFrom[2])
                    Y2 = int(dateTo[2])
                    flag = 0
                    if D1 in range(1,32) and D2 in range(1,32) and M1 in range(1,13) and M2 in range(1,13) and Y1 in range(1900,2050) and Y2 in range(1900,2050):
                       pass
                    else:
                        print('Invalid Dates entered. Closing Session...')
                        continue
                    if Y1 == Y2:
                        if M1 == M2:
                            if D1 == D2:
                                print('Dates accepted.')
                            elif D1 > D2:
                                flag = 1
                        elif M1 > M2:
                            flag = 1
                    elif Y1 > Y2:
                        flag = 1
                    if flag == 1:
                        print('Invalid Dates entered. Closing Session...')
                        continue
                    customer.printStatement(d1, d2)
                else:
                    print('Invalid Account Number. Closing Session...')
                    continue 
            elif choice == 5:
                try:
                    acTo = int(input('Account To: '))
                except:
                    print('Invalid account number. Closing Session...')
                    continue
                if len(str(acTo)) < 10:
                    print('Invalid account number. Closing Session...')
                    continue
                try:
                    amount = int(input('Amount: '))
                except:
                    print('Invalid amount. Closing Session...')
                    continue
                customer.transferMoney(acTo,amount)
            elif choice == 6:
                try:
                    if int(self.getCustId()) == self.cust_id:
                        pass
                    else:
                        print('Invalid Account Number. Closing Session...')
                        continue
                except:
                    print('E: Invalid Input')
                proceed = self.confirm()
                if proceed == 'Y' or proceed == 'y':
                    customer.accountClosure()
                    break
            elif choice == 7:
                print('Logging out...')
                break

    def getDate(self,str):
        print('Date Format: DD-MM-YYYY')
        d1 = input('Date '+str+': ')
        return d1

    def getCustId(self):
        return input('Enter Account Number: ')

    def confirm(self):
        return input('Are you sure? Y/N: ')


class CustomerLoggedIn:

    def __init__(self, cust_id):
        self.cust_id = cust_id

    def showMenu(self):
        print('\n\tCUSTOMER MENU')
        print('1. Address Change')
        print('2. Money Deposit')
        print('3. Money Withdrawal')
        print('4. Print Statement')
        print('5. Transfer Money')
        print('6. Account Closure')
        print('7. Logout')
        while True:
            try:
                choice = int(input('\nChoice: '))
                if choice not in range(1, 8):
                    print('Invalid choice, Re-Enter choice...')
                else:
                    return choice
            except:
                print('Invalid choice. Retry...')


    def adrChange(self, adrL1, adrL2):
        db = DBOperations()
        try:
            db.setCol('CUST_INFO','ADRLINE1',adrL1,self.cust_id)
            db.setCol('CUST_INFO','ADRLINE2',adrL2,self.cust_id)
            db.conn.close()
            print('Address successfully changed...')
        except:
            db.conn.close()
            print('E: Error in changing Address')

    def moneyDeposit(self, amount):
        db = DBOperations()
        currbal = int(self.getCurrentBalance())
        print('Current Balance: ', currbal)
        newbal =  currbal + amount
        print('New Balance: ',newbal)
        db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal,self.cust_id)
        self.updateTransaction(amount,newbal,"'Credit'",self.cust_id)
        db.conn.close()
        print('Money successfully deposited...')

    def moneyWithdraw(self,amount):
        db = DBOperations()
        currbal = int(self.getCurrentBalance())
        print('Current Balance: ', currbal)
        newbal = currbal - amount
        actype = self.getAcType()
        if newbal<0:
            print('Given amount exceeds your current Balance')
        elif actype == 'Current':
            if newbal<5000:
                print('Transaction not allowed...')
                print('Your Account type: Current Account')
                print('Minimum Balance required: 5000')
                print('Current Balance: ', currbal)
                print('Transaction terminated...')
                db.conn.close()
                return
            else:
                db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal,self.cust_id)
                self.updateTransaction(amount, newbal, "'Debit'",self.cust_id)
                db.conn.close()
        else:
            db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal,self.cust_id)
            self.updateTransaction(amount, newbal, "'Debit'",self.cust_id)
            db.conn.close()
        print('Money successfully Withdrawn...')
        print('Previous Balance: ',currbal)
        print('New Balance: ',newbal)

    def printStatement(self,d1,d2):
        query = "SELECT * FROM TRANSACTIONS WHERE ID='"+str(self.cust_id)+"' AND TR_DATE BETWEEN TO_DATE('"+d1+"','DD-MM-YYYY') AND TO_DATE('"+d2+"','DD-MM-YYYY')"
        db = DBOperations()
        db.cur.execute(query)
        results = db.cur.fetchall()
        db.conn.close()
        if len(results) ==0:
            print('No previous transactions history...')
            return
        print('Date\t\tTransaction Type\tAmount\tBalance')
        [print("-", end="") for i in range(48)]
        print("")
        for row in results:
            #splitting datetime object into date and time
            s1 = ((str(row[1])).split())[0]
            s1 = s1+"\t\t"+row[4]+"\t\t\t"+str(row[2])+"\t\t"+str(row[3])
            print(s1)

    def transferMoney(self,acTo,amount):

        currbal = int(self.getCurrentBalance())
        newbal = currbal - amount
        actype = self.getAcType()
        if newbal < 0:
            print('Given amount exceeds your current Balance')
            return
        elif actype == 'Current':
            if newbal < 5000:
                print('Transaction not allowed...')
                print('Your Account type: Current Account')
                print('Minimum Balance required: 5000')
                print('Current Balance: ', currbal)
                print('Transaction terminated...')
                return
            else:
                db = DBOperations()
                # check if acTo exists in database
                k = db.getCol('CUST_ACCOUNTS', 'ID', acTo)
                if k == [] or not acTo == k[0][0]:
                    print('Target account number does not exist. Closing session...')
                    db.conn.close()
                    return
                else:
                    try:
                        # deduct amount:
                        db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal, self.cust_id)
                        # increase target's amount
                        # find newbalance for acto and set it
                        currbal1 = db.getCol('CUST_ACCOUNTS', 'BALANCE', acTo)
                        currbal1 = currbal1[0][0]
                        newbal1 = currbal1 + amount
                        db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal1, acTo)
                        db.conn.close()
                    except cx_Oracle.DatabaseError as ex:
                        error = ex.args
                        print('Error.code =', error.code)
                        print('Error.message =', error.message)
                        print('Error.offset =', error.offset)
                        db.conn.rollback()
                        db.conn.close()
                        return
        else:
            try:
                db = DBOperations()
                db.setCol('CUST_ACCOUNTS', 'BALANCE', newbal, self.cust_id)
                db.conn.close()
            except cx_Oracle.DatabaseError as ex:
                error = ex.args
                print('Error.code =', error.code)
                print('Error.message =', error.message)
                print('Error.offset =', error.offset)
                db.conn.rollback()
                db.conn.close()
                return
        print('Money successfully transferred...')
        print('Your Account:')
        print('Previous Balance: ', currbal)
        print('New Balance: ', newbal)
        self.updateTransaction(amount,newbal,"'Debit'",self.cust_id)
        self.updateTransaction(amount, newbal1, "'Credit'", acTo)

    def accountClosure(self):
        db = DBOperations()
        address = db.getCol('CUST_INFO','ADRLINE1',self.cust_id)[0][0]
        address = address + "\n" + db.getCol('CUST_INFO','ADRLINE2',self.cust_id)[0][0]
        print('The amount ', self.getCurrentBalance(), ' will be sent to your address:')
        print(address)
        db.removeRow('CUST_ACCOUNTS', self.cust_id)
        db.removeRow('CUST_INFO', self.cust_id)
        today = self.getTodayDate()
        today = "TO_DATE('" + today + "','DD-MM-YYYY')"
        values = [str(self.cust_id),today]
        db.setRow('CLOSED_ACCOUNTS',values)
        db.conn.close()
        print('Your account '+str(self.cust_id)+' has been closed successfully.')
        print('We hope you had a pleasant experience with us.')
        print('See you again, soon.')
        return

    def updateTransaction(self, amount, balance, trType, ID):
        db = DBOperations()
        today = self.getTodayDate()
        today = "TO_DATE('" + today + "','DD-MM-YYYY')"
        db.setRow('TRANSACTIONS', [str(ID), today, str(amount), str(balance), trType])
        db.conn.close()

    def getAcType(self):
        db = DBOperations()
        result = db.getCol('CUST_ACCOUNTS', 'ACTYPE', self.cust_id)
        db.conn.close()
        return result[0][0]

    def getCurrentBalance(self):
        db = DBOperations()
        result = db.getCol('CUST_ACCOUNTS', 'BALANCE', self.cust_id)
        db.conn.close()
        return result[0][0]

    def getTodayDate(self):
        return time.strftime("%d-%m-%Y")


class AdminLoggedIn:
    def __init__(self,admin_id):
        self.admin_id = admin_id
    def showMenu(self):
        print('\n\tADMINISTATOR MENU')
        print('1. Print closed accounts history')
        print('2. Admin Logout')
        while True:
            try:
                choice = int(input('\nChoice: '))
                if choice not in range(1, 3):
                    print('Invalid choice, Re-Enter choice...')
                else:
                    return choice
            except:
                print('Invalid choice. Retry...')


class MyProgram:
    def getChoice(self):
        print('\n\tMAIN MENU')
        print('1. Sign Up (New Customer)')
        print('2. Sign In (Existing Customer)')
        print('3. Admin Sign In')
        print('4. Quit')
        while True:
            try:
                choice = int(input('Choice: '))
                if choice not in range(1, 5):
                    print('Invalid choice, Re-Enter choice...')
                else:
                    return choice
            except:
                print('E: Invalid Choice. Retry...')

    def runIt(self):
        while True:
            choice = self.getChoice()
            if choice == 1:
                customer = SignUp()
                customer.newCustDetails()
            elif choice == 2:
                customer = CustomerSignIn()
                customer.promptUser()
            elif choice == 3:
                admin = AdminSignIn()
                admin.promptUser()
            elif choice == 4:
                quit()


ob = MyProgram()
ob.runIt()
