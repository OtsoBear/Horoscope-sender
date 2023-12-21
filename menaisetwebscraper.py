import requests
import os

#Palauttaa päivän horoskooppisivun url osotteen
def pageGetter():
    sivu = requests.get("https://www.is.fi/menaiset/horoskooppi/").text.split("menaiset/horoskooppi/art-")
    sivu[2].split("menaiset/horoskooppi/art-")
    urlmysteeri = sivu[2].split('"')[0]
    url = "https://www.is.fi/menaiset/horoskooppi/art-" + urlmysteeri
    return url



#Parser syö URL osotteen päivän horoskooppeihin ja palauttaa listan, jossa on horoskoopit ja niiden ennustukset, muodossa: HOROSKOOPPI \r\n ennuste (ilman väliä ennen tai jälkeen \r\n
def parser(URL):
    pageList = requests.get(URL).text.split('class="article-body margin-bottom-24 padding-x-16"><span>')
    ennustusLista = []
    horoskoopit = ["JOUSIMIES","KAURIS","VESIMIES","KALAT","OINAS","HÄRKÄ","KAKSONEN","RAPU","LEIJONA","NEITSYT", "VAAKA", "SKORPIONI"] #Horoskoopit on aina samassa järjestyksessä sivulla, joten ne on hardcodattu listaan oikeaan järjestykseen koska oon laiska
    del pageList[0]
    for i in range(0,11):
        ennustusLista.append(horoskoopit[i] +os.linesep + pageList[i].split("</span>")[0])
    return ennustusLista






