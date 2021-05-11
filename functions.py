import sqlconnect as connect
import random
import json
import datetime

#returns the day of the journey date
def weekDayFinder(journey_date):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    l = list(map(int, journey_date.split('/')))
    day = datetime.date(l[2], l[1], l[0]).weekday()
    weekDayFinder.journey_day = week_days[day]

def mainMenu():
    print("-"*45)
    print("WELCOME TO SIMPLE RAILWAY RESERVATION SYSTEM")
    print("-"*45)
    print("1. USER MODE")
    print("2. ADMIN MODE")
    choice = input("\nEnter your choice: ")
    if choice == "1":
        userMode()
    elif choice == "2":
        adminMode()
    else:
        input("You have entered a wrong value. Press ENTER key to go back: ")
        mainMenu()


def userMode():
    print("\n1. Book a Ticket")
    print("2. PNR Enquiry")
    print("3. Cancel Ticket")
    print("4. Booking History")
    print("5. GO BACK")
    choice = input("\nEnter your choice: ")
    if choice == "1":
        board = str(input("\nType your boarding station code (e.g. ADI): ")).upper()
        destination = str(input("Type your destination station code (e.g. CYI): ")).upper()
        journey_date = (input("Enter date of journey in DD/MM/YYYY format: "))
        weekDayFinder(journey_date)
        journey_day = weekDayFinder.journey_day
        trainFinder(board, destination,journey_day)
        bookTicket(board, destination, journey_date)
    elif choice == "2":
        pnrChecker()
    elif choice == "3":
        cancelTicket()
    elif choice == "4":
        bookingHistory()
    elif choice == "5":
        mainMenu()
    else:
        input("You have entered a wrong value. Press ENTER key to go back: ")
        userMode()

def trainFinder(board, destination, journey_day):
    indexBoard = int()
    trains_available = []
    indexDestination = int()

    # MYSQL Queries
    connect.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema ='rrs'")
    table_names = [i[0] for i in connect.cursor.fetchall()]

    #table_names contain all the table in the rrs database. rrs = railway reservation system

    for j in range(len(table_names)):

        #excluding trains and user_bookings table
        if table_names[j] != "trains" and table_names[j] != "user_bookings":
            connect.cursor.execute("SELECT train_no FROM `trains`")
            train_no_list = [x[0] for x in connect.cursor.fetchall()]
            for y in range(len(train_no_list)):
                connect.cursor.execute("SELECT running_days FROM `trains` WHERE train_no = %s", (int(table_names[j])))
                running_days = connect.cursor.fetchone()[0]
                break
            if journey_day in running_days:
                #MySQL query to get the list of all the station codes for each train
                connect.cursor.execute("SELECT station_code FROM `%s`", (int(table_names[j])))
                routeList = [k[0] for k in connect.cursor.fetchall()]

                #check if any of the station code matches with boarding station
                for l in range(len(routeList)):
                    if routeList[l] == board:
                        #indexBoard stores the index of the station code when it's equal to boarding station
                        indexBoard = routeList.index(routeList[l])
                for m in range(len(routeList)):
                    if routeList[m] == destination:
                        #indexBoard stores the index of the station code when it's equal to destination station
                        indexDestination = routeList.index(routeList[m])
                        break
                if indexBoard < indexDestination:
                    trains_available.append(table_names[j])
    if trains_available != []:
        for trainNo in range(len(trains_available)):
            connect.cursor.execute("SELECT train_name FROM `trains` WHERE train_no = %s", (int(trains_available[trainNo])))
            row1 = connect.cursor.fetchone()[0]
            connect.cursor.execute("SELECT arrival FROM `%s` WHERE station_code = %s",
                                   (int(trains_available[trainNo]), board))
            row2 = connect.cursor.fetchone()[0]
            connect.cursor.execute("SELECT arrival FROM `%s` WHERE station_code = %s",
                                   (int(trains_available[trainNo]), destination))
            row3 = connect.cursor.fetchone()[0]
            print(str(trainNo + 1)+". Train No: "+str(trains_available[trainNo])+" | "+str(row1)+" | Boarding Arrival "
                                                                                                  "Time: "+str(
                row2)+" | Destination Arrival Time: "+str(row3))
    else:
        input("No Train Found! Press ENTER key to go back: ")
        userMode()


