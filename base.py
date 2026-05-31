
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

winStatements=[
    'Cheater.','Not bad I guess.','Great.','Satisfactory.','Close one.','Balright.'
]

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

#------------------------Terminal-PLayer-----------------------#

from colorama import Fore,Back,Style,init

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

#------------------------GUI-PLayer---------------------------#



#------------------------Launcher-----------------------------#

if __name__=='__main__':
    try:
        words=set(open(wordsfile).read().split())
    except FileNotFoundError:
        print(f"'{wordsfile}' not found. Add a valid word list to play.")
        exit(1)

    mode=input ('Play in [t]erminal or [g]ui?. ').lower().strip()

    if mode=='t':
        while True:
            wordleTerminal(words)
            again=input('\nPlay again? [y/n]: ').lower().strip()
            if again!='y':
                break
    #if mode=='g':
    #    wordleGUI(words)
    #else:
    #    break






