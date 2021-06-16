#!/usr/bin/python3
print("Content-Type: text/html; charset=utf-8\n")

import requests
from pprint import pprint
import cgi
import cgitb
import random
import sys

requestLimit = 0
apikey = ''
def formToCoordinate(location):
    parsedLocation = '%'.join(location.split())
    locationToCordinate = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={parsedLocation}&key={apikey}')
    coordinateJSON = locationToCordinate.json()

    coordinate = str(coordinateJSON['results'][0]['geometry']['location']['lat']) + ',' + str(coordinateJSON['results'][0]['geometry']['location']['lng'])
    return coordinate

def getReview(place_id,amount):
    therequest = requests.get(f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={apikey}')
    therequestJSON = therequest.json()
    reviews = []
    counter = 0
    
    try:
        for i in therequestJSON['result']['reviews']:
            if counter == amount:
                break
            else:
                reviews.append([i['text'],i['profile_photo_url'],i['rating'],i['relative_time_description'],i['author_name']])
                counter += 1
    except:
        reviews = ['No review found.','https://avaazdo.s3.amazonaws.com/original_5c3920ad08677.jpg','Unknown','Never','Devs Broke the code']

    return reviews


def getPlace(coordinate, type, radius):
    global requestLimit
    if requestLimit == 5:
        raise KeyError
        return ['No place nearby']
    nearbyResturantRequest = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={coordinate}&radius={radius}&keyword={type}&key={apikey}')
    nearbyResturantJSON = nearbyResturantRequest.json()

    try: 
        nearbyResturantChoice = random.choice(nearbyResturantJSON['results'])
    except:
        requestLimit += 1
        return "Error"

    amountTrying = 0

    while 'parking' in nearbyResturantChoice['types'] or nearbyResturantChoice['rating'] < 4 or nearbyResturantChoice['user_ratings_total'] < 30:
        if amountTrying == 10:
            break
        nearbyResturantChoice = random.choice(nearbyResturantJSON['results'])
        amountTrying += 1

    
    nearbyResturantKeyWords = nearbyResturantChoice['types'] #keywords

    nearbyResturantName = nearbyResturantChoice['name'] #name

    nearbyResturantRating = nearbyResturantChoice['rating'] #rating

    nearbyResturantAmountOfReviews = nearbyResturantChoice['user_ratings_total'] #amount of reviews

    nearbyResturantPhotoID = nearbyResturantChoice['photos'][0]['photo_reference']
    nearbyResturantPhoto = f'https://maps.googleapis.com/maps/api/place/photo?photoreference={nearbyResturantPhotoID}&maxheight=1600&key={apikey}'

    nearbyResturantCoordinate = str(nearbyResturantChoice['geometry']['location']['lat']) + ',' + str(nearbyResturantChoice['geometry']['location']['lng']) 

    nearbyResturantPlaceID = nearbyResturantChoice['place_id']
    nearbyResturantReview = getReview(nearbyResturantPlaceID, 1)
    

    
    

    return [nearbyResturantName,nearbyResturantRating,nearbyResturantAmountOfReviews,nearbyResturantPhoto,nearbyResturantKeyWords,nearbyResturantReview,nearbyResturantCoordinate]
    #returns resturant details: a list of [name, rating, # of ratings, photo url, keywords, a review, coords (this don't worry about)]


def directions(origin, target, transport):
    #Get directions/distance to nearby place.
    request = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={target}&mode={transport}&key={apikey}"

    directionRequest = requests.get(request)
    directions = directionRequest.json()

    distanceAway = directions['routes'][0]['legs'][0]['distance']['text']
    timeTakes = directions['routes'][0]['legs'][0]['duration']['text']

    directionList = []
    for step in directions['routes'][0]['legs'][0]['steps']:
        directionList.append(step['html_instructions'])

    return [distanceAway,timeTakes,directionList] #returns a list of [distance away, time elapsed, a list of directions]

def places_to_html(coordinates, type, placebefore, name):
    type = "|".join(type)
    RandomResturantInfo = getPlace(coordinates, type, 1600)
    if RandomResturantInfo == 'Error':
        print(f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Plan my Day</title>
                <link rel="preconnect" href="https://fonts.gstatic.com">
                <link href="https://fonts.googleapis.com/css2?family=Mulish:wght@300&display=swap" rel="stylesheet">
                <link href="error.css" rel="stylesheet">
            </head>
            <body>
                <div class="field">
                <div class="main-ctn">
                    <h1>Oops...</h1>
                    <hr>
                    <br>
                    <p>Looks like we couldn't find any results for {location}. This could either be because:</p>
                    <ul>
                    <li>{location} is <span class="important">too remote</span>, and 5 nearby locations that fit the criteria could not be found.</li>
                    <li>{location} is <span class="important">not specific enough</span> of a location. For example, instead of trying Alaska, try Anchorage, or instead of New York, try Coney Island.</li>
                    <li>We have ran <span class="important">out of requests</span> for the day. We are using a free $200 monthly plan and it is possible to get charged if we exceed it. Thus, we have set a quota where only 25 locations can be serviced a day.</li>
                    </ul>
                    
                    <div class="field button-field">
                    
                    <form class="form" action="./script.py" method="GET" id="form">
                        <input name="location" type="text" placeholder="Insert location">
                        <input id="invisible" name="transport" value="{transportation}">
                        <button type="submit" form="form">Try again</button>
                    </form>
                    </div>
                </div>
                </div>
            </body>
        </html>
        """)
        sys.exit()
    target = RandomResturantInfo[-1]
    
    SampleDirectionsFromPlaceToResturant = directions(coordinates, target, transportation)

    resturant = RandomResturantInfo[0]
    rating = RandomResturantInfo[1]
    image = RandomResturantInfo[3]
    tags = RandomResturantInfo[4]
    reviews = RandomResturantInfo[5]
    placeCords = RandomResturantInfo[6]

    distanceAway = SampleDirectionsFromPlaceToResturant[0]
    timeTakes = SampleDirectionsFromPlaceToResturant[1]
    directionList = SampleDirectionsFromPlaceToResturant[2]

    tag = ""
    for i in tags:
        tag += f'<div class="tag">{i}</div>'

    directionparsed = ""

    for i in directionList:
        directionparsed += f"<li>{i}</li>"

    text, photo, userrating, timeago, author = reviews[0]
    grid = f"""
                    <div class="grid-item">
                        <div class="contain">
                            <h2>{name} <span class="red">+{timeTakes}</span></h2>
                            <div class="flex info">
                                <div class="imagehold">
                                    <img class="main_image" src="{image}">
                                </div>
                                <div class="text-info">
                                    <h1>{resturant}</h1>
                                    <p class="rating">{rating}⭐</p>
                                    <div class="tags">
                                        {tag}
                                    </div>
                                    <div class="review">
                                        <p class="review-text">"{text}"</p>
                                        <div class="author">
                                            <div class="person flex">
                                                <img width="32px" height="32px" src="{photo}">
                                                <p>{author} ~ {userrating}⭐, {timeago}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="gray">
                                    <div class="directions field">
                                        <p>{transportation.capitalize()} instructions from <b>{placebefore}</b> ({distanceAway}-{timeTakes})</p>
                                        <ol>
                                            {directionparsed}
                                        </ol>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
    """
    return grid, placeCords, resturant

formData = cgi.FieldStorage()

d = {}
for k in formData.keys():
    d[k] = formData[k].value

transportation = d['transport']
try:
    location = d['location']
except:
    location = 'Stuyvesant High School'
    
initalcoor = formToCoordinate(location)


breakfast, bcoor, bbefore = places_to_html(initalcoor, ['bakery', 'cafe', 'breakfast'], location, "Breakfast (9:00 A.M to 9:30 A.M)")
attraction1, acoor1, abefore1 = places_to_html(bcoor, ["attraction", "bowling", "park", "theater", "beach", "hiking", "Museum"], bbefore, "Attraction #1 (9:30 A.M to 2 P.M)")
lunch, lcoor, lbefore = places_to_html(acoor1, ['restaurant', 'lunch'], abefore1, "Lunch (2:00 P.M to 2:30 P.M)")
attraction2, acoor2, abefore2 = places_to_html(lcoor, ["mall", "park", "zoo", "movie"], lbefore, "Attraction #2 (2:30 P.M to 7:00 P.M)")
dinner, dcoor, dbefore = places_to_html(acoor2, ['restaurant', 'dinner'], abefore2, "Dinner (7:00 P.M to 2:30 P.M)")

body = breakfast + attraction1 + lunch + attraction2 + dinner
html = f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Plan my Day</title>
        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
        <link href="scriptstyle.css" rel="stylesheet">
    </head>
    
    <body>
        <div class="container main-container">
            <div class="grid main-grid">
                <div class="grid-item field first" id="about">
                    <h1>Your randomized plan for <span class="red">{location}</span></h1>
                </div>
                {body}
                <div class="field">
                    <h1 class="remind">Unsatisfied with the results? Try a <a class="last" href="./index.html">different location</a>, or <a class="last" href="" >reload</a> the page!</h1>
                </div>
            </div>
        </div>
    </body>
</html>
"""
print(html)
