from selenium import webdriver
from colors import Color as c
from time import sleep
from copy import deepcopy
#import msvcrt  #windows
import getch    #linux
import os

#initalize the webdriver
web = webdriver.Chrome('C:/chromedriver')



#setup the list for keeping track on sales as well as the different elements
cookies = '/html/body/mh-app/mh-modal/div/div/div[2]/div/mathem-cookie-consent-modal/form/div[2]/div/div[1]/button/span'
addware = '//*[@id="content-main"]/mh-product-detail-page/div/div[1]/div[1]/mh-product-detail/mathem-product-details/mathem-ui-floater/mathem-ui-product-quantity/div[1]/button/span'
addmorewares = '//*[@id="content-main"]/mh-product-detail-page/div/div[1]/div[1]/mh-product-detail/mathem-product-details/mathem-ui-floater/mathem-ui-product-quantity/div[2]/button[2]/span'
waresale = '//*[@id="content-main"]/mh-product-detail-page/div/div[1]/div[1]/mh-product-detail/mathem-product-details/mh-product-splash'
removeware = '//*[@id="content-main"]/mh-product-detail-page/div/div[1]/div[1]/mh-product-detail/mathem-product-details/mathem-ui-floater/mathem-ui-product-quantity/div[2]/button[1]/span'
sales = []

#class for keeping track on sales, the price and ammount as well as if they should buy the sale or not
class Sale: 
    def __init__(self, warenumber, name, ammount, price) -> None:
        self.warenumber = warenumber
        self.name = name
        self.ammount = ammount
        self.price = price
        self.buy = False

#class for displaying the results of a shopping session
class ShopResult:
    def __init__(self, warename, errormsg):
        self.warename = warename
        self.errormsg = errormsg

def ShowSales(shoppinglist):
    for i in range(len(sales)):
        print(f"Varans nummer: {sales[i].warenumber}, varans namn: {shoppinglist[sales[i].warenumber].name}, {sales[i].ammount} för {sales[i].price}kr")
    input("burh")


#method for finding sales
def LookForSales(shoppinglist, referenceindex):
    #clears the sales list in order to avoid getting double the content if the method is called twice
    sales.clear()
    #goes into mathem and clicks on cookies
    web.get('https://www.mathem.se/')
    sleep(5)
    try:
        button = web.find_element_by_xpath(cookies)
        button.click()
    except:
        pass
    #finding the correct url
    for i in range(len(shoppinglist)):
        url = ''
        sale = ""
        foundurl = False
        for index in range(len(referenceindex)):

            for reference in range(len(referenceindex[index].references)):
                
                if referenceindex[index].references[reference] == shoppinglist[i].name:
                    url = referenceindex[index].url
                    foundurl = True
        
        if not foundurl:
            print("Kunde inte hitta vara")

        else:   #goes to the url, if it finds a sale it will check for the letters "för" which means that there is a special price x for y kr
            web.get(url)    #this will also make it so that the first click will automatically buy that ammount, therefore the ammount is logged in
            sleep(2)    #order to be able to go back x - 1 steps in order to not buy too many of it
            print(shoppinglist[i].name)
            try:
                sale = web.find_element_by_xpath(waresale).text
                if not len(sale):
                    print("Ingen rabatt hittad")
                    continue
                foundsale = False
                for l in range(len(sale)):
                    #print(sale[l])
                    if sale[l] == 'f':
                        if sale[l + 1] == 'ö' and sale[l + 2] == 'r':
                            #print(f"{sale[l]}{sale[l + 1]}{sale[l + 2]}")
                            pricestr = ""
                            for num in range(l + 3, len(sale) - 2):
                                pricestr += sale[num]

                            price = int(pricestr)
                            sales.append(Sale(i, shoppinglist[i].name, int(sale[l - 2]), price))
                            print("Hittade rabatt!")
                            foundsale = True
                            break
                if not foundsale:
                    print("rabatt hittad, inte x för y")

            except:
                print("Ingen rabatt hittad")
    Clear()

    #ShowSales(shoppinglist)
    """for i in range(len(sales)):
        print(f"Varans nummer: {sales[i].warenumber}, varans namn: {shoppinglist[sales[i].warenumber].name}, {sales[i].ammount} för {sales[i].price}kr")"""

