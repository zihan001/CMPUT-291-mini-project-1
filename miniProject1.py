#---------------------------------------------
# Mini-Project 1
# 
# 
# created by: ahlee1   (Alfred Lee)
#             azhossai (Ahmed Zihan Hossain)
#             cmmacleo (Connor Macleod)
#---------------------------------------------

import sqlite3
import getpass
import random
import time
from operator import itemgetter
from datetime import date

##################################################################################
# AHMED CODE
##################################################################################

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.create_function('num_matches_two', 2, num_matches_two)
    connection.commit()
    return

def signup():
    # Inserts uid, name and password into user table in database.
    global connection, cursor
    
    # Adds all existing uid in users table to a list.
    userList = []
    cursor.execute("SELECT DISTINCT uid FROM users;")
    used_uid = cursor.fetchall()
    for i in used_uid:
        if i not in userList:
            userList.append(i)

    # Check if entered uid not in list and less than
    # or equal to 4 characters.
    valid_uid = 0
    while not valid_uid:
        uid = input("Enter an uid: ")
        if (len(uid) <= 4) and all(uid not in x for x in userList):
            valid_uid = 1
        else:
            print("Invalid uid. Try again.")
    name = input("Enter name: ")
    pwd = input("Enter a password: ")
    valid_pass = 0
    cursor.execute("INSERT INTO users VALUES (?, ?, ?);", (uid, name, pwd),)
    connection.commit()
    print("You are now signed up!")
    return

def start_sesh(sesh, uid):
    # if session not active, starts a new session and returns its sno
    # else returns sno of current session
    global connection, cursor

    if sesh == 0:
        # Adds all existing sno in sessions table to a list.
        randomList=[]
        cursor.execute("SELECT DISTINCT sno FROM sessions;")
        used_sesh = cursor.fetchall()
        for i in used_sesh:
            randomList.append(i[0])

        # if randomly generated number not in list, valid sno.
        newrandom = 0
        while not newrandom:
            r = random.randint(1,10000)
            if r not in randomList:
                newrandom = 1
                sno = r
                randomList.append(r)
        start = date.today()
        cursor.execute("INSERT INTO sessions VALUES (?, ?, ?, NULL);", (uid, sno, start),)
        connection.commit()
        print("Session started.")
        return sno
    else:
        print("Session already active.")
        cursor.execute("SELECT sno FROM sessions WHERE uid = ? AND end = NULL", (uid),)
        sno = cursor.fetchall()
        return sno

def end_sesh(sesh, sno, uid):
    # ends the session by adding date to the end column of sessions table in database.
    global connection, cursor

    end = date.today()
    cursor.execute("UPDATE sessions SET end = ? WHERE lower(uid) = ? AND sno = ? AND end IS NULL;", (end, str(uid.lower()), sno),)
    connection.commit()
    print("Session Ended")
    return 0

def user_menu(uid):
    # Prompts user to enter a number to access features for users
    global connection, cursor, sno, sesh

    sno = 0
    logged_out = 0
    sesh = 0
    while not logged_out:
        print("\nPress the number")
        print("1: Start session")
        print("2: Search for songs and playlists")
        print("3: Search for artists")
        print("4: End session")
        print("5: Log out")
        print("6: Exit")
        option = input("What do you want to do? ")
        if option == "1":
            sno = start_sesh(sesh, uid)
            sesh = 1
        elif option == "2":
            keywords = input("Please enter keywords: ")
            SearchSongsAndPlaylists(uid, keywords)
        elif option == "3":
            searchArtists(uid)
        elif option == "4":
            if sesh == 1:
                sesh = end_sesh(sesh, sno, uid)
            else:
                print("Session not active.")
        elif option == "5":
            if sesh == 1:
                sesh = end_sesh(sesh, sno, uid)      # session is ended when logging out and exiting as well.
            print("Logged Out")
            return 0
        elif option == "6":
            if sesh == 1:
                sesh = end_sesh(sesh, sno, uid)
            print("Exiting...")
            return 1
        else:
            print("Invalid. Try again")

