#from ctypes import set_last_error
#
import msvcrt  #windows
#import getch    #linux
import os
import sys
import socket
import pickle
import webscraper as w
from colors import Color as c
from wares import Ware
from references import WareReference
from time import sleep

#defines connection data and parameters
HEADER = 64
PORT = 
FORMAT = 'utf-8'
DISCONNECT_MSG = "disconnect"
SERVER = ''
ADDR = (SERVER, PORT)   

#sets up the connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#method to recieve all data
def GetData(shoppinglist, referenceindex):

    #clears prevoius lists
    shoppinglist.clear()
    referenceindex.clear()

    #send the command to start the process of sending data
    client.send("GetData".encode(FORMAT))
    
    #first gets the length of the data, and then the actual data
    recvshoplistlen = int(client.recv(HEADER).decode(FORMAT))
    
    recvshoplist = b''
    while len(recvshoplist) < recvshoplistlen:
        temprecvshoplist = client.recv(recvshoplistlen)
        recvshoplist += temprecvshoplist

    recvrefindexlen = int(client.recv(HEADER).decode(FORMAT))
    
    recvrefindex = b''

    while len(recvrefindex) < recvrefindexlen:  #makes sure you get the entire list, in an attempt to make the application more future proof
        temprecvrefindex = client.recv(recvrefindexlen)
        recvrefindex += temprecvrefindex

    #unpickles data and puts it into the correct list
    shoppinglist = pickle.loads(recvshoplist)
    referenceindex = pickle.loads(recvrefindex)

    #used for testing
    """if not len(referenceindex): print("Referenceindex was empty")
    for i in range(len(referenceindex)):
        print(f"Name: {referenceindex[i].name}, url: {referenceindex[i].url}, ammount of references: {len(referenceindex[i].references)}")"""
    print("Data mottagen!")


    return shoppinglist, referenceindex

#method to update the database at the server computer
def SendData(referenceindex):

    #pickles the data and gets its length
    pickledData = pickle.dumps(referenceindex)
    pickledDataLen = len(pickledData)

    #first sends a message to tell the server that you want to update the data
    senddatamsg = "SendData".encode(FORMAT)
    senddatamsg += b' ' * (HEADER - len(senddatamsg))
    client.send(senddatamsg)

    #get conformation msg of recieving the data length
    
    #sends the length of the data
    pickledDatalen = str(pickledDataLen).encode(FORMAT)
    pickledDatalenB = pickledDatalen + b' ' * (HEADER - len(pickledDatalen))
    print(pickledDatalenB)
    client.send(pickledDatalenB)
    
    #waits for conformation msg
    #print(client.recv(HEADER).decode(FORMAT))

    #sends actual data
    client.send(pickledData)

    #prints out conformation message
    print(client.recv(HEADER).decode(FORMAT))

#method for adding a new WareReference
def AddWareReference(referenceindex):
    name = ""
    url = ""
    #does a while loop until you put something into name and url, then appends
    loop = True
    while loop:
        name = input("Skriv in namnet på den nya varan: ")
        if len(name) == 0:
            print(c.error + "ERROR!" + c.default + " namn måste innehålla minst en bokstav, var vänlig försök igen")
        else: loop = False
    loop = True
    while loop:
        url = input("Skriv in url till varan: ")
        
        if len(name) == 0:
            print(c.error + "ERROR!" + c.default + " url måste innehålla minst en bokstav, var vänlig försök igen")
        else: loop = False 
    referenceindex.append(WareReference(name, url))
    print("Vara tillagd, går tillbaka till föregående meny...")
    sleep(1)
    Clear()

