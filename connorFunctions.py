import sqlite3

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

def searchArtists(uid):
    global connection, cursor

    connection.create_function('num_matches', 3, num_matches)

    userKeys = input("Please Enter Keywords seperated by a space:\n").lower()

    page = 0
    finished  = False
    while not finished:

        ####### DOES NOT SHOW ARTISTS THAT DON'T HAVE A SONG

        cursor.execute("SELECT DISTINCT a.name, a.nationality, artcnt.acnt, a.aid\
                        from (SELECT DISTINCT a.aid, count(*) AS acnt FROM perform pe LEFT JOIN artists a ON pe.aid = a.aid WHERE pe.aid = a.aid GROUP BY a.aid) AS artcnt,\
                        artists a, songs s, perform pe\
                        WHERE s.sid = pe.sid AND lower(a.aid) = lower(pe.aid) AND lower(a.aid) = lower(artcnt.aid)\
                        ORDER BY num_matches(a.name, s.title, ? ) DESC;",( userKeys,))

        # print results
        print("----------------------------------")
        artists = cursor.fetchall()
        if not artists:
            print('No more Artists, go to previous page')
            page -= 5
        else:
            num = page
            try:
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
    global connection, cursor

    # Select sessions without an end
    cursor.execute("Select se.sno\
                    from sessions se, users u\
                    where se.end is NULL AND se.uid = ?;", (userid,))
    sessresults = cursor.fetchall()


    ######### CREATING NEW SESSION NOT TESTED
    # create new sess
    if not sessresults:
        # create session and get session number
        sessnum = start_sesh(0, userid)

    else:
        sessnum = sessresults[0][0]

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




def delete_data():
    global connection, cursor
    cursor.execute("DELETE FROM users;")
    cursor.execute("DELETE FROM songs;")
    cursor.execute("DELETE FROM sessions;")
    cursor.execute("DELETE FROM listen;")
    cursor.execute("DELETE FROM playlists;")
    cursor.execute("DELETE FROM plinclude;")
    cursor.execute("DELETE FROM artists;")
    cursor.execute("DELETE FROM perform;")
    connection.commit()
    return

def insert_data_c():
    global connection, cursor

    cursor.execute('''insert into users values 
                    ('cmma', 'Connor', '123'),
                    ('Rad7', 'RANDOM', '123'),
                    ('kait', 'Kaitlyn', '456');''')

    cursor.execute('''insert into songs values 
                    (50 , 'Unity', 165), 
                    (51 , 'Xenogenesis', 177),
                    (52 , 'Jackpot', 123),
                    (53 , 'Spectre', 180),
                    (54 , 'Unity', 170),
                    (55 , 'Sing Me To Sleep', 150),
                    (56 , 'Levels', 160),
                    (57 , 'The Nights', 100),
                    (59 , 'rAnDsOnG', 10),
                    (60 , 'RaNdSoNg', 1000),
                    (58 , 'Wake Me Up', 180);''')

    cursor.execute('''insert into sessions values 
                    ('cmma', 1, '2022-09-20', '2022-09-22'),
                    ('cmma', 2, '2022-10-27', NULL),
                    ('rAd7', 20, '1978-01-01', NULL),
                    ('kait', 1, '2021-03-10', '2021-03-15');''')

    cursor.execute('''insert into listen values 
                    ('cmma', 1, 50, 1),
                    ('cmma', 1, 57, 1),
                    ('rAD7', 20, 59, 100.01),
                    ('rAD7', 20, 60, 69.69),
                    ('cmma', 1, 58, 1),
                    ('cmma', 1, 54, 1),
                    ('cmma', 2, 55, 1),
                    ('kait', 1, 53, 1),
                    ('kait', 1, 50, 1);''')

    cursor.execute('''insert into playlists values 
                    (70, 'EDM Tracks 1', 'cmma'),
                    (72, 'EDM Tracks 2', 'cmma'),
                    (1935, 'IiIiIs Greatest Hits', 'rAd7'),
                    (71, 'Now This is Music', 'kait');''')

    cursor.execute('''insert into plinclude values 
                    (70, 57, 1),
                    (70, 58, 2),
                    (70, 54, 3),
                    (70, 50, 4),
                    (70, 55, 5),
                    (72, 55, 1),
                    (71, 54, 1),
                    (71, 57, 2),
                    (71, 50, 3),
                    (71, 52, 4);''')

    cursor.execute('''insert into artists values 
                    ('ftrt', 'TheFatRat', 'German', '1234'),
                    ('alwa', 'Alan Walker', 'Norwegian', '5678'),
                    ('avic', 'Avicii', 'Swedish', '9012'),
                    ('none', 'name0', 'Canadian', '3456'),
                    ('ntwo', 'nametwo', 'Canadian', '7890'),
                    ('IJkl', 'IiIiI', 'NunyaBiz', 'password'),
                    ('eFgH', 'EeEeE', 'NunyaBiz', 'PASSword'),
                    ('AbCd', 'AaAaA', 'NunyaBiz', 'passWORD'),
                    ('nthr', 'nameIII', 'Canadian', '1357'),
                    ('nfor', 'namefor', 'Canadian', '2468');''')

    cursor.execute('''insert into perform values 
                    ('ftrt', 50),
                    ('ftrt', 51),
                    ('ftrt', 52),
                    ('alwa', 53),
                    ('alwa', 54),
                    ('alwa', 55),
                    ('avic', 56),
                    ('avic', 57),
                    ('ijkL', 59),
                    ('ijKl', 60),
                    ('efGh', 60),
                    ('none', 57),
                    ('ntwo', 57),
                    ('nthr', 57),
                    ('nfor', 57),
                    ('avic', 58);''')
    connection.commit()
    return


def main():
    global connection, cursor

    database = 'test.db'  # name of database used here

    # connecting the database
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    delete_data()
    insert_data_c()



if __name__ == '__main__':
    main()