def artist_menu(aid):
    # Prompts artist to enter a number to access features for artists
    global connection, cursor

    logged_out = 0
    while not logged_out:
        print("\nPress the number")
        print("1: Add a song")
        print("2: Find top fans and playlists")
        print("3: Log out")
        print("4: Exit")
        option = input("What do you want to do? ")
        if option == "1":
            addSong(aid)
        elif option == "2":
            Top3Fans(aid)
            Top3Playlists(aid)
        elif option == "3":
            print("Logged Out")
            return 0
        elif option == "4":
            print("Exiting...")
            return 1
        else:
            print("Invalid. Try again")

def login():
    # login if valid id provided or signup
    # asks for password and checks if id and pass match
    # if id in both tables asks to login as which
    # else goes to the relevant menu.
    global connection, cursor
    
    valid_id = 0
    while not valid_id:
        id = input("Enter id to login or type 'signup' to signup: ")
        if id == "signup":
            signup()
        else:
            cursor.execute("SELECT uid FROM users;")
            user_ids = cursor.fetchall()
            cursor.execute("SELECT aid FROM artists;")
            artist_ids = cursor.fetchall()
            if any(id in x for x in user_ids) or any(id in x for x in artist_ids):
                wrong_pass = 1
                while wrong_pass:
                    password = getpass.getpass(prompt = "Enter password")
                    cursor.execute("SELECT uid, pwd FROM users WHERE uid = ? AND pwd = ?;", (id, password),)
                    login_list = cursor.fetchall()
                    cursor.execute("SELECT aid, pwd FROM artists WHERE aid = ? AND pwd = ?;", (id, password),)
                    login_list += cursor.fetchall()
                    login_check = (id, password)
                    if login_check in login_list:       # check if (id, pass) match with database
                        wrong_pass = 0
                        valid_id = 1
                    else:
                        print("Wrong password.")
                        prompt = input("Press 'q' to go back, press any other letter to try again: ")
                        if prompt == 'q':
                            wrong_pass = 0
            else:
                print("id not valid.")
    if any(id in x for x in user_ids) and any(id in p for p in artist_ids):     # if id in both tables
        type_check = input("Enter 'user' to login as an user or enter 'artist' to login as an artist")
        if type_check == "user":
            return user_menu(id)
        if type_check == "artist":
            return artist_menu(id)
    elif any(id in x for x in user_ids):
        return user_menu(id)
    elif any(id in x for x in artist_ids):
        return artist_menu(id)

##################################################################################
# CONNOR CODE
##################################################################################

# function helps Search for Artists
def num_matches(name, title, keywords):
    global connection, cursor

    keywords = keywords.split(' ')

    count = 0

    for keyword in keywords:
        if keyword in name.lower():
            count += 1
        elif keyword in title.lower():
            count += 1

    return count

def num_matches_two(name, keywords):
    global connection, cursor

    keywords = keywords.split(' ')

    count = 0

    for keyword in keywords:
        if keyword in name.lower():
            count += 1

    return count