#method for removing a WareReference
def RemoveWareReference(referenceindex):
    if len(referenceindex) <= 2:
        print("Inga referenser tillgängliga, återvänder till föregående meny...")
        sleep(1)
        Clear()

    else:
        refindexnames = []
        for i in range(2, len(referenceindex)):
            refindexnames.append(referenceindex[i].name)

        selectedcontent = 0
        action = -2
        loop = True
        title = "Välj en vara att ta bort"
        while loop:
            menuUI(title, refindexnames, selectedcontent)

            action, selectedcontent = menuUX(len(refindexnames), selectedcontent)

            if action == -2:
                continue

            elif action == -1:
                loop = False
                return -1

            else:
                prevRefIndLen = len(referenceindex)
                RemoveSelectedWareReference(referenceindex, selectedcontent + 2)   #the method works with removing from the referenceindex as well
                if prevRefIndLen != len(referenceindex):
                    return selectedcontent + 2


#very similar to RemoveReference, but changed to work with WareReferences instead
def RemoveSelectedWareReference(referenceindex, selectedcontent):
    title = f"Är du säker på att du vill ta bort {referenceindex[selectedcontent].name}?"
    action = -2
    loop = True
    selectedoption = 0
    while loop:
        menuUI(title, ["Ja", "Nej"], selectedoption)
        action, selectedoption = menuUX(2, selectedoption)
        
        if action == -2:
            continue

        elif action == -1 or action == 1:
            loop = False
        
        else:
            referenceindex.pop(selectedcontent)
            print("Vara borttagen, återvänder till föregående meny...")
            sleep(1)
            loop = False
            Clear()


#method for adding a new reference to one of the existing "WareReference"
def AddReference(references):
    loop = True
    while loop:
        newreference = input("Skriv in den nya referensen: ")
        if len(newreference) == 0:
            print(c.error + "ERROR!" + c.default + " nya referensen måste innehålla minst en bokstav, var vänlig försök igen")
        else:   break
    references.append(newreference)
    print("Referens tillagd! återvänder till föregående meny...")
    sleep(1)
    Clear()

def EditURL(selectedRefIndex):
    loop = True
    while loop:
        editedurl = input("Skriv in en ny URL: ")
        if len(editedurl) == 0:
            print(c.error + "ERROR!" + c.default + " url måste innehålla minst en bokstav, var vänlig försök igen")
            
        else:   break
    selectedRefIndex.url = editedurl
    selectedRefIndex.references[1] = editedurl
    print("URL updaterad, går tillbaka till föregående meny...")
    sleep(1)
    Clear()

#changes the reference to the user input
def EditReferences(references, selectedreference):
    loop = True
    while loop:
        editedreference = input("Skriv in det nya namnet på referensen: ")
        if len(editedreference) == 0:
            print(c.error + "ERROR!" + c.default + " referens måste innehålla minst en bokstav, var vänlig försök igen")
            
        else:   break
    references[selectedreference] = editedreference
    print("Referens updaterad, går tillbaka till föregående meny...")
    sleep(1)
    Clear()

#method for removing references  
def RemoveReferences(references, selectedreference):
    title = f"Är du säker på att du vill ta bort {references[selectedreference]}?"
    action = -2
    loop = True
    selectedoption = 0
    while loop:
        menuUI(title, ["Ja", "Nej"], selectedoption)
        action, selectedoption = menuUX(2, selectedoption)
        
        if action == -2:
            continue

        elif action == -1 or action == 1:
            loop = False
        
        else:
            references.pop(selectedreference)
            print("Referens borttagen, återvänder till föregående meny...")
            sleep(1)
            loop = False
            Clear()




#method for being able to navigate the different menus
def menuUX(optionslen, selectedcontent):
    #action is used when selecting a option, -2 does nothing, -1 will close the menu and everything above will activate a specified method 
    action = -2
    print(c.black)
    pressedkey = str(msvcrt.getch())   #windows
    #pressedkey = getch.getch()  #linux
    print(c.default)
    
    match(pressedkey):
            #button w and uparrow
            case "b'w'" | "b'H'":  #windows
            #case "w" | "A":     #linux
                if selectedcontent <= 0:
                    selectedcontent = optionslen - 1
 
                else:
                    selectedcontent -= 1
            #button s and downarrow
            case "b's'" | "b'P'":   #windows
            #case "s" | "B":     #linux
 
                if selectedcontent >= optionslen - 1:
                    selectedcontent = 0
                else:
                    selectedcontent += 1
            #button enter, d and rightarrow
            case "b'\\r'" | "b'd'" | "b'M'":   #windows
            #case "\n" | "d" | "C":  #linux
                action = selectedcontent
            #button q, a and leftarrow
            case "b'q'" | "b'a'" | "b'K'":  #windows
            #case "q" | "a" | "D":   #linux
                action = -1
    
    Clear()
    return action, selectedcontent


