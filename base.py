
#------------------------Stat-Tracker---------------------------#

import os
import json

statsfile='wordlestats.json'
wordsfile='words.txt'

def loadstats():
    if os.path.exists(statsfile):
        with open(statsfile) as f:
            return json.load(f)
    return {
        'Played': 0,
        'Wins': 0,
        'Current Streak': 0,
        'Max Streak': 0,
        'Guess Distribution': {
            '1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0
        }
    }

def savestats(stats):
    with open(statsfile,'w') as f:
        json.dump(stats,f,indent=2)

def updatestats(stats,won,attempts):
    stats['Played']+=1
    if won:
        stats['Wins']+=1
        stats['Current Streak']+=1
        stats['Max Streak']=max(stats['Max Streak'],stats['Current Streak'])
        stats['Guess Distribution'][str(attempts)]+=1
    else:
        stats['Current Streak']=0
    savestats(stats)

#-------------------------Checker----------------------------#

def checker(guess,target):
    ''' 
    Function takes in user input guess word, checks letters against
    the specific target word.

    Two passes:
        Pass One: Checks for greens;
            Green for correct letter in correct space.
        Pass Two: Checks for yellows;
            Yellow for correct letter in word, incorrect space.
        Else returns gray;
            grey for letter is not in the target word.
    '''
    result=['grey']*5

    # list of letters in target word
    characters=list(target)

    # Pass One
    for i in range(5):
        if guess[i]==characters[i]:
            result[i]='green'
            characters[i]=None

    # Pass Two
    for i in range(5):
        if result[i]=='green':
            continue
        if guess[i] in characters:
            result[i]='yellow'
            characters[characters.index(guess[i])]=None

    return list(zip(guess,result))

#------------------------Notebook-Player-----------------------#

import random

def wordle():
    ''' 
    Reads in text file of words, randomizes a selection for each attempt.
    Tracks previous attempts each playthrough.
    Plays like the NYT Wordle; 6 attempts.
    '''
    words=open('words.txt').read().split()
    target=random.choice(words)
    
    priors=set()
    attempt=1

    while attempt<=6:

        # display the current attempt
        guess=input(f'Guess {attempt} of 6: ').lower().strip()
        
        # check for guess input less than 5 letters
        if len(guess)!=5:
            print('Answer must be 5 letters.')
            continue

        # checks for repeat guesses
        if guess in priors:
            print('Already guessed.')
            continue
        
        # checks for invalid words:
        if guess not in words:
            print('Not in word list.')
            continue

        # set tracker, only uses attempt if word is valid
        priors.add(guess)
        attempt+=1
        
        # checking the word
        result=checker(guess,target)
        print(' '.join(f'[{l}]' for l, _ in result))

        if guess==target:
            print(f'{winStatements[attempt-2]}')
            return

    print(f'The word was: {target}.')

#------------------------Terminal-Player-----------------------#

from colorama import Fore,Back,Style,init
import tkinter as tk

init(autoreset=True)

# set color scheme for letter guesses
terminalColors={
    'green':Back.GREEN+Fore.WHITE+Style.BRIGHT,
    'yellow':Back.YELLOW+Fore.WHITE+Style.BRIGHT,
    'grey':Back.LIGHTBLACK_EX+Fore.WHITE+Style.BRIGHT
}

def result2Terminal(result):
    row=''
    for letter,color in result:
        row+=terminalColors[color]+f'{letter.upper()}'+Style.RESET_ALL+' '
    print(row)

def stats2Terminal(stats):
    winPercent=int(stats['Wins']/stats['Played']*100)# if stats['Played']>0
    print(f"\nStats --> Times Played: {stats['Played']}   Win %: {winPercent}   Current Streak: {stats['Current Streak']}   Best Streak: {stats['Max Streak']}")
    print('\nGuess Distribution:')
    for k in range(1,7):
        count=stats['Guess Distribution'][str(k)]
        #bar=f':'*count
        print(f'   {k}: {count}')

def wordleTerminal(words):
    '''
    '''
    target=random.choice(list(words))
    stats=loadstats()
    priors=set()
    attempt=1

    print('\nTerminal Wordle\n')

    while attempt<=6:
        guess=input(f'Guess {attempt} of 6: ').lower().strip()
        
        if len(guess)!=5:
            print('Answer must be 5 letters.')
            continue
        if guess in priors:
            print('Already guessed.')
            continue
        if guess not in words:
            print('Not in word list.')
            continue
            
        priors.add(guess)
        result=checker(guess,target)
        result2Terminal(result)

        if guess==target:
            print(f'{winStatements[attempt-2]}')
            updatestats(stats,True,attempt)
            stats2Terminal(stats)
            return

        attempt+=1

    print(f'\n Unlucky. The word was: {target.upper()}')
    updatestats(stats,False,0)
    stats2Terminal(stats)

#------------------------GUI-Player---------------------------#