def ChooseSalesUX(selectedoptiontV, selectedoptiontH, saleslen):
    print(c.black)
    #pressedkey = str(msvcrt.getch())   #windows
    pressedkey = str(getch.getch())
    print(c.default)
    
    match(pressedkey):
            #button w and uparrow
            #case "b'w'" | "b'H'":  #windows
            case "w" | "A":     #linux
                if selectedoptiontV <= 0:
                    selectedoptiontV = saleslen
 
                else:
                    selectedoptiontV -= 1
            #button s and downarrow
            #case "b's'" | "b'P'":   #windows
            case "s" | "B":     #linux
 
                if selectedoptiontV >= saleslen:
                    selectedoptionV = 0
                else:
                    selectedoptiontV += 1
            
            #d, rightarrow, a, leftarrow
            #case "b'a'" | "b'd'" | "b'K'" | "b'M'": #windows
            case "d" | "C" | "a" | "D": #linux
                if selectedoptiontH == 1:
                    selectedoptiontH = 0
                else:
                    selectedoptiontH = 1
            #button enter
            #case "b'\\r'":  #windows
            case "\n":  #linux
                if selectedoptiontV < saleslen:
                    sales[selectedoptiontV].buy = selectedoptiontH
                else:
                    selectedoptiontH = 2
            #button q
            #case "b'q'":
    Clear()
    return  selectedoptiontV, selectedoptiontH

#similar to the different menus shown before, but with a yes/no format that you can select from left to right
def ChooseSales():
    #vertical (V) and horizontal (H)
    selectedoptionV = 0
    selectedoptionH = 0

    biggestsale = 0
    for i in range(len(sales)):
        if len(f"{sales[i].name}, {sales[i].ammount} för {sales[i].price}kr") > biggestsale:
            biggestsale = len(f"{sales[i].name}, {sales[i].ammount} för {sales[i].price}kr")
    biggestsale += 5
    loop = True

    while loop:
        if biggestsale > 5:
            print("Rabatter hittade:" + " " * (biggestsale - 11) + "köp?\n")
        else:
            print("Rabatter hittade: Inga")


        for i in range(len(sales)):
            salesinfo = f"{sales[i].name}, {sales[i].ammount} för {sales[i].price}kr"
            print(salesinfo + " " * (biggestsale - len(salesinfo)), end="")
            #checks the different cases, if selected and active, change background and text, if only selected, change background and if only active change text
            if (selectedoptionV == i and selectedoptionH == 1 and sales[i].buy):
                print(c.selectedgreen, end="")
            elif sales[i].buy:
                print(c.green, end="")
            elif selectedoptionV == i and selectedoptionH == 1:
                print(c.selected, end="")
            print("Ja" + c.default + " " * 5, end="")

            #same as above
            if (selectedoptionV == i and selectedoptionH == 0 and not sales[i].buy):
                print(c.selectedred, end="")
            elif not sales[i].buy:
                print(c.error, end="")
            elif selectedoptionV == i and selectedoptionH == 0:
                print(c.selected, end="")
            print("Nej" + c.default)

        print(" " * (biggestsale - 3), end="")
        if selectedoptionV == len(sales):
            print(c.selected, end="")
        print("Fortsätt till köp" + c.default)
        selectedoptionV, selectedoptionH = ChooseSalesUX(selectedoptionV, selectedoptionH, len(sales))

        if selectedoptionH == 2:
            loop = False