def searchArtists(uid):
    global connection, cursor

    connection.create_function('num_matches', 3, num_matches)

    userKeys = input("Please Enter Keywords seperated by a space:\n").lower()

    page = 0
    finished  = False
    while not finished:

        ####### DOES NOT SHOW ARTISTS THAT DON'T HAVE A SONG

        cursor.execute("SELECT name, nationality, acnt, aid, MAX(ord) FROM (SELECT DISTINCT a.name, a.nationality, artcnt.acnt, a.aid, num_matches(a.name, s.title, ? ) as ord\
                        from (SELECT DISTINCT a.aid, count(*) AS acnt FROM perform pe LEFT JOIN artists a ON lower(pe.aid) = lower(a.aid) WHERE lower(pe.aid) = lower(a.aid) GROUP BY lower(a.aid)) AS artcnt,\
                        artists a, songs s, perform pe\
                        WHERE s.sid = pe.sid AND lower(a.aid) = lower(pe.aid) AND lower(a.aid) = lower(artcnt.aid)\
                        UNION\
                        SELECT DISTINCT a.name, a.nationality, 0 as acnt, a.aid, num_matches_two(a.name, ? ) as ord\
                        FROM artists a\
                        WHERE lower(a.aid) NOT IN (SELECT lower(aid) FROM perform))\
                        WHERE ord > 0\
                        GROUP BY aid ORDER BY ord DESC;",( userKeys, userKeys))

        # print results
        print("----------------------------------")
        artists = cursor.fetchall()
        if not artists:
            print('No more Artists, go to previous page')
            page -= 5
        else:
            num = page
            try:
                print("Row, Artist Name, Nationality, Song Count")
                for i in range(5):
                    print(str(page + i) + ": " + artists[page + i][0] + "  "+ artists[page + i][1] + "  " + str(artists[page + i][2]))
            except:
                pass
        print("----------------------------------")

        maxres = len(artists) - 1

        # user input
        userInput = input("Type 's' to stop search, 'n' for next page, 'p' for previous page\nOr, Select the artist by search rank on this page to view their songs\n")
        
        # input code
        if userInput == "s":
            finished = True
        elif userInput == "n" and page <= maxres / 5:
            page += 5
        elif userInput == "p" and page >= 5:
            page -= 5
        else:
            
            try:
                userInput = int(userInput)

                if int(userInput) >= 0 and int(userInput) <= maxres:
                    aid = artists[userInput][3]
                    se = False
                    while not se:

                        cursor.execute("Select s.sid, s.title, s.duration\
                                        from songs s, perform pe\
                                        where s.sid = pe.sid and lower(pe.aid) = lower( ? );", (aid,))
                        results = cursor.fetchall()
                        print("-------------Songs----------------")
                        for result in results:
                            print(str(result[0]) + ",  " + result[1] +",  " + str(result[2]))
                        print("----------------------------------")
                        sid = input("Select a song by SID or select 'b' to go back: ")

                        if sid == "b":
                            se = True
                        else:
                            cursor.execute("Select s.sid, s.title, s.duration\
                                            from songs s, perform pe\
                                            where s.sid = ? and s.sid = pe.sid and lower(pe.aid) = lower( ? );", (sid, aid))
                            if cursor.fetchall():
                                songActions(sid, uid)
                                se = True
                            else:
                                print("Invalid Input")
                else:
                    print("Selection out of range")
            except:
                print("Invalid input")




    return
        

####### NOT FULLY TESTED
def listenToSong(userid, songid):
    global connection, cursor, sno, sesh

    ######### CREATING NEW SESSION NOT TESTED
    # create new sess
    if not sesh:
        # create session and get session number
        sessnum = start_sesh(0, userid)
        sno = sessnum
        sesh = 1
    else:
        sessnum = sno

    #inserting a row
    try:
        cursor.execute("INSERT INTO listen values(?, ?, ?, 1);", (userid, sessnum, songid)) # sno given from previous query, uid & sid from system
        connection.commit()
    except:
        cursor.execute("UPDATE listen SET cnt = cnt + 1 WHERE uid = ? AND sno = ? AND sid = ?", (userid, sessnum, songid))
        connection.commit()

    print("----------------------------------")
    print("Listened to song with SID: "+ songid)
    print("----------------------------------")

    return