#method for printing out the title, all of the content as well as coloring the selected content differently
def menuUI(title, content, selectedcontent):
        print(title)
        print()
        for i in range(len(content)):

            if selectedcontent == i:
                print(c.selected, end="")

            print(content[i] + c.default)


#similar to menuUI but changed to work for the reference index list
#prevcontent is the content previously chosen, contentoptionsspacing is the space in between the current content and the content inside the currently selected content
#contentoptions is the content inside the currently selected content, for example if you have references selected the contentoptions will be all of the references
def RefIndexUI(title, content, prevcontent, contentoptionsspacing, contentoptions, selectedcontent, prevfirstItem, prevlastItem):

    print(f"current item: {selectedcontent}")

    #start and stop values for the displayed items
    
    if len(content) < 15:
        firstItem = 1
        lastItem = len(content) - 1

    else:
        if selectedcontent <= 1:
            firstItem = 1
            lastItem = 16

        elif selectedcontent == len(content) - 1:
            firstItem = len(content) - 16
            lastItem = len(content) - 1

        else:
            if selectedcontent > prevlastItem:
                firstItem = selectedcontent - 15
                lastItem = selectedcontent

            elif selectedcontent < prevfirstItem:
                firstItem = selectedcontent
                lastItem = selectedcontent + 15
            
            else:
                firstItem = prevfirstItem
                lastItem = prevlastItem
    print(f"first item: {firstItem}, last item: {lastItem}")

    print(title)
    print()
    print(prevcontent, end="")     #prints the previous content
    if firstItem == 1:
        if selectedcontent == 0:

            print(c.selected, end="")   #if the first content is selected

        print(content[0] + c.default, end="")
        print(" " * (contentoptionsspacing - len(content[0])) + contentoptions[0])    #also prints the options avalible (either edit/remove or )

    for i in range(firstItem, lastItem + 1):
        #blank spaces for additional options
        print(" " * len(prevcontent), end="")

        if selectedcontent == i:
            print(c.selected, end="")
        #if there are contentoptions left
        if len(contentoptions) > i:

            print(content[i] + c.default + " " * (contentoptionsspacing - len(content[i])) + contentoptions[i])

        else:
            print(content[i] + c.default)
    #continues to print the contentoptions if they exceed the ammount of content
    if len(contentoptions) > len(content):
        for i in range(len(content), len(contentoptions)):
            print(" " * (len(prevcontent) + contentoptionsspacing) + contentoptions[i])
    return firstItem, lastItem

#method for looking at the shopping list
def ShoppingListMenu(title, content):
    
    action = -2
    selectedcontent = 0
    loop = True
    
    #adds the option to go back at the top of the list 
    
    contentdisp = ["Gå tillbaka"]
    biggestname = 0

    #gets the longest name in the content
    for i in range(len(content)):
        if len(content[i].name) > biggestname:
            biggestname = len(content[i].name)

    biggestname += 5
    #appends all the content data into a list with the appropiate spacing between name and ammount
    for i in range(len(content)):
        newcontentdisp = content[i].name + " " * (biggestname - len(content[i].name)) + str(content[i].ammount)
        contentdisp.append(newcontentdisp)
    #also adds more info about the content within the title
    title += "\nNamn" + " " * (biggestname - 6) + "Antal"
    while loop:
        menuUI(title, contentdisp, selectedcontent)

        action, selectedcontent = menuUX(len(contentdisp), selectedcontent)

        if action == -1 or action == 0:
            loop = False
        
