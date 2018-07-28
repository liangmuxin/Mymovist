from django.shortcuts import render
import pyrebase
from django.contrib import auth
import re
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
config = {
    'apiKey': "AIzaSyDlMK7Vb3gRxi-UX96m-BHjqmmYL8eQIAM",
    'authDomain': "signin-c94ea.firebaseapp.com",
    'databaseURL': "https://signin-c94ea.firebaseio.com",
    'projectId': "signin-c94ea",
    'storageBucket': "signin-c94ea.appspot.com",
    'messagingSenderId': "888606275050"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


def signIn(request):
    return render(request, "signIn.html")


def postsign(request):
    email = request.POST.get("email")
    passwd = request.POST.get("password")
    try:
        user = authe.sign_in_with_email_and_password(email, passwd)
    except:
        message = "Your user name and password is invalid, please try again."
        return render(request, "signIn.html", {"mess": message})

    # print(user["idToken"])
    session_id = user["idToken"]
    request.session["uid"] = str(session_id)
    return render(request, "welcome.html", {"e": email})


def logout(request):
    auth.logout(request)
    return render(request, "signIn.html")


def signUp(request):
    return render(request, "signUp.html")


def postsignup(request):
    email = request.POST.get("email")
    passwd = request.POST.get("pass")
    try:
        user = authe.create_user_with_email_and_password(email, passwd)
    except:
        msg = "cannot create, try again"
        return render(request, "signUp.html", {"mess": msg})
    uid = user["localId"]
    data = {"name": email}
    database.child("users").child(uid).child("username").set(data)
    return render(request, "signIn.html")


# def searchresults(request):  # working on search
#   word = request.POST.get("word")
#   # whatever = database.child("-L845NM4BFQxePE_Xs10").order_by_key().limit_to_first(3).get().val()
#     # myform = whatever[0]["title"]
#     return render(request, "searchresults.html", {"res": word})

def searchalgorithm(mydata, option, mysearch):

    resultlst = []
    if mysearch == "":
        resultlst = mydata
    else:

        if option == "genres":
            for va in mydata:
                for vals in json.loads(va["genres"]):
                    if mysearch == vals["name"].lower() or mysearch == vals["name"].upper():
                        resultlst.append(va)
        elif option == "country":
            for va in mydata:
                for vals in json.loads(va['production_countries']):
                    if mysearch == vals["iso_3166_1"].lower() or mysearch == vals["iso_3166_1"].upper():
                        resultlst.append(va)
        else:
            for va in mydata:
                if mysearch == va["title"].lower() or mysearch == va["title"].upper():
                    resultlst.append(va)
    if len(resultlst) == 0:
        for va in mydata:
            if mysearch[0] == va["title"][0].lower() or mysearch[0] == va["title"][0].upper():
                resultlst.append(va)

    if len(resultlst) > 100:
        return resultlst[0:100]
    elif len(resultlst) == 0:
        return []
    else:
        return resultlst


def fscty(mydata, opt):
    if opt == "uk":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['production_countries']):
                if vals["iso_3166_1"] == "GB":
                    resultlst.append(va)
    elif opt == "us":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['production_countries']):
                if vals["iso_3166_1"] == "US":
                    resultlst.append(va)
    elif opt == "gs":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['production_countries']):
                if vals["iso_3166_1"] == "DE":
                    resultlst.append(va)
    else:
        resultlst = mydata
    return resultlst


def fsgen(mydata, opt):
    if opt == "act":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['genres']):
                if vals["name"] == "Action":
                    resultlst.append(va)
    elif opt == "cri":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['genres']):
                if vals["name"] == "Crime":
                    resultlst.append(va)
    elif opt == "fan":
        resultlst = []
        for va in mydata:
            for vals in json.loads(va['genres']):
                if vals["name"] == "Fantasy":
                    resultlst.append(va)
    else:
        resultlst = mydata
    return resultlst


def fsvot(mydata, opt):
    if opt == "eit":
        resultlst = []
        for va in mydata:
            if float(va["vote_average"]) >= 8:
                resultlst.append(va)
    elif opt == "fiv":
        resultlst = []
        for va in mydata:
            if float(va["vote_average"]) < 8 and float(va["vote_average"]) >= 5:
                resultlst.append(va)
    elif opt == "bel":
        resultlst = []
        for va in mydata:
            if float(va["vote_average"]) < 5:
                resultlst.append(va)
    else:
        resultlst = mydata
    return resultlst


def searchresults(request):
    word = request.POST.get("searchkey")
    option = request.POST.get("searchby")

    if option != "user":
        cty = request.POST.get("country")
        gen = request.POST.get("genres")
        vot = request.POST.get("votes")
        wholedata = database.child("-L845NM4BFQxePE_Xs10").order_by_key().get().val()
        wholedata = fscty(wholedata, cty)
        wholedata = fsgen(wholedata, gen)
        wholedata = fsvot(wholedata, vot)

        output = searchalgorithm(wholedata, option, word)

        titles = []
        genres = []
        country = []
        overviews = []
        rates = []
        for o in output:
            titles.append(o["title"])
            tmp = []
            for o_ in json.loads(o["genres"]):
                tmp.append(o_["name"])
            genres.append(tmp)
            tmp = []
        # country.append(o["production_countries"])
            for o_ in json.loads(o["production_countries"]):
                tmp.append(o_["name"])
            country.append(tmp)
            overviews.append(o['overview'])
            rates.append(o["vote_average"])
        comb = zip(titles, genres, country, rates, overviews)
        # print(type(list(comb)))
        cblst = list(comb)
        # print(len(cblst))
        return render(request, "searchresults.html", {"res": cblst})

    else:
        get_user = database.child("users").shallow().get().val()
        # print(get_user)
        for g in get_user:
            if word == database.child("users").child(g).get().val()["username"]["name"]:
                myuser = word
                ts = database.child("users").child(g).child("savings").shallow().get().val()
                print(word)
                print(ts)
                if ts == None:
                    print(1)
                    return render(request, "nodata.html")
                else:
                    movielst = []
                    for i in ts:
                        tmp = database.child('users').child(g).child("savings").child(i).get().val()
                        movielst.append(tmp)
                    titles = []
                    comments = []
                    rates = []
                    for m in movielst:
                        titles.append(m["Title"])
                        comments.append(m["Comment"])
                        rates.append(m["Rate"])
                    comb = zip(titles, rates, comments)
                    return render(request, "yourfriend.html", {"e": myuser, "res": comb})
        return render(request, "nouser.html")