#
def songInfo(songid):
    global connection, cursor

    print("----------------------------------")

    # print artist featured
    cursor.execute("SELECT a.name\
                    FROM artists a, perform pe, songs s\
                    WHERE s.sid = ? AND pe.sid = s.sid AND lower(pe.aid) = lower(a.aid);", (songid,))
    results = cursor.fetchall()
    for name in results:
        print(name[0] + ', ', end="")
    print("")

    # print song info
    cursor.execute("SELECT s.sid, s.title, s.duration\
                    FROM songs s\
                    WHERE lower(s.sid) = lower( ? );", (songid,))
    results = cursor.fetchall()
    print(str(results[0][0]) + ", " + results[0][1] + ", " + str(results[0][2])) # results[0] + ", " + results[1] + ", " + results[2]

    # print playlists song is in
    cursor.execute("SELECT distinct p.title\
                    FROM playlists p, plinclude pl\
                    WHERE p.pid = pl.pid AND lower(pl.sid) = lower( ? );", (songid,))
    results = cursor.fetchall()
    for songplay in results:
        print(songplay[0] + ', ', end="")
    print("")
    print("----------------------------------")

    return

def addToPlaylist(userid, songid):
    global connection, cursor

    # selects playlists that the user owns
    cursor.execute("Select p.pid, p.title\
                    from playlists p\
                    where lower(p.uid) = lower( ? )", (userid,))

    # print playlists user can add song to
    playlists = cursor.fetchall()
    for playlist in playlists:
        print(str(playlist[0]) +",  "+ playlist[1])

    # user selects either PID or a new playlist title (title selected by input not being a known PID)
    userIn = input("Type the Playlist by PID (first column) or type 'c' to create a new playlist: ").lower()

    # create new playlist
    if userIn == 'c':
        ptitle = input("Enter the title of the new playlist: ")

        # generate new pid
        cursor.execute("Select MAX(p.pid)\
                        from playlists p")
        playid = cursor.fetchall()[0][0] + 1

        cursor.execute("insert into playlists values(?, ?, ?)", (playid, ptitle, userid)) # uid & pid from system, title from user
        connection.commit()

        order = 1

        cursor.execute("insert into plinclude values(?, ?, ?);", (playid, songid, order))
        connection.commit()

        print("----------------------------------")
        print("Created playlist and added song!")
        print("----------------------------------")

    # add to existing playlist
    else:
        # check if song is in playlist selected
        cursor.execute("SELECT pl.pid FROM plinclude pl WHERE pl.pid = ? and pl.sid = ?;", (userIn, songid))
        results_s = cursor.fetchall()

        if not results_s:
            # check if user input is an existing playlist
            cursor.execute("SELECT p.pid FROM playlists p WHERE p.pid = ?;", (userIn,))
            results_p = cursor.fetchall()
            # check if user input is in playlists
            

            #-- if new playlist (result is NULL)
            if not results_p:
                print("----------------------------------")
                print("Playlist doesn't exist")
                print("----------------------------------")
            else:
                playid = userIn

                #-- Add song to playlist
                #-- for finding the order of the new song
                cursor.execute("Select MAX(pl.sorder), pl.pid \
                                from plinclude pl\
                                where pl.pid = ?;", (playid,))
                order = cursor.fetchall()
                if order[0][0] == None:
                    order = 1
                else:
                    order = order[0][0] + 1
                #-- add 1 to previous query and make that the inserted song's 'sorder'
                cursor.execute("insert into plinclude values(?, ?, ?);", (playid, songid, order))
                connection.commit()

                print("----------------------------------")
                print("Song added to playlist!")
                print("----------------------------------")

        else:
            print("----------------------------------")
            print("Song already exists in that playlist")
            print("----------------------------------")
    return