#method for referenceindex menu
def ReferenceIndexMenu(referenceindex):
    selectedcontent = 0
    action = -2
    firstItem = 1
    lastItem = 10
    title = "Referens databas"
    loop = True
    biggestcontent = 0
    refindexnames = []
    #gets the biggest name in the referenceindex
    #also appends all names into a list for the RefIndexUI method
    for i in range(len(referenceindex)):
        refindexnames.append(referenceindex[i].name)
        if len(referenceindex[i].name) > biggestcontent:
            biggestcontent = len(referenceindex[i].name)
    biggestcontent += 5

    while loop:
        firstItem, lastItem = RefIndexUI(title, refindexnames, "", biggestcontent, referenceindex[selectedcontent].references, selectedcontent, firstItem, lastItem)
        action, selectedcontent = menuUX(len(referenceindex), selectedcontent)

        if action == -2:
            pass
        
        elif action == -1:
            loop = False
        
        elif action == 0:
            AddWareReference(referenceindex)
            refindexnames.append(referenceindex[-1].name)
        
        elif action == 1:
            RefIndPop = RemoveWareReference(referenceindex)
            if RefIndPop > 0:
                refindexnames.pop(RefIndPop)

        else:
            prevcontent = refindexnames[selectedcontent] + " " * (biggestcontent - len(refindexnames[selectedcontent]))
            ReferenceIndexReferencesMenu(prevcontent, referenceindex[selectedcontent].references, referenceindex[selectedcontent])

#method when you have selected a specific Reference
def ReferenceIndexReferencesMenu(prevcontent, references, referenceindex):
    selectedcontent = 0
    action = -2
    firstItem = 1
    lastItem = 10
    title = "Referens databas"
    loop = True
    biggestreference = 0
    #referencesnames = []
    for i in range(len(references)):
        #referencesnames.append(references[i])
        if len(references[i]) > biggestreference:
            biggestreference = len(references[i])
    biggestreference += 5
    while loop:
        #prevcontent
        firstItem, lastItem = RefIndexUI(title, references, "", biggestreference, ["Ändra", "Ta bort"], selectedcontent, firstItem, lastItem)
        action, selectedcontent = menuUX(len(references), selectedcontent)
        
        if action == -2:
            pass

        elif action == -1:
            loop = False

        elif action == 0:
            AddReference(references)

        else:
            prevcontent = references[selectedcontent] + " " * (biggestreference - len(references[selectedcontent]))
            ReferenceIndexReferencesOptionsMenu(prevcontent, ["Ändra", "Ta bort"], references, selectedcontent, referenceindex)
            if len(references) - 1 < selectedcontent:
                selectedcontent = len(references) - 1
            

#method for editing and/or deleting references
def ReferenceIndexReferencesOptionsMenu(prevcontent, options, references, currentreference, referenceindex):
    action = -2
    selectedcontent = 0
    firstItem = 1
    lastItem = 10
    title = "Referens databas"
    loop = True
    while loop:
        #sending in a "" for the options since there is atleast 1 option required
        firstItem, lastItem = RefIndexUI(title, options, prevcontent, 0, [""], selectedcontent, firstItem, lastItem)
        action, selectedcontent = menuUX(len(options), selectedcontent)
        if action == -2:
            pass
        
        elif action == -1:
            loop = False
        
        elif action == 0:
            if currentreference == 1:
                EditURL(referenceindex)
            else:
                EditReferences(references, currentreference)
            break 
        else:
            if currentreference == 1:
                print(c.error + "ERROR!" + c.default + " kan inte ta bort url")
                continue
            RemoveReferences(references, currentreference)
            break