def savedsearch(request):
    idtoken = request.session['uid']
    tmpuser = authe.get_account_info(idtoken)['users'][0]['localId']
    ts = database.child("users").child(tmpuser).child("savings").shallow().get().val()
    # print(ts)
    movielst = []
    if ts == None:
        return render(request, "nodata.html")
    else:
        for i in ts:
            tmp = database.child('users').child(tmpuser).child("savings").child(i).get().val()
            movielst.append(tmp)
        print(movielst)
        name = database.child("users").child(tmpuser).child("username").get().val()['name']
        titles = []
        comments = []
        rates = []
        for m in movielst:
            titles.append(m["Title"])
            comments.append(m["Comment"])
            rates.append(m["Rate"])
        comb = zip(titles, rates, comments)

        return render(request, "savedsearch.html", {"e": name, "res": comb})


def searchsaved(request, param):
    try:
        param = param.split("%20").join(" ")
    except:
        pass
    wholedata = database.child("-L845NM4BFQxePE_Xs10").order_by_key().get().val()
    output = []
    for val in wholedata:
        if param == val["title"]:
            output.append(val)
            break

    titles = []
    genres = []
    country = []
    overviews = []
    rates = []
    for o in output:
        titles.append(o["title"])
        tmp = []
        for o_ in json.loads(o["genres"]):
            tmp.append(o_["name"])
        genres.append(tmp)
        tmp = []
        # country.append(o["production_countries"])
        for o_ in json.loads(o["production_countries"]):
            tmp.append(o_["name"])
        country.append(tmp)
        overviews.append(o['overview'])
        rates.append(o["vote_average"])
    comb = zip(titles, genres, country, rates, overviews)
    cblst = list(comb)
    return render(request, "searchresults.html", {"res": cblst})


def friendlist(request):
    idtoken = request.session['uid']
    tmpuser = authe.get_account_info(idtoken)['users'][0]['localId']
    friends = database.child("users").child(tmpuser).child("friends").shallow().get().val()
    if friends == None:
        return render(request, "nofriend.html")
    else:
        myfriends = []
        for f in friends:
            myfriends.append(database.child("users").child(tmpuser).child("friends").child(f).get().val()["name"])

        return render(request, "friendlist.html", {"f": myfriends})


def follow(request, param):
    idtoken = request.session['uid']
    tmpuser = authe.get_account_info(idtoken)['users'][0]['localId']
    myname = database.child("users").child(tmpuser).child("username").get().val()["name"]

    import time
    from datetime import datetime
    time_now = datetime.now()
    t = int(time.mktime(time_now.timetuple()))
    tmpdata = {"name": param}

    database.child("users").child(tmpuser).child("friends").child(t).set(tmpdata)
    return render(request, 'welcome.html', {'e': myname})


def create(request, param):
    try:
        param = param.split("%20").join(" ")
    except:
        pass
    data = {
        "thismovie": param
    }
    # print(request.POST.get("what"))
    return render(request, "savinginterface.html", data)


def create_history(request, param):
    print(request.get_full_path())
    rate = request.POST.get("searchby")
    comments = request.POST.get("comments")
    import time
    from datetime import datetime
    time_now = datetime.now()
    t = int(time.mktime(time_now.timetuple()))
    idtoken = request.session['uid']
    tmpuser = authe.get_account_info(idtoken)['users'][0]['localId']
    tmpdata = {
        "Title": param,
        "Rate": rate,
        "Comment": comments
    }
    database.child("users").child(tmpuser).child("savings").child(t).set(tmpdata)
    name = database.child("users").child(tmpuser).child("username").get().val()['name']
    return render(request, 'welcome.html', {'e': name})


def hello(request, param1):
    return HttpResponse("Param is :" + param1)


def backtowelcome(request):
    idtoken = request.session['uid']
    tmpuser = authe.get_account_info(idtoken)['users'][0]['localId']
    name = database.child("users").child(tmpuser).child("username").get().val()['name']
    return render(request, 'welcome.html', {'e': name})


def viewfriend(request, param):
    get_user = database.child("users").shallow().get().val()
    # print(get_user)
    for g in get_user:
        if param == database.child("users").child(g).get().val()["username"]["name"]:
            myuser = param
            ts = database.child("users").child(g).child("savings").shallow().get().val()

            if ts == None:
                return render(request, "nodata.html")
            else:
                movielst = []
                for i in ts:
                    tmp = database.child('users').child(g).child("savings").child(i).get().val()
                    movielst.append(tmp)
                titles = []
                comments = []
                rates = []
                for m in movielst:
                    titles.append(m["Title"])
                    comments.append(m["Comment"])
                    rates.append(m["Rate"])
                comb = zip(titles, rates, comments)
                return render(request, "yourfriend.html", {"e": myuser, "res": comb})