def addSong(artid):
    global connection, cursor

    newTitle = input("Enter song title: ")
    trying = True
    while trying:
        try:
            newDuration = int(input("Enter song duration: "))
            trying = False
        except:
            print("Invalid duration")

    #--"Two different artists can have a song with the same name and duration."
    cursor.execute("Select s.title, s.duration\
                    from songs s, perform pe\
                    where lower(s.title) = lower( ? ) and s.duration = ? and s.sid = pe.sid and pe.aid = ?;", (newTitle, newDuration, artid))

    #-- ask if user wants to add duplicate song values if result isn't NULL
    userIn = "Y"
    if cursor.fetchall():
        selected = False
        while not selected:
            userIn = input("You already have a song with this Title and Duration, proceed anyways? (Y or N)\n")
            if userIn == "Y" or userIn == "N":
                selected = True
            else:
                print("Invalid input")

    if userIn == "Y":

        # generate song id
        cursor.execute("Select MAX(s.sid)\
                        from songs s")
        newsid = cursor.fetchall()
        if newsid[0][0] == None:
            newsid = 1
        else:
            newsid = newsid[0][0] + 1

        cursor.execute("insert into songs values(?, ?, ?);", (newsid, newTitle, newDuration))
        connection.commit()

        #-- insert each artist (by aid) given by user
        # initial artist
        cursor.execute("insert into perform values(?, ?);", (artid, newsid))
        connection.commit()

        adding = True
        while adding:
            peradd = input("Add another artist (by aid) or select '1' to stop adding: ")

            if peradd == "1":
                adding = False
            else:

                # check if artist exists
                cursor.execute("SELECT a.aid FROM artists a WHERE a.aid = ?", (peradd,))
                res = cursor.fetchall()

                if not res:
                    print("Invalid AID")
                else:
                    # adds artist
                    try:
                        cursor.execute("insert into perform values(?, ?);", (peradd, newsid))
                        connection.commit()
                        print("Artist added!")
                    except:
                        print("Artist already added")
    else:
        print("No song was added")

    return

# song selected
def songActions(sid, uid):
    d = False
    while not d:
        print("Select an action for SID "+ sid +":\n1. Listen to song:\n2. See more Information\n3. Add to playlist\n4. Cancel")
        userIn = input("Select action (1, 2, 3, or 4): ")

        if userIn == "1":
            listenToSong(uid, sid)
        elif userIn == "2":
            songInfo(sid)
        elif userIn == "3":
            addToPlaylist(uid, sid)
        elif userIn == "4":
            d = True
        else:
            print("Invalid Input")

##################################################################################
# ALFRED CODE
##################################################################################

def SearchSongsAndPlaylists(uid,keywords):
    global connection, cursor

    # Create a table of keywords we want to search for
    Values = ""
    for i in keywords.split():
        Values += "('{}'),".format(i.lower())

    # Remove last comma
    Values = Values[:-1]

    # Create a table with the keywords we want to search for
    # Using that table look for matches in songs by joining if any title matches
    # Now group and use count to see number of matches
    cursor.execute("WITH matches(keyword) AS (VALUES {})\
                    SELECT s.sid, s.title, s.duration, COUNT(*)\
                    FROM songs s INNER JOIN matches m\
                    ON s.title LIKE '%' || m.keyword || '%'\
                    GROUP BY s.sid, s.title, s.duration\
                    ORDER BY COUNT(*) DESC;".format(Values))
    songs = cursor.fetchall()
    cursor.execute("WITH matches(keyword) AS (VALUES {})\
                    SELECT p.pid, p.title, p.duration, COUNT(*)\
                    FROM (SELECT p.pid, p.title, SUM(s.duration) AS duration\
                          FROM playlists p, plinclude pi, songs s\
                          WHERE p.pid = pi.pid\
                          AND pi.sid = s.sid\
                          GROUP BY p.pid, p.title\
                          UNION\
                          SELECT p.pid, p.title, 0 AS duration\
                          FROM playlists p\
                          WHERE p.pid not IN(SELECT DISTINCT pid\
                                            FROM plinclude)) as p\
                    INNER JOIN matches m\
                    ON p.title LIKE '%' || m.keyword || '%'\
                    GROUP BY p.pid, p.title, p.duration\
                    ORDER BY COUNT(*) DESC;".format(Values))
    playlists = cursor.fetchall()

    # Add song and playlist value to both lists, then join both lists ordering by number of matches
    total = [list(song)+['Song'] for song in songs]
    total += [list(playlist)+['Playlist'] for playlist in playlists]
    total = sorted(total, key=itemgetter(3), reverse=True)

    done = False
    row = 1
    print("Row Id          Title Duration     Type")
    while not done:
        # Print 5 values in the table
        for i in range(5):
            if(row-1>=len(total)):
                done = True
                print("End of Search")
                break
            print("{0:>3}{1:>3}{2:>15}{3:>9}{5:>9}".format(row,*total[row-1]))
            row+=1
        # Depending on user input
        if(done == True):
            inp = input("Choose Row or E to exit: ")
        else:
            inp = input("Choose Row or C to continue: ")
        try:
            if(inp.lower()=="e" and done == True):
                return
            elif(inp.lower()=="c" and done == False):
                continue
            # only if value has been printed can user select it
            elif(int(inp)<=row and int(inp)>=1):
                # Depending on if song or playlist
                if(total[int(inp)-1][4] == "Playlist"):
                    playlistInfo(str(total[int(inp)-1][0]), str(total[int(inp)-1][1]), uid)
                elif(total[int(inp)-1][4] == "Song"):
                    songActions(str(total[int(inp)-1][0]),uid)
                return
            else:
                print("Not Valid Input")
                return
        except ValueError:
            print("Not Valid Input")
            return
            
    return