def bookTicket(board, destination, journey_date):

    username = "saurabh prakash"
    bookTicket_train_no = int(input("\nEnter the train number to book: "))
    bookTicket_class = str(input("Enter the coach category(SL,3A,2A): ")).upper()

    passenger = str(input("Enter passenger name: ")).upper()
    passenger_age = str(input("Enter passenger age: "))
    passenger_gender = str(input("Enter passenger gender: ")).upper()

    connect.cursor.execute("SELECT coaches FROM `trains` WHERE train_no = %s", (bookTicket_train_no))
    # json.loads converts string dictionary to dictionary
    coach_count = json.loads(connect.cursor.fetchone()[0])[bookTicket_class]
    connect.cursor.execute("SELECT count(*) FROM `user_bookings` WHERE class = %s", (bookTicket_class))
    count = connect.cursor.fetchone()[0]
    for i in range(coach_count):
        if count in range(72 * i, 72 * (i + 1)):
            if (bookTicket_class == "SL"):
                berth_class = "S" + str(i + 1)
            elif (bookTicket_class == "3A"):
                berth_class = "B" + str(i + 1)
            elif (bookTicket_class == "2A"):
                berth_class = "A" + str(i + 1)
            booking_status = "CNF/" + str(berth_class) + "/" + str(count + 1) + "/GN"
            break
        elif count >= 72 * coach_count:
            input("Sorry, No seats available! Press ENTER key to go back: ")
            userMode()

    # PNR Generate
    pnr = random.randint(10000000000, 99999999999)

    # Journey Start and End Date Time
    connect.cursor.execute("SELECT arrival FROM `%s` WHERE station_code = %s", (bookTicket_train_no, board))
    start_datetime = str(journey_date) + " " + str(connect.cursor.fetchone()[0])

    connect.cursor.execute("SELECT arrival FROM `%s` WHERE station_code = %s", (bookTicket_train_no, destination))
    end_datetime = str(journey_date) + " " + str(connect.cursor.fetchone()[0])
    connect.cursor.execute("SELECT train_name FROM `trains` WHERE train_no = %s",(bookTicket_train_no))
    train_name = connect.cursor.fetchone()[0]
    connect.cursor.execute('INSERT INTO `user_bookings` (username,start_datetime,end_datetime,train_no,pnr,'
                           'booking_status,current_status,class,name,age,gender,board,destination,status,train_name) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"booked",%s)',
                           (username, start_datetime, end_datetime, bookTicket_train_no, pnr, booking_status,
                            booking_status, bookTicket_class, passenger, passenger_age, passenger_gender, board, destination,train_name))
    connect.db.commit()
    print("-----------------------------------------------")
    print("          Ticket Successfully Booked!          ")
    print("-----------------------------------------------")
    print("               Reservation Slip                ")
    print("-----------------------------------------------")
    print("PNR: " + str(pnr))
    connect.cursor.execute("SELECT train_name FROM `trains` WHERE train_no = %s", (bookTicket_train_no))
    train_name = connect.cursor.fetchone()[0]
    print("TRAIN NO. " + str(bookTicket_train_no) + ": " + str(train_name))
    print("FROM " + str(board) + " TO " + str(destination))
    print("SCH DEP: " + str(start_datetime) + " ARR: " + str(end_datetime))
    print("BOOKING STATUS: " + str(booking_status))

    input("Successfully Booked! Press ENTER key to go back: ")
    userMode()



def pnrChecker():
    pnr = input("Enter PNR to check: ")
    sql = connect.cursor.execute("SELECT * FROM `user_bookings` WHERE pnr = %s", (pnr))
    if sql:
        l = connect.cursor.fetchall()[0]
        print("-"*45)  #prints line
        if l[10]=='cancelled':
            input("The ticket has been cancelled! Press ENTER to go back: ")
            userMode()
        else:
            print("Train No. "+l[4]+":"+l[5])
            print("FROM " + l[11] + " TO " + l[12])
            print("SCH DEP (" +l[11]+"): "+ l[2] + "\nSCH ARR (" +l[12]+"): " + l[3])
            print("\nPassenger Details:")
            print(l[13]+" "+l[14]+" "+l[15])
            print("BOOKING STATUS: " + l[7])
            print("CURRENT STATUS: " + l[8])
            choice = input("Press ENTER key to go back: ")
            userMode()
    else:
        input("Sorry, there is no record for this PNR. Press ENTER key to go back")
        userMode()

def cancelTicket():
    pnr = input("Enter PNR of the ticket: ")
    connect.cursor.execute("UPDATE `user_bookings` SET status='cancelled' WHERE pnr = %s",(pnr))
    connect.db.commit()
    input("Ticket successfully cancelled! Press ENTER key to go back: ")
    userMode()

def bookingHistory():
    connect.cursor.execute("SELECT * FROM `user_bookings` WHERE username = 'saurabh prakash'")
    #l = connect.cursor.fetchall()[0]
    for l in connect.cursor:
        print("-" * 45)
        print("Booking "+str(l[0]))
        print("-" * 45)
        print("Train No. " + l[4] + ":" + l[5])
        print("FROM " + l[11] + " TO " + l[12])
        print("SCH DEP (" + l[11] + "): " + l[2] + "\nSCH ARR (" + l[12] + "): " + l[3])
        print("\nPassenger Details:")
        print(l[13] + " " + l[14] + " " + l[15])
        print("BOOKING STATUS: " + l[7])
        print("CURRENT STATUS: " + l[8])
        print("\n")
    input("Press ENTER key to go back: ")
    userMode()



