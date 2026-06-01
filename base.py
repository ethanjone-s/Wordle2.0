
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
            result[i]='blue'
            characters[i]=None

    # Pass Two
    for i in range(5):
        if result[i]=='blue':
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
from tkinter import colorchooser

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
    Main program to run Wordle in local terminal.
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
    'blue':{'bg':'#395296','fg':'#ffffff'},
    'green':{'bg':'#008000','fg':'#ffffff'},
    'yellow':{'bg':'#c9c869','fg':'#ffffff'},
    'grey':{'bg':'#808080','fg':'#ffffff'},
    'empty':{'bg':'#ffffff','fg':'#000000'}
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
    def __init__(self,root,words,scale=1.0):
        self.root=root
        self.root.title('Wordlite')
        self.root.configure(bg='#ffffff')
        self.root.resizable(False,False)

        self.words=words
        self.target=random.choice(list(words))
        self.stats=loadstats()
        self.scale=scale
        self.darkMode=False

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
        tk.Label(header,text='Wordlite',font=('Cascadia Mono',self.s(28),'bold'),
                 bg='#ffffff',fg='#161617').pack()
        self.menu=tk.Button(
            header,text='≡',
            font=('Cascadia Mono',self.s(18)),
            bg='#ffffff',fg='#161617',
            relief='flat',bd=0,
            command=self.showMenu
        )
        self.menu.place(relx=1.0,rely=0.5,anchor='e',x=-self.s(10))
        tk.Frame(self.root,bg='#d3d6da',height=1).pack(fill='x')
        
        # build the tile grid
        gridFrame = tk.Frame(self.root, bg='#ffffff', pady=self.s(20),padx=self.s(80))
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
        #self.buildStats()

        self.playAgainBttn=tk.Button(
            self.root,text='Play Again',
            font=('Cascadia Mono',self.s(11),'bold'),
            bg='#31633d',fg='#ffffff',
            relief='flat',bd=0,
            padx=self.s(20),pady=self.s(8),
            command=self.resetGame
    )
        self.playAgainBttn.pack(pady=self.s(12))
        self.playAgainBttn.pack_forget()     

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
                    font=('Cascadia Mono',self.s(11),'bold'),
                    bg='#d3d6da',fg='#161617',
                    width=8 if wide else 4,
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

    def showMenu(self):
        menu=tk.Menu(self.root,tearoff=0)
        menu.add_command(label='Stats',command=self.showStatsWindow)
        menu.add_command(label='Dark Mode',command=self.toggleDarkMode)
        menu.add_command(label='Tile Colors',command=self.showColorPicker)
        
        x=self.menu.winfo_rootx()
        y=self.menu.winfo_rooty()+self.menu.winfo_height()
        menu.tk_popup(x,y)

    def showStatsWindow(self):
        win=tk.Toplevel(self.root)
        win.title('Stats')
        win.configure(bg='#ffffff')
        win.resizable(False,False)

        winPercent=int(self.stats['Wins']/self.stats['Played']*100 if self.stats['Played'] > 0 else 0)

        # building the highest stats
        statsRow=tk.Frame(win,bg='#ffffff',pady=self.s(10))
        statsRow.pack()
        for i, (label,value) in enumerate([
            ('Played',self.stats['Played']),
            ('Win %',winPercent),
            ('Streak',self.stats['Current Streak']),
            ('Best',self.stats['Max Streak'])
        ]):
            col = tk.Frame(statsRow,bg='#ffffff',padx=self.s(12))
            col.grid(row=0,column=i)
            tk.Label(col,text=str(value),font=('Cascadia Mono',self.s(20),'bold'),
                    bg='#ffffff',fg='#161617').pack()
            tk.Label(col, text=label,font=('Cascadia Mono',self.s(9)),
                    bg='#ffffff',fg='#161617').pack()
            
        tk.Frame(win,bg='#ffffff',height=1).pack(fill='x',pady=self.s(4))

        # user guess distribution
        tk.Label(win,text='Guess Distribution',
                font=('Cascadia Mono',self.s(11),'bold'),
                bg='#ffffff',fg='#161617').pack(pady=(self.s(6),self.s(4)))
        
        distFrame=tk.Frame(win,bg='#ffffff')
        distFrame.pack(padx=self.s(20),pady=self.s(8))

        maxCount=max(self.stats['Guess Distribution'].values()) or 1

        for k in range(1, 7):
            count=self.stats['Guess Distribution'][str(k)]
            bWidth=max(self.s(30),int((count/maxCount)*self.s(200)))
            bColor='#566eb0' if count==maxCount else '#8fe089'

            row=tk.Frame(distFrame,bg='#ffffff')
            row.pack(fill='x',pady=self.s(2))

            tk.Label(row,text=str(k),font=('Cascadia Mono',self.s(10)),
                bg='#ffffff',fg='#161617',width=2,anchor='e').pack(side='left',padx=(0,self.s(6)))

            bar=tk.Frame(row,bg=bColor,height=self.s(24),width=bWidth)
            bar.pack_propagate(False)
            bar.pack(side='left')

            tk.Label(bar,text=str(count),font=('Cascadia Mono',self.s(9),'bold'),
                bg=bColor,fg='#161617').pack(side='right',padx=self.s(6),expand=True)

    def toggleDarkMode(self):
        self.darkMode=not self.darkMode
        bg='#212121' if self.darkMode else '#ffffff'
        fg='#e3e3e3' if self.darkMode else '#161617'
        kbBg='#818384' if self.darkMode else '#d3d6da'
        greyKb = '#404040' if self.darkMode else '#808080'
        
        letterColors['empty']['bg']=bg
        letterColors['empty']['fg']=fg
        letterColors['grey']['bg']=greyKb

        def recolor(widget):
            try:
                if widget.cget('bg') in ('#ffffff','#212121'):
                    widget.config(bg=bg)
                elif widget.cget('bg') in ('#d3d6da','#818384'):
                    widget.config(bg=kbBg)
            except tk.TclError:
                pass
            try:
                if widget.cget('fg') in ('#161617','#c2c2c2'):
                    widget.config(fg=fg)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                recolor(child)
        
        recolor(self.root)

        for letter,color in self.keyColors.items():
            if color=='grey'and letter in self.keyButtons:
                self.keyButtons[letter].config(bg=greyKb)

    def showColorPicker(self):
        win=tk.Toplevel(self.root)
        win.configure(bg='#ffffff')
        win.resizable(False,False)

        #tk.Label(win,text='',
        #        font=('Cascadia Mono', self.s(14), 'bold'),
        #        bg='#ffffff').pack(pady=(self.s(10), self.s(6)))
        frame=tk.Frame(win,bg='#ffffff')
        frame.pack(padx=self.s(20),pady=self.s(10))

        for i,(name,key) in enumerate([
            ('Correct','blue'),
            ('Misplaced','yellow'),
            ('Incorrect','grey')
        ]):
            tk.Label(frame,text=name,font=('Cascadia Mono',self.s(10)),
                bg='#ffffff',fg='#161617',width=10,anchor='w').grid(row=i,column=0,pady=self.s(6))
            preview=tk.Frame(frame,bg=letterColors[key]['bg'],
                            width=self.s(32), height=self.s(32))
            preview.grid(row=i,column=1,padx=self.s(10))
            preview.grid_propagate(False)
            tk.Button(frame,text='Change',font=('Cascadia Mono',self.s(9)),
                    relief='flat',bg='#d3d6da',fg='#161617',
                    command=lambda k=key,p=preview:self.changeColor(k,p)
                    ).grid(row=i,column=2,padx=self.s(6)) 

    def changeColor(self,colorKey,preview):
        result=colorchooser.askcolor(
            color=letterColors[colorKey]['bg'],
            title=f'Choose color for {colorKey} tiles.'
        )
        if result[1]:
            letterColors[colorKey]['bg']=result[1]
            preview.config(bg=result[1])

            for letter,color in self.keyColors.items():
                if color==colorKey and letter in self.keyButtons:
                    self.keyButtons[letter].config(bg=result[1])

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
            self.showMsg(winStatements[self.currentRow],permanent=True)
            self.gameOver=True
            self.playAgainBttn.pack(pady=self.s(12))
            return
    
        self.currentRow+=1
        self.currentGuess=[]

        if self.currentRow==6:
            updatestats(self.stats,False,0)
            self.showMsg(self.target.upper(),permanent=True)
            self.gameOver=True
            self.playAgainBttn.pack(pady=self.s(12))

    def colorRow(self,result):
        for col, (letter,color) in enumerate(result):
            colors=letterColors[color]
            self.tiles[self.currentRow][col].config(
                bg=colors['bg'],highlightbackground=colors['bg'])
            self.tileLabels[self.currentRow][col].config(
                bg=colors['bg'],fg=colors['fg'])
        
    def updateKeyboard(self,result):
        '''
        Priority set for blue to change first, then yellow, then grey.
        '''
        priority={'blue':3,'yellow':2,'grey':1}
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
        self.playAgainBttn.pack_forget()
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

def wordleGUI(words,scale=1.0):
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
        wordleGUI(words,scale=1.35)