#method used for handling data, anything from viewing the data to adding, editing or removing data
def HandleData(referenceindex, shoppinglist):
    title = "Välj en databas"
    selectedcontent = 0
    action = -2
    loop = True
    while loop:
        menuUI(title, ["Referens databas", "Inköpslista"], selectedcontent)
        action, selectedcontent = menuUX(2, selectedcontent)

        if action == -2:
            continue

        elif action == -1:
            loop = False
        
        elif action == 0:
            ReferenceIndexMenu(referenceindex)

        else:
            ShoppingListMenu("Inköpslista", shoppinglist)


#method used for either getting an updated list from the database or updating the database with your new changes
def UpdateData(referenceindex, shoppinglist):
    action = -2
    selectedcontent = 0
    loop = True
    title = "Välj vad du vill göra med datan"
    while loop:
        menuUI(title, ["Hämta data", "Skicka data"], selectedcontent)

        action, selectedcontent = menuUX(2, selectedcontent)

        if action == -2:
            continue

        elif action == -1:
            return shoppinglist, referenceindex

        elif action == 0:
            pass
            shoppinglist, referenceindex = GetData(shoppinglist, referenceindex)

        else:
            SendData(referenceindex)
            pass

#method for main menu
def mainmenu(title, content, shoppinglist, referenceindex):
    action = -2
    selectedcontent = 0    #starting position of the menu selector
    loop = True
    while loop:
        
        #prints out the menu content 
        menuUI(title, content, selectedcontent)

        #gets action taken
        action, selectedcontent = menuUX(len(content), selectedcontent)
        #presents the different options
        if action == -2:
            continue

        elif action == -1:
            loop = False

        elif action == 0:
            w.LookForSales(shoppinglist, referenceindex)
            w.ChooseSales()
            w.BuyWares(shoppinglist, referenceindex)
        
        elif action == 1:
            HandleData(referenceindex, shoppinglist)

        elif action == 2:
            shoppinglist, referenceindex = UpdateData(referenceindex, shoppinglist)

        elif action == 3:
            loop = False



Clear = lambda: os.system('cls')

#used for testing
def CheckData(referenceindex):
    for i in range(len(referenceindex)):
        print(f"name: {referenceindex[i].name}, url: {referenceindex[i].url}")



def main():
    #sets up the lists that will be shopping list and the url required
    shoppinglist = []
    referenceindex = []
    shoppinglist, referenceindex = GetData(shoppinglist, referenceindex)
    
    #used for testing the management of databases
    """shoppinglist.append(Ware("julmust", 2))
    shoppinglist.append(Ware("sill", 3))
    shoppinglist.append(Ware("laxrom", 4))
    shoppinglist.append(Ware("lindt", 1))
    shoppinglist.append(Ware("https://www.mathem.se/varor/apelsin/apelsin-klass1", 4))
    referenceindex.append(WareReference("Lägg till ny vara", ""))
    referenceindex.append(WareReference("Ta bort vara", ""))
    referenceindex[0].references.clear()
    referenceindex[0].references.append("")
    referenceindex[1].references.clear()
    referenceindex[1].references.append("")
    referenceindex.append(WareReference("julmust", "https://www.mathem.se/varor/julmust/apotekarnes-julmust-light-4x140cl"))
    referenceindex.append(WareReference("sill", "https://www.mathem.se/varor/sill-ovriga-sorter/lingon-o-enbarssill-280ml-erssons"))
    referenceindex.append(WareReference("laxrom", "https://www.mathem.se/varor/laxrom/regnbagslaxrom-fryst-80g-fiskeriet"))
    referenceindex.append(WareReference("lindt", "https://www.mathem.se/varor/chokladkaka-mork/choklad-70--100g-lindt-excellence"))
    referenceindex.append(WareReference("vara 5", "https://www.mathem.se/varor/apelsin/apelsin-klass1"))"""


    Clear()
    title = "Välkommen till mathem autobuyer 1.0!"
    content = ["Börja handla", "Hantera databaser", "Updatera databaser", "Avsluta"]
    mainmenu(title, content, shoppinglist, referenceindex)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Ett fel uppstod, programmet avslutades")
        print(e)
    finally:
        
        client.send(DISCONNECT_MSG.encode(FORMAT))