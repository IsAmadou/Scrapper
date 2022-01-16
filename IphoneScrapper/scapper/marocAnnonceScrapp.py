import re
from datetime import datetime, timedelta

import pytz
import requests
from bs4 import BeautifulSoup

from IphoneScrapper.models import Phone


class MarocAnnonceScrapp:

    def __init__(self):
        url = 'https://www.marocannonces.com/maroc/telephones-portables--b359.html?kw=iphone&pge={}'
        self.marocAnnonce(url)

    def marocAnnonce(self, url):
        try:
            currentPage = 1
            morePage = True
            lastPhoneDate = Phone.objects.filter(origin__icontains="Maroc annonces").order_by('-dateAnnonce')
            if len(lastPhoneDate):
                lastPhoneDate = (lastPhoneDate[:1])[0].dateAnnonce.replace(tzinfo=pytz.utc)
            else:
                lastPhoneDate = datetime(2020, 1, 1, 0, 0, 0, 0).replace(tzinfo=pytz.utc)

            print(f"Annonceeeeeeeee {lastPhoneDate}")
            while morePage and currentPage <= 2:
                page = requests.get(url.format(currentPage))
                soup = BeautifulSoup(page.content, "html.parser")
                phonesHtml = soup.find("ul", class_="cars-list").find_all("li")

                for phoneHtml in phonesHtml:
                    try:
                        _class = phoneHtml.get("class")
                        if _class is not None and _class[0] == 'adslistingpos':
                            continue
                        else:
                            phoneDict = {}

                            # Title
                            title = phoneHtml.find("h3")
                            if title:
                                phoneDict['title'] = (" ".join(title.text.split())).lower()

                            # Price
                            price = phoneHtml.find("strong", class_="price")
                            if price:
                                phoneDict['price'] = int(''.join(re.findall("[0-9]+", " ".join(price.text.split()))))
                            else:
                                phoneDict['price'] = 0

                            # City
                            city = phoneHtml.find("span", class_="location")
                            if city:
                                phoneDict['city'] = (" ".join(city.text.split())).lower()

                            # DateAnnonce
                            dates = phoneHtml.find_all("em", class_="date", limit=1)
                            phoneDict['time_hour'] = int(
                                dates[0].find_all("span")[-1].text.strip().lower().split(':')[0])
                            phoneDict['time_minute'] = int(
                                dates[0].find_all("span")[-1].text.strip().lower().split(':')[1])

                            if dates[0].find("span", class_="cnt-today"):
                                d = datetime.today()
                                phoneDict['day'] = d.day
                                phoneDict['month'] = d.month
                                phoneDict['year'] = d.year
                            else:
                                date = dates[0].text.strip().lower()
                                if re.findall('[a-z]+', date)[0] == "hier":
                                    d = datetime.today() - timedelta(days=1)
                                    phoneDict['day'] = d.day
                                    phoneDict['month'] = d.month
                                    phoneDict['year'] = d.year
                                else:
                                    d = date.split(' ')
                                    phoneDict['day'] = int(d[0])
                                    phoneDict['month'] = ['jan', 'fév', 'mar', 'avr', 'mai', 'jun', 'jul',
                                                          'aoû', 'sep', 'oct', 'nov', 'déc'].index(str(d[1])) + 1
                                    if len(d[2]):
                                        phoneDict['year'] = int(d[2])
                                    else:
                                        phoneDict['year'] = datetime.now().year - 1

                            phoneDict['datetime'] = datetime(phoneDict['year'], phoneDict['month'], phoneDict['day'],
                                                             phoneDict['time_hour'], phoneDict['time_minute'], 0,
                                                             0).replace(tzinfo=pytz.utc)

                            # Compare LastPhone date and new getting phone date to know if you need to store it.
                            if phoneDict['datetime'] > lastPhoneDate:

                                queryRes = Phone.objects.create(title=phoneDict['title'], price=phoneDict['price'],
                                                              city=phoneDict['city'], dateAnnonce=phoneDict['datetime'],
                                                              origin='Maroc annonces')
                                print(queryRes.__str__())
                            else:
                                morePage = False
                                break
                    except Exception as e:
                        print(e)
                        continue

                if morePage:
                    next = int(soup.find("li", class_="next").a.get("href").strip().lower().split('&')[-1]
                               .split('=')[-1])
                    if currentPage != next:
                        currentPage = next
                        continue
                    else:
                        break
                else:
                    break

        except Exception as e:
            print(e)
            pass
