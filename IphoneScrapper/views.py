import csv
import threading
from datetime import datetime
import copy

import pytz
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
from Amadou_Issaka_Project.wsgi import backgroundAvitoScrapp, backgroundMarocAnnonceScrapp
from IphoneScrapper.mailing.mail import SendMail
from IphoneScrapper.models import Phone


def home(request):
    phones = Phone.objects.order_by('-dateAnnonce')

    if request.method == 'GET':
        title = request.GET.get('title')
        city = request.GET.get('city')
        minPrice = request.GET.get('minPrice')
        maxPrice = request.GET.get('maxPrice')
        minDate = request.GET.get('minDate')
        maxDate = request.GET.get('maxDate')
        action = request.GET.get('action')

        if title is not None and title:
            phones = phones.filter(title__icontains=title.strip().lower())
        if city is not None and city:
            phones = phones.filter(city__icontains=city.strip())
        if minPrice is not None and minPrice:
            phones = phones.filter(price__gt=int(minPrice.strip()))
        if maxPrice is not None and maxPrice:
            phones = phones.filter(price__lte=int(maxPrice.strip()))
        if minDate is not None and minDate:
            minDate = minDate.split("T")
            minDateDate = minDate[0].split("-")
            minDateTime = minDate[1].split(":")
            minDate = datetime(int(minDateDate[0]), int(minDateDate[1]), int(minDateDate[2]), int(minDateTime[0]),
                               int(minDateTime[1]), 0, 0).replace(tzinfo=pytz.utc)
            phones = phones.filter(dateAnnonce__gt=minDate)
        if maxDate is not None and maxDate:
            maxDate = maxDate.split("T")
            maxDateDate = maxDate[0].split("-")
            maxDateTime = maxDate[1].split(":")
            maxDate = datetime(int(maxDateDate[0]), int(maxDateDate[1]), int(maxDateDate[2]), int(maxDateTime[0]),
                               int(maxDateTime[1]), 0, 0).replace(tzinfo=pytz.utc)
            phones = phones.filter(dateAnnonce__lte=maxDate)

        # Send Search result in Mail
        if action is not None and action == 'SendMail':
            print(action)
            email = request.GET.get("email")
            if email is not None and email:
                mail = SendMail(email, phones)
                mail.sendWithCsv()

    # phones = phones.order_by('-dateAnnonce')
    size = phones.count()
    pagination = Paginator(phones, 15)
    phones = pagination.get_page(request.GET.get('page'))

    # Get List of cities to fill city filter select
    cities = []
    [cities.append(cit) for cit in Phone.objects.order_by('city').values_list('city', flat=True) if cit not in cities]

    return render(request, 'home.html', {
        'phones': phones,
        'size': size,
        'cities': cities,
    })


def scrapp(request):
    avito = threading.Thread(target=backgroundAvitoScrapp)
    ma = threading.Thread(target=backgroundMarocAnnonceScrapp)
    avito.start()
    ma.start()
    return redirect('home')


def exportcsv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="Iphones.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['Title', 'Price', 'City', 'Date Publication', 'Origin'])
    phones = Phone.objects.order_by('-dateAnnonce')
    for phone in phones:
        writer.writerow([phone.title, phone.price, phone.city, phone.dateAnnonce, phone.origin])
    return response
    # return render(request, 'home.html')


def avg(request):
    phones = Phone.objects
    selectedCity = " "
    if request.method == 'GET':
        city = request.GET.get('city')
        selectedCity = city

        if city is not None and city:
            phones = phones.filter(city__icontains=city.strip())

    models = ["IPhone 3G", "IPhone 3GS", "IPhone 4", "IPhone 4s", "IPhone 5", "IPhone 5c", "IPhone 5s",
              "IPhone 6", "IPhone 6 Plus", "IPhone 6s", "IPhone 6s Plus", "IPhone SE", "IPhone 7", "IPhone 7 Plus",
              "IPhone 8", "IPhone 8 Plus", "IPhone X", "IPhone XS", "IPhone XS Max", "IPhone XR ", "IPhone 11",
              "IPhone 11 Pro", "IPhone 11 Pro Max", "IPhone 12 mini", "IPhone 12", "IPhone 12 Pro", "IPhone 12 Pro Max",
              "IPhone 13 mini", "IPhone 13", "IPhone 13 Pro", "IPhone 13 Pro Max"]

    # copy phones in new Manager Objectlist for filtering models and doing average of theirs price
    avg = {}
    for model in models:
        phonesCopie = copy.copy(phones)
        phonesCopie = phonesCopie.filter(title__icontains=model.strip().lower())
        # Get  sum of Iphone models price
        sumModel = 0
        nbrPhone = 0
        for ph in phonesCopie:
            if ph.price > 0:
                sumModel += ph.price
                nbrPhone += 1
        print("Le modele %s à %d" % (model, nbrPhone))
        # Get average of Iphone model price and put it in dict with model as key
        if nbrPhone > 0:
            avg[model] = sumModel / nbrPhone

    # Get List of cities to fill city filter select
    cities = []
    [cities.append(cit) for cit in Phone.objects.order_by('city').values_list('city', flat=True) if cit not in cities]

    return render(request, 'avg.html', {
        'cities': cities,
        'selectedCity': selectedCity,
        'avg': avg,
    })
