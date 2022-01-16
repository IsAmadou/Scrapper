import re
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from IphoneScrapper.models import Phone


class AvitoScrapp:

    def __init__(self):
        URL = 'https://www.avito.ma/fr/maroc/t%C3%A9l%C3%A9phones/iphone--%C3%A0_vendre?o={}&pcb=2'
        self.avito(URL)

    def avito(self, url):
        try:
            currentPage = 1
            morePage = True
            lastPage = 1

            lastPhone = Phone.objects.filter(origin__icontains="Avito").order_by('-dateAnnonce')
            lastPhoneDate = Phone.objects.filter(origin__icontains="Avito").order_by('-dateAnnonce')

            if len(lastPhoneDate):
                lastPhoneDate = (lastPhoneDate[:1])[0].dateAnnonce.replace(tzinfo=pytz.utc)
            else:
                lastPhoneDate = datetime(2020, 1, 1, 0, 0, 0, 0).replace(tzinfo=pytz.utc)

            print(f"Avitooooooooooooooooooooo {lastPhoneDate}")
            while morePage and currentPage <= 3: # lastPage:
                page = requests.get(url.format(currentPage))
                soup = BeautifulSoup(page.content, "html.parser")
                phonesHtml = soup.find("div", class_="sc-1nre5ec-0 gpXkJn listing").find_all("div", "oan6tk-0 hEwuhz")

                for phoneHtml in phonesHtml:
                    try:
                        phoneDict = {}

                        # title
                        title = phoneHtml.find("span", class_="oan6tk-17 lfyRQw")
                        if title:
                            phoneDict['title'] = (" ".join(title.text.split())).lower()

                        # Price
                        price = phoneHtml.find("span", class_="sc-1x0vz2r-0 kKGxRt oan6tk-15 caZekr")
                        if price:
                            phoneDict['price'] = int(''.join(re.findall("[0-9]+", " ".join(price.text.split()))))
                        else:
                            phoneDict['price'] = 0

                        # City
                        city = phoneHtml.find_all("span", class_="sc-1x0vz2r-0 kIeipZ", limit=2)
                        if city:
                            phoneDict['city'] = city[1].text.strip().lower()

                        # DateAnnonce
                        dates = phoneHtml.find_all("span", class_="sc-1x0vz2r-0 kIeipZ", limit=2)
                        if dates:
                            times = dates[0].text.split(":")
                            now = datetime.now()
                            if len(times) == 2:
                                phoneDict['datetime'] = datetime(now.year, now.month, now.day, int(times[0]),
                                                                 int(times[1]),
                                                                 0, 0).replace(tzinfo=pytz.utc)
                            elif len(times) == 1:
                                phoneDict['day'] = int((times[0].split(" "))[0])
                                phoneDict['month'] = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
                                                      'août', 'septembre', 'octobre', 'novembre', 'décembre'].index(
                                    (times[0].split(" "))[1].lower()) + 1

                                date = datetime.now()
                                testDate = datetime(datetime.now().year, phoneDict['month'], phoneDict['day'],
                                                    date.hour,
                                                    date.minute, 0, 0).replace(tzinfo=pytz.utc)

                                today = phoneDict['datetime'] = datetime(date.year, date.month, date.day, date.hour,
                                                                         date.minute, 0, 0).replace(tzinfo=pytz.utc)
                                if testDate > today:
                                    testDate = datetime(datetime.now().year - 1, phoneDict['month'], phoneDict['day'],
                                                        date.hour, date.minute, 0, 0).replace(tzinfo=pytz.utc)
                                phoneDict['datetime'] = testDate

                        # Compare LastPhone date and new getting phone date to know if you need to store it.
                        if len(lastPhone) :
                            if phoneDict['datetime'] > lastPhoneDate  and (lastPhone[:1])[0].title != phoneDict['title'] \
                                    and (lastPhone[:1])[0].price != phoneDict['price'] and (lastPhone[:1])[0].origin != 'Avito':
                                queryRes = Phone.objects.create(title=phoneDict['title'], price=phoneDict['price'],
                                                                city=phoneDict['city'], dateAnnonce=phoneDict['datetime'],
                                                                origin='Avito')
                                print(queryRes.__str__())
                            else:
                                morePage = False
                                break
                        else:
                            if phoneDict['datetime'] > lastPhoneDate:
                                queryRes = Phone.objects.create(title=phoneDict['title'], price=phoneDict['price'],
                                                                city=phoneDict['city'],
                                                                dateAnnonce=phoneDict['datetime'],
                                                                origin='Avito')
                                print(queryRes.__str__())
                            else:
                                morePage = False
                                break

                    except Exception as e:
                        print(e)
                        continue
                if morePage:
                    nextPage = int(
                        soup.find_all("a", class_="sc-1cf7u6r-0 fdVuvA sc-2y0ggl-1 jNHVks")[-1].get('href').split("=")[
                            1].split("&")[0])
                    lastPage = int(soup.find_all("a", class_="sc-1cf7u6r-0 fdVuvA sc-2y0ggl-1 jNHVks")[-2].text)

                    if currentPage != nextPage:
                        currentPage = nextPage
                        continue
                    else:
                        break
                else:
                    break

        except Exception as e:
            print(e)
            pass
