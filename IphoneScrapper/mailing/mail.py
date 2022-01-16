import csv

from django.core.mail import EmailMessage

from Amadou_Issaka_Project.settings import EMAIL_HOST_USER


class SendMail:

    def __init__(self, to, phones):
        self.to = to
        self.phones = phones


    def sendWithCsv(self):
        with open('phones.csv', 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['title', 'price', 'city', 'dateAnnonce', 'origin'])
            for phone in self.phones:
                writer.writerow([phone.title, phone.price, phone.city, phone.dateAnnonce, phone.origin])

        msg = EmailMessage(
            "IphoneScrap search result",
            "Hi \n\r Please receive your iphoneScrap search result",
            EMAIL_HOST_USER,
            [self.to.strip()]
        )
        msg.attach_file('phones.csv')
        try:
            msg.send()
        except Exception as e:
            print(e)
