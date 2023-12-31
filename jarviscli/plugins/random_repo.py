# All plugins should inherite from this library
from github3 import login,GitHub, exceptions
from colorama import Fore
from random import randint
from plugin import alias, plugin, require
# This is the standard form of a plugin for jarvis

# Anytime you make a change REMEMBER TO RESTART Jarvis

# You can run it through jarvis by the name
# in the @plugin tag.


class RandomProjectPicker:
    def getRandomRepo(self,repo_gen,jarvis):
        repos=[]
        try:
           for repo in repo_gen:
               repos.append(repo)
           n=len(repos)
           jarvis.say("Number of repo: "+str(n),Fore.YELLOW)
           chosen_repo=repos[randint(0,n-1)];
           jarvis.say("The Chosen repo is: "+chosen_repo.name,Fore.YELLOW)
        except(exceptions.NotFoundError):
            jarvis.say("User Not Found!",Fore.RED)
        self.run(jarvis)
    def loginWithToken(self,jarvis):
        auth_token = jarvis.input("Give Jarvis your Github Access Token: ",Fore.YELLOW)
        try:
            g=login(token=auth_token)
            g.me()
            repo_gen=g.repositories(type='owner')
            self.getRandomRepo(repo_gen,jarvis)
        except(exceptions.AuthenticationFailed):
            jarvis.say("Inavlid Access Token!",color=Fore.RED)
            self.run(jarvis)

    def noLogin(self,jarvis):
        username = jarvis.input("Give Jarvis your Github username: ",Fore.YELLOW)
        g=GitHub()
        #try:
        repo_gen=g.repositories_by(username)
        self.getRandomRepo(repo_gen,jarvis)
            
    def run(self,jarvis):
    
        jarvis.say("Choose login method:",color=Fore.YELLOW)
        jarvis.say("1. With Personal Access Token.",color=Fore.YELLOW)
        jarvis.say("2. No login.",color=Fore.YELLOW)
        jarvis.say("3. Close.",color=Fore.YELLOW)
        choice=jarvis.input("Enter your choice: ",color=Fore.GREEN).strip();
        while (choice<"1" or choice>"3"):
            jarvis.say("Invalid choice!",color=Fore.RED)
            choice=jarvis.input("Enter your choice: ",color=Fore.GREEN).strip();
        if (choice =="1"):
            RandomProjectPicker().loginWithToken(jarvis)
        elif (choice == "2"):
            RandomProjectPicker().noLogin(jarvis)

@alias('random github repo')
@require(network=True)
@plugin('random repo')

def my_plugin(jarvis, s):
    RandomProjectPicker().run(jarvis)

