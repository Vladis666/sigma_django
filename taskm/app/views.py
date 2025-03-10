from django.shortcuts import render

def index(request):
    return render(request, "index.html")

def statistic(request):
    return render(request,"statistic.html")

def tasks(request):
    return  render(request,"tasks.html")

def page_not_found(request, exception):
    return render(request,"notfound.html")