#method for buying wares
def BuyWares(realshoppinglist, referenceindex):
    shoppinglist = deepcopy(realshoppinglist) #used to make sure no changes are made to the real shoppinglist
    shopresults = [] #used for displaying the results of the shopping
    foundAllSales = False   #used for checking if all x for y sales have been found, in that case stops checking for sales
    currentSaleCheck = 0    #keeps check on what sale from the sales list is next
    if currentSaleCheck == len(sales):  foundAllSales = True    #checks if the sales list is empty or not
    web.get('https://www.mathem.se/')
    input("Tryck på enter när du har loggat in")
    for i in range(len(shoppinglist)):
        print(shoppinglist[i].ammount)
        url = ''
        sale = ""
        foundurl = False
        for index in range(2, len(referenceindex)):

            for reference in range(1, len(referenceindex[index].references)):
                
                if referenceindex[index].references[reference] == shoppinglist[i].name:
                    url = referenceindex[index].url
                    foundurl = True
        
        if not foundurl:
            print("Kunde inte hitta vara")
            shopresults.append(ShopResult(f"{c.error}{shoppinglist[i].name}{c.default}", "Kunde inte hitta varan i databasen"))

        else:
            web.get(url)
            sleep(2)

            try:    #since the program wouldnt stop even if the button was not pressed, I had to check if you could remove a ware instead
                button = web.find_element_by_xpath(addware)
                button.click()
                
                sleep(1)
                button = web.find_element_by_xpath(removeware)
                button.click()
                
                sleep(1)
                try:    #if there is a special sale, addware would not work since the bought ammount would not be 0
                    button = web.find_element_by_xpath(addware)
                    button.click()
                    #########add this code if you buy too many wares###########
                    button = web.find_element_by_xpath(removeware)
                    button.click()
                     
                    ############################################################
                except:
                    button = web.find_element_by_xpath(addmorewares)
                    button.click()
                    


            except:
                print("Kunde inte lägga varan i kundvagnen")
                shopresults.append(ShopResult(f"{c.error}{shoppinglist[i].name}{c.default}", "Varan kunde inte läggas i kundvagnen"))
                continue
            
            if not foundAllSales:
                if i == sales[currentSaleCheck].warenumber: #checks if there is a sale on the current ware
                    
                    if sales[currentSaleCheck].buy: #checks if you want to buy the sales
                        
                        if shoppinglist[i].ammount <= sales[currentSaleCheck].ammount:   #checks if the ammount specified in the list is smaller or equal of the sale
                            shoppinglist[i].ammount = 1 #in that case you only want to press buy once, as it automatically adds that ammount to the shoppinglist
                        else:   #if the ammount you want to buy is larger than the special price
                            shoppinglist[i].ammount -= (sales[currentSaleCheck].ammount - 1)  #subtracts the ammount that the special price bougth, for example if you want to buy 3 and
                            #there are 2 for x kr, you will first buy the initial 2, and then you will want to buy a third one, since you already bought the first one in the code you will subtract 1 less

                    else:   #if you dont want to buy the sale
                        shoppinglist[i].ammount -= (sales[currentSaleCheck].ammount)    #subtracts the ammount you want to buy with the ammount you buy with the first click
                        if shoppinglist[i].ammount == 1: shoppinglist[i].ammount += 1
                    currentSaleCheck += 1
                    if currentSaleCheck == len(sales):  foundAllSales = True    #sets foundallsales to True if all sales have been found to avoid trying to get non existing lists

            print(shoppinglist[i].ammount)


            if shoppinglist[i].ammount > 1:
                button = web.find_element_by_xpath(addmorewares)
                sleep(1)
                for m in range(1, shoppinglist[i].ammount):

                    try:
                        button.click()
                        
                        sleep(0.1)
                    except:

                        print(f"Kunde bara lägga i {m} utav {shoppinglist[m].ammount} varor i kundvagnen")
                        shopresults.append(ShopResult(f"{c.error}{shoppinglist[m].name}{c.default}", f"Kunde endast lägga i {m} utav {shoppinglist[m].ammount} i kundvagnen"))
                        break

            elif shoppinglist[i].ammount < 0:
                button = web.find_element_by_xpath(removeware)
                sleep(1)
                for m in range(-shoppinglist[i].ammount):
                    button.click()
                    
                    sleep(0.1)
        sleep(1)
        if len(shopresults) - 1 < i: #checks that the current ware has not been added prior to this, then adds it with green to show that buying the ware was a success
            print("Köp lyckades")
            shopresults.append(ShopResult(f"{c.green}{shoppinglist[i].name}{c.default}", ""))
    ShowShoppingResults(shopresults)
            


def ShowShoppingResults(shopresults):
    
    for i in range(len(shopresults)):
        print(f"{shopresults[i].warename}     {shopresults[i].errormsg}")

    input("Tryck på enter för att gå tillbaka till huvudmenyn")

Clear = lambda: os.system('cls')
    