letterColors={
    'green':{'bg':"#008000",'fg':"white"},
    'yellow':{'bg':"#c9c869",'fg':"white"},
    'grey':{'bg':"#808080",'fg':"white"},
    'empty':{'bg':"#ffffff",'fg':"black"}
}
winStatements=[
    'Cheater.','Not bad I guess.','Great.','Satisfactory.','Close one.','Balright.'
]
# keyboard layout
keyboardLayout=[
    list('qwertyuiop'),
    list('asdfghjkl'),
    ['Enter']+list('zxcvbnm')+['⌫']
]

class wordle:
    def __init__(self,root,words):
        self.root=root
        self.root.title('Wordle 2.0')
        self.root.configure(bg='#ffffff')
        self.root.resizable(False,False)

        self.words=words
        self.target=random.choice(list(words))
        self.stats=loadstats()
        self.scale=scale

        self.currentRow=0
        self.currentGuess=[]
        self.priors=set()
        self.gameOver=False
        self.keyColors={}

        self.tiles=[]
        self.tileLabels=[]
        self.keyButtons={}

        self.buildUI()
        self.root.bind('<Key>',self.onKey)
    
    def s(self,n):
        return int(n*self.scale)

    #--------------------Building-The-UI----------------------#

    def buildUI(self):
        # build the header
        tk.Frame(self.root,bg='#a9b3c2',height=1).pack(fill='x')
        header=tk.Frame(self.root,bg='#ffffff',pady=self.s(10))
        header.pack(fill='x')
        tk.Label(header,text='Wordle 2.0',font=('Cascadia Mono',self.s(28),'bold'),
                 bg='#ffffff',fg='#161617').pack()
        tk.Frame(self.root,bg='#d3d6da',height=1).pack(fill='x')
        
        # build the tile grid
        gridFrame = tk.Frame(self.root, bg='#ffffff', pady=self.s(20))
        gridFrame.pack()
        
        for r in range(6):
            rowTiles,rowLabels=[],[]
            for c in range(5):
                frame=tk.Frame(
                    gridFrame,width=self.s(62),height=self.s(62),bg='#ffffff',
                    highlightbackground='#d3d6da',highlightthickness=2
                )
                frame.grid(row=r,column=c,padx=self.s(3),pady=self.s(3))
                frame.pack_propagate(False)

                label=tk.Label(frame,text='',font=('Cascadia Mono',self.s(24),'bold'),
                               bg='#ffffff',fg='#161617')
                label.pack(expand=True,fill='both')
                rowTiles.append(frame)
                rowLabels.append(label)
            self.tiles.append(rowTiles)
            self.tileLabels.append(rowLabels)

        # build the message bar
        self.msgLabel = tk.Label(
            self.root, text='',font=('Cascadia Mono',self.s(12),'bold'),
            bg='#ffffff',fg='#161617')
        self.msgLabel.pack(pady=self.s(4))      

        # build keyboard and stats
        self.buildKeyboard()
        self.buildStats()

        tk.Button(
            self.root,text='Play Again',
            font=('Cascadia Mono',self.s(11),'bold'),
            bg='#008000',fg='#ffffff',
            relief='flat',bd=0,
            padx=self.s(20),self.s(pady=8),
            command=self.resetGame
    ).pack(pady=self.s(12))

    def buildKeyboard(self):
        kbFrame=tk.Frame(self.root,bg='#ffffff',pady=self.s(8))
        kbFrame.pack()

        for rowKeys in keyboardLayout:
            rowFrame=tk.Frame(kbFrame,bg='#ffffff')
            rowFrame.pack(pady=self.s(2))

            for key in rowKeys:
                wide=key in ('Enter','⌫')
                bttn=tk.Button(
                    rowFrame,
                    text=key if wide else key.upper(),
                    font=('Cascadia Mono',self.s(10),'bold'),
                    bg='#d3d6da',fg='#161617',
                    width=6 if wide else 3,
                    height=2,
                    relief='flat',bd=0,
                    command=lambda k=key: self.onKeyButton(k)
                )
                bttn.pack(side='left',padx=self.s(2))
                if not wide:
                    self.keyButtons[key]=bttn

    def buildStats(self):
        statsFrame=tk.Frame(self.root,bg='#ffffff',pady=self.s(14))
        statsFrame.pack()

        self.statValLabels={}
        items=[
            ('Played','Played'),
            ('winPercent','Win %'),
            ('Current Streak','Streak'),
            ('Max Streak','Best')
        ]

        for i,(key,label) in enumerate(items):
            col=tk.Frame(statsFrame,bg='#ffffff',padx=self.s(14))
            col.grid(row=0,column=i)
            val=tk.Label(col,text='0',font=('Cascadia Mono',self.s(22),'bold'),
                         bg='#ffffff')
            val.pack()
            tk.Label(col,text=label,font=('Cascadia Mono',self.s(9)),
                     bg='#ffffff',fg='#808080').pack()
            self.statValLabels[key]=val

        self.refreshStats()

    def refreshStats(self):
        winPercent=(int(self.stats['Wins']/self.stats['Played']*100) if self.stats['Played']>0 else 0)

        self.statValLabels['Played'].config(text=str(self.stats['Played']))
        self.statValLabels['winPercent'].config(text=str(winPercent))
        self.statValLabels['Current Streak'].config(text=str(self.stats['Current Streak']))
        self.statValLabels['Max Streak'].config(text=str(self.stats['Max Streak']))

    #--------------------Input-Handling-----------------------#

    def onKey(self,event):
        if self.gameOver:
            return
        key=event.keysym
        if key=='Return':
            self.submitGuess()
        elif key=='BackSpace':
            self.deleteLetter()
        elif key.isalpha() and len(key)==1:
            self.addLetter(key.lower())

    def onKeyButton(self,key):
        if self.gameOver:
            return
        if key=='Enter':
            self.submitGuess()
        elif key=='⌫':
            self.deleteLetter()
        else:
            self.addLetter(key)

    def addLetter(self,letter):
        if len(self.currentGuess)<5:
            col=len(self.currentGuess)
            self.tileLabels[self.currentRow][col].config(text=letter.upper())
            self.tiles[self.currentRow][col].config(
                highlightbackground='#878a8c',highlightthickness=2)
            self.currentGuess.append(letter)

    def deleteLetter(self):
        if self.currentGuess:
            self.currentGuess.pop()
            col=len(self.currentGuess)
            self.tileLabels[self.currentRow][col].config(text='')
            self.tiles[self.currentRow][col].config(
                highlightbackground='#d3d6da',highlightthickness=2)
            
    #------------------Guess-Submission---------------------#

    def submitGuess(self):
        guess=''.join(self.currentGuess)

        if len(guess)!=5:
            self.showMsg('Answer must be 5 letters.')
            return
        if guess in self.priors:
            self.showMsg('Already guessed')
            return
        if guess not in self.words:
            self.showMsg('Not in word list.')
            return
    
        self.priors.add(guess)
        result=checker(guess,self.target)
        self.colorRow(result)
        self.updateKeyboard(result)

        if guess==self.target:
            updatestats(self.stats,True,self.currentRow+1)
            self.refreshStats()
            self.showMsg(winStatements[self.currentRow],permanent=True)
            self.gameOver=True
            return
    
        self.currentRow+=1
        self.currentGuess=[]

        if self.currentRow==6:
            updatestats(self.stats,False,0)
            self.refreshStats()
            self.showMsg(self.target.upper(),permanent=True)
            self.gameOver=True

    def colorRow(self,result):
        for col, (letter,color) in enumerate(result):
            colors=letterColors[color]
            self.tiles[self.currentRow][col].config(
                bg=colors['bg'],highlightbackground=colors['bg'])
            self.tileLabels[self.currentRow][col].config(
                bg=colors['bg'],fg=colors['fg'])
        
    def updateKeyboard(self,result):
        '''
        Priority set for green to change first, then yellow, then grey.
        '''
        priority={'green':3,'yellow':2,'grey':1}
        for letter, color in result:
            if letter in self.keyButtons:
                current=self.keyColors.get(letter,'none')
                if priority.get(color,0)>priority.get(current,0):
                    self.keyColors[letter]=color
                    self.keyButtons[letter].config(
                        bg=letterColors[color]['bg'],
                        fg=letterColors[color]['fg']
                    )

    def showMsg(self,msg,permanent=False):
        self.msgLabel.config(text=msg)
        if not permanent:
            self.root.after(2000,lambda:self.msgLabel.config(text=''))

    def resetGame(self):
        self.target = random.choice(list(self.words))
        self.currentRow = 0
        self.currentGuess = []
        self.priors = set()
        self.gameOver = False
        self.keyColors = {}

        for r in range(6):
            for c in range(5):
                self.tiles[r][c].config(
                    bg='#ffffff', highlightbackground='#d3d6da', highlightthickness=2)
                self.tileLabels[r][c].config(
                    text='', bg='#ffffff', fg='#161617')

        for btn in self.keyButtons.values():
            btn.config(bg='#d3d6da', fg='#161617')

        self.msgLabel.config(text='')

#-----------------------Gui-Player-----------------------------#

def wordleGUI(words):
    root=tk.Tk()
    wordle(root,words,scale=scale)
    root.mainloop()

#------------------------Launcher-----------------------------#

if __name__=='__main__':
    try:
        words=set(open(wordsfile).read().split())
    except FileNotFoundError:
        print(f"'{wordsfile}' not found. Add a valid word list to play.")
        exit(1)

    mode=input ('Play in [t]erminal or [g]ui? ').lower().strip()

    if mode=='t':
        while True:
            wordleTerminal(words)
            again=input('\nPlay again? [y/n]: ').lower().strip()
            if again!='y':
                break
    if mode=='g':
        wordleGUI(words,scale=1.5)