def adminMode():
    dict={}
    print("\n1. Add a Train")
    print("2. Assign Seats")
    print("3. Add Train Route")
    print("4. Reservation Chart")
    print("5. Delete a Train")
    print("6. Exit")
    choice = input("\nEnter your choice: ")
    if choice == "1":
        addTrain()
    elif choice == "2":
        assignSeats()
    elif choice == "3":
        addRouteDetails()
    elif choice == "4":
        reservationChart()
    elif choice == "5":
        deleteTrain()
    elif choice == "6":
        mainMenu()
    else:
        input("You have entered a wrong value. Press ENTER key to go back: ")
        adminMode()



def addTrain():
    train_no = int(input("Enter Train No: "))
    train_name = str(input("Enter Train Name: ")).upper()
    running_days = str(input("Enter running days seperated by comma(e.g. Monday,Wednesday): "))
    running_days_list = str(running_days.split(","))

    connect.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema ='rrs'")
    table_names = [i[0] for i in connect.cursor.fetchall()]
    if str(train_no) not in table_names:
        add_train_sql = '''CREATE TABLE IF NOT EXISTS `%s` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `station_code` VARCHAR(255) NOT NULL,
            `station_name` VARCHAR(255) NOT NULL,
            `arrival` TIME NOT NULL,
            `departure` TIME NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB;'''

        connect.cursor.execute(add_train_sql, train_no)
        connect.cursor.execute("INSERT INTO `trains` (train_no,train_name,running_days,coaches) VALUES(%s,%s,%s,'later')",(train_no,train_name,running_days_list))
        connect.db.commit()
        choice = input("Sucessfully Updated! Enter 1 to assign seats or 0 to go back: ")
        if choice == "1":
            assignSeats()
        elif choice == "0":
            adminMode()
        else:
            input("You have entered a wrong value. Press ENTER key to go back: ")
            adminMode()
    else:
        choice = input("Train already exists! Enter 1 to add in the table or 0 key to go back: ")
        if choice == "1":
            addRouteDetails()
        elif choice == "0":
            adminMode()

def addRouteDetails():
    # #INSERTING TRAIN ROUTE DETAILS
    train_no = int(input("Enter Train No: "))
    route = input("Enter the route details seperated by commas(e.g. station code, station name, arrival time in "
                  "HH:MM:SS format , departure time in HH:MM:SS format: ")
    # spaces removed from string if any
    no_space_route = route.replace(" ", "")
    route_list = no_space_route.split(",")
    sql = '''INSERT INTO `%s` (station_code,station_name,arrival,departure) VALUES(%s,%s,%s,%s)'''
    values = (train_no, route_list[0].upper(), route_list[1].upper(), route_list[2], route_list[3])
    connect.cursor.execute(sql, values)
    connect.db.commit()
    choice = input("Enter 1 to add more or 0 to go back: ")
    if choice == "1":
        addRouteDetails()
    elif choice == "0":
        adminMode()
    else:
        input("You have entered a wrong value. Press ENTER key to go back: ")
        adminMode()

def assignSeats():
    dict = ''
    train_no = input("Enter train number to assign seats: ")
    sleeper = int(input("Enter no of coaches of SL: "))
    second_ac = int(input("Enter no of coaches of 2A: "))
    third_ac = int(input("Enter no of coaches of 3A: "))
    # {"2A":1,"3A":4,"SL":11}
    assignSeats.dict = '{"2A":' + str(second_ac) + ',"3A":' + str(third_ac) + ',"SL":' + str(sleeper) + '}'
    connect.cursor.execute("UPDATE `trains` SET coaches = %s WHERE train_no = %s",(assignSeats.dict,int(train_no)))
    connect.db.commit()
    choice = input("Sucessfully Updated! Enter 1 to add routes or 0 to go back: ")
    if choice == "1":
        addRouteDetails()
    elif choice == "0":
        adminMode()
    else:
        input("You have entered a wrong value. Press ENTER key to go back: ")
        adminMode()

def reservationChart():
    train_no = int(input("Enter Train No: "))
    print("-" * 55)
    print("RESERVATION CHART FOR TRAIN NO. "+str(train_no))
    print("-" * 65)
    print("NAME     GENDER AGE    BERTH          PNR        BOARD  DESTINATION")
    print("-" * 65)
    connect.cursor.execute("SELECT * FROM `user_bookings` WHERE train_no = %s", (train_no))
    for l in connect.cursor:
        print(l[13]+"     "+l[15]+l[14]+"      "+l[8]+"  "+l[6]+"      "+l[11]+"      "+l[12])
    input("Press ENTER key to go back: ")
    adminMode()

def deleteTrain():
    train_no = int(input("Enter Train No: "))
    connect.cursor.execute("DROP TABLE `%s`",(train_no))
    connect.cursor.execute("DELETE FROM `trains` WHERE train_no = %s",(train_no))
    connect.db.commit()
    input("Successfully Deleted! Press ENTER key to go back: ")
    adminMode()