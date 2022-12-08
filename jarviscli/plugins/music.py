# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:33:46 2022

@author: alexi
"""
from urllib.request import urlopen
import pygame
import bs4
import re
import pafy
import vlc
import sqlite3


from plugin import plugin
from plugin import require

@require(network=True)
@plugin("music")
def music(jarvis,s):

    global cursor
    script_location=__file__
    #Database for the music playlist, using sqlite
    data_base = sqlite3.connect(script_location+"\playList1.db")
    cursor=data_base.cursor() 

    #Table creation
    cursor.execute('Create Table  if not exists Playlists(title char(50) primary key)')
    cursor.execute('Create Table  if not exists Song(playlist char(50) references Playlists(title),title char(50),key char(11) primary key)')

    #First playlist creation
    addPlayList("My_First_PlayList")
    end=False
    while not end:

        jarvis.say("\nHello! Bro what would you like to do")
        jarvis.say("\n1.Search some music")
        jarvis.say("\n2.Go to your playlists")
        jarvis.say("\n3. Ciao ? ")
        
        number=jarvis.input("Choose (1-3): ")
        
        try:
            number=int(number)
            
            #Checking the input
            if  number!=1 and number !=2 and  number!=3:
                jarvis.say("Choose the right number please\n")
            else:
                if number==1:   
                    research=jarvis.input("\nWhat would you like to hear ? : ")
                    search(jarvis,research)
                
                elif number==2:
                    playlists(jarvis)
                    
                else:
                    end=True

                    data_base.commit() #save the database

                    cursor.close() #close the cursor
                    data_base.close()#close the database
                
                    jarvis.say("Have a nice day !!!!\n")
        except:
            jarvis.say("A problem occured :'( \n")
        
    



"""
Search the keys and names of the musics and display them
It gives two options, add the song to a playlist or play the audio
"""
def search(jarvis,research):


    keys,names=find_keys(jarvis,research)

    #Displaying the video titles
    for i in range(1,len(names)+1):
        jarvis.say(f"{i}.{names[i-1]}")
    number=jarvis.input("\nChoose ? :")
    

    try:
        number=int(number)
        if number>len(names) or number<=0:
            jarvis.say("Choose a valid number please\n")
        else:
            jarvis.say("1.Add Song to a PlayList\n")
            jarvis.say("2.Play this Song\n")

            number_song=int(jarvis.input("\nChoose (1-2)? :"))

            if number_song==1:
                addSong_to_Playlist(jarvis,title=names[number-1],key=keys[number-1])
            else:
                play_audio(jarvis,keys[number-1]) 
    except:
        jarvis.say("Choose the right number please step broo !!\n")
        


"""
Playlist management
"""
def playlists(jarvis):
    jarvis.say("\n1.Add a PlayList")
    jarvis.say("\n2.Manage a PlayList")
    
    number=jarvis.input("\nChoose (1-2): ")
    
    try:
        number=int(number)
        jarvis.say(str(number))
        if number not in [1,2]:
            jarvis.say("\nChoose the right number please broo !!")
        else:
            if number==1:
                name=jarvis.input("\nGive me the name of the Playlist that you want to add:: ")
                addPlayList(name)
            else:
                
                jarvis.say("Select a PlayList\n")
                playlists=getPlayLists()
                
                

                for i in range(0, len(playlists)):
                    jarvis.say(f"{i}.{playlists[i][0]}")

                number_playlists=jarvis.input("Give me the number of the Playlist that you want to manage : \n")

                try :
                    number_playlists=int(number_playlists)

                except:
                    jarvis.say("\nChoose a valid number please!!")
                
                jarvis.say("\n1.Supress this playlist")
                jarvis.say("2.Supress a song from this playlist")
                jarvis.say("3.Play this Playlist")

                number=jarvis.input("\nWhat do you want to do:")

                try :
                    number=int(number)

                    if number==1:
                        removePlayList(playlists[number_playlists][0])
                    elif number==2:
                        jarvis.say("\n Select a Song to remove\n")
                        Songs=getSong(playlists[number_playlists][0])
                        for i in range(0, len(Songs)):
                            jarvis.say(f"{i}.{Songs[i][0]}")

                        number_song=jarvis.input("\n Which song do you want to remove? (delect its number) :")

                        try:
                            number_song=int(number_song)
                            removeSong(playlists[number_playlists][0],Songs[number_song][0])
                        except:
                            jarvis.say("\nChoose a valid number")
                    
                    else: #playing a Song from a PlayList
                        keep_playing=True
                        while keep_playing:
                            jarvis.say("Select a song\n")
                            Songs=getSong(playlists[number_playlists][0])
                            for i in range(0, len(Songs)):
                                jarvis.say(f"{i}.{Songs[i][0]}")

                            number_song=jarvis.input("Which song do you want to play? \n")

                            try:
                                number_song=int(number_song)
                                jarvis.say(str(Songs[number_song][1]))
                                play_audio(jarvis,Songs[number_song][1])
                            
                            except:
                                jarvis.say("choose a valid number")
                        
                            jarvis.say("Do you want to listen another song? \nyes\nno")
                            keep_playing=jarvis.input("So !!??! : ")=="yes"



                
                except:
                    jarvis.say("A problem occured")
                        







                
    except:
        jarvis.say("A problem occured")
                
    
def addSong_to_Playlist(jarvis,title,key):
    playlists=getPlayLists()
    for i in range(1, len(playlists)+1):
                    jarvis.say(f"\n{i}.{playlists[i-1][0]}")
    number_playlists=int(jarvis.input("\nChoose your playlists broo : "))
    jarvis.say(title)
    jarvis.say(key)
    addSong(playlists[number_playlists-1][0],title.replace(' ','_'),key)



    

        



"""
Find the keys and the title of the youtube videos thanks to the research request
"""


def find_keys(jarvis,research):
    #Base url
    url="https://www.youtube.com/results?search_query="
    
    research=research.replace(' ','+')
    
    html=urlopen(url+research)
    
    #Getting the source code of the html page
    soup= bs4.BeautifulSoup(html,'html.parser')
    
    #getting all the keys of the videos
    results=re.findall('(((videoId)(.*?)(,)))',str(soup)) #récupérer les clefs pour accéder aux une vidéo youtube
    
    keys=[]
    names=[]
    
    count=0
    
    for clef in results:
        #cleaning of the keys
        clef=str(clef)[12:23]
        if keys==[]:
            keys.append(clef)
            
            #requesting the video
            video = pafy.new(clef)
        
            names.append(video.title)
            count+=1

        elif clef[0]!='[' and  clef not in keys:
            keys.append(clef)
            
            video = pafy.new(clef)
            names.append(video.title)
            count+=1

        if count>=10: #we only take the first 10 videos, it is possible to change the value of count
            break
    return keys,names #return keys of the youtube videos and the name of the videos ; keys=[key1,key2,key3,...] and names=[name1,name2,..]

"""
play the audio thanks to vlc
The audio can be paused by pressing any keyboard key
"""
def play_audio(jarvis,key):
    global media
    
    #find the youtube video
    video = pafy.new(key)

    
    bestaudio = video.getbestaudio()
    playurl = bestaudio.url

    try:
        # creating vlc media player object
        media = vlc.MediaPlayer(playurl)
        # start playing video
        media.play()
        media.audio_set_volume(100)
    except:
        jarvis.say("To play the music you must install VLC\ntry this:\nsudo apt install vlc -y")
    Game = True
    jarvis.say("Press any keyboard key to pause the music")
    pygame.init()
    display = pygame.display.set_mode((300, 300))
    pause = False
    while Game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                pygame.display.quit()
                pygame.quit()
                Game=False
                
                
            if event.type==pygame.KEYDOWN:
                media.set_pause(not pause)
                pause= not pause
                















"""
Add a new playlist
"""

def addPlayList(name):
    global cursor
    try:
        requete=f'Insert into playLists values("{name}")'
        print(requete)
        cursor.execute(requete) 
    except:
        pass
    

"""
Add a new song to a playlist
"""
def addSong(name_PlayList,title,key):
    global cursor
    requete=f'Insert into song values("{name_PlayList}","{title}","{key}")'
    cursor.execute(requete)

"""
Remove a song from a playlist
"""
def removeSong(name_PlayList,title):
    global cursor
    requete=f'Delete from Song where title=="{title}" and playlist=="{name_PlayList}"'
    a=cursor.execute(requete)
   
"""
Remove a playlist
"""  
def removePlayList(name_PlayList):
    global cursor
    requete1=f'Delete from playlists where title="{name_PlayList}"'
    requete2=f'Delete from Song where playlist="{name_PlayList}"'
    cursor.execute(requete1)
    cursor.execute(requete2)
    


"""
Get a song from a playlist
"""
def getSong(name_PlayList):
    global cursor
    requete=f'Select title,key from Song where playlist="{name_PlayList}" '
    songs=cursor.execute(requete).fetchall()     #songs=[('titre', 'clef'), ('titre2', 'clef2'),...]
    return songs

"""
Get a playlist
"""
def getPlayLists():
    global cursor
    requete=f'Select title from playlists'
    playlist=cursor.execute(requete).fetchall()
    return playlist