def playlistInfo(playlistid, playlistname, uid):
    global connection, cursor

    # Selects songs in selected playlist
    cursor.execute("SELECT * \
                    FROM songs s\
                    WHERE s.sid IN ( SELECT p.sid\
                                     FROM plinclude p\
                                     WHERE p.pid = ?);", (playlistid,))
    playlists = cursor.fetchall()

    # Print the songs in the playlist
    print("\n",playlistname," songs:")
    print("Row Id          Title Duration")
    for i in range(1,len(playlists)+1):
        print("{0:>3}{1:>3}{2:>15}{3:>9}".format(i,*playlists[i-1]))

    # Let user select a song in playlist
    inp = input("Choose Row or e to exit: ")
    try:
        if(inp.lower()=="e"):
            return
        elif(int(inp)<=len(playlists) and int(inp)>=1):
            songActions(str(playlists[int(inp)-1][0]),uid)
            return
        else:
            print("Not Valid Input")
            return
    except ValueError:
        print("Not Valid Input")
        return
    return

def Top3Fans(aid):
    global connection, cursor

    # Select Artists Top 3 Fans
    cursor.execute("SELECT listen.uid, SUM(listen.cnt*songs.duration)\
                    FROM listen, songs\
                    WHERE listen.sid IN (SELECT perform.sid\
                                        FROM perform, artists\
                                        WHERE perform.aid = ?) \
                    AND listen.sid = songs.sid\
                    GROUP BY listen.uid\
                    ORDER BY SUM(listen.cnt*songs.duration) DESC\
                    LIMIT 3;", (aid,))
    fans = cursor.fetchall()

    # Print Top 3 Fans
    print("Top 3 Fans")
    print("Row UID")
    for i in range(1,len(fans)+1):
        print("{0:>3}{1:>3}".format(i,fans[i-1][0]))
    return

def Top3Playlists(aid):
    global connection, cursor

    # Select Artists Top 3 Playlists
    cursor.execute("SELECT plinclude.pid, COUNT(plinclude.sid)\
                    FROM plinclude\
                    WHERE plinclude.sid IN (SELECT perform.sid\
                                            FROM perform, artists\
                                            WHERE perform.aid = ?)\
                    GROUP BY plinclude.pid\
                    ORDER BY COUNT(plinclude.sid) DESC\
                    LIMIT 3;", (aid,))
    playlists = cursor.fetchall()

    print("Top 3 Playlists")
    print("Row PID")
    # Print Top 3 Playlists
    for i in range(1,len(playlists)+1):
        print("{0:>3}{1:>3}".format(i,playlists[i-1][0]))
    return

def main():
    # main function of program
    global connection, cursor

    path = input("Enter path: ")
    connect(path)

    exit = 0
    while not exit:
        exit = login()

    connection.commit()
    connection.close()
    return

    # something happens and we get 100% :)

if __name__ == "__main__":
    main()