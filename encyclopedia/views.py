from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
from markdown2 import Markdown
from random import randint

from . import util

markdowner = Markdown()

# create new class for query form
class NewQueryForm(forms.Form):
    query = forms.CharField(label="Search wiki")

# create new class for title form
class NewTitleForm(forms.Form):
    title = forms.CharField(label="Enter page title")

# define index view
def index(request):
    # post method covers the search functionality on the home page
    if request.method == "POST":
        form = NewQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            entries = util.list_entries()
            # if exact match found, return entry page
            if query in entries:
                return redirect('wiki:entry', query)
            # otherwise return list with links to matching pages
            else:
                matches = []
                for entry in entries:
                    if query in entry:
                        matches.append(entry)
                return render(request, "encyclopedia/search.html", {
                    "matches": matches,
                    "query": query
                })
    # if method is GET then simply return list of available entries
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(),
            "form": NewQueryForm()
        })

# define view to return entry page
def entry(request, search):
    # return error page of entry not found in wiki
    if util.get_entry(search) == None:
        return render(request, "encyclopedia/error.html")
    # otherwise convert Md file content to HTML and render entry page
    else:
        entry = markdowner.convert(util.get_entry(search))
        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "search": search
    })

# define view for new entry page
def new(request):
    # post method if user submits new page
    if request.method == "POST":
        # submit new page
        titleform = NewTitleForm(request.POST)
        if titleform.is_valid():
            title = titleform.cleaned_data["title"]
            entries = util.list_entries()
            # return error response if wiki page already exists
            if title in entries:
                return HttpResponse(f"Error: A wiki page for {title} already exists.")
            content = request.POST['newpage']
            # if title check is passed then save Md file and return new page
            util.save_entry(title, content)
            return redirect('wiki:entry', title)
    # otherwise just render new entry page
    else:
        return render(request, "encyclopedia/new.html", {
            "titleform": NewTitleForm()
        })

# define view for edit entry page
def edit(request, search):
    # if user submits changes
    if request.method == "POST":
        # get title and content from request data
        search = request.POST["title"]
        content = request.POST["editpage"]
        # save the entry in place of existing and redirect to new page
        util.save_entry(search, content)
        return redirect('wiki:entry', search)
    # if user arrives from 'Edit Entry' link on entry page
    else:
        # get the entry content for respective entry title, render edit page with title/content
        content = util.get_entry(search)
        return render(request, "encyclopedia/edit.html", {
            "search": search,
            "content": content
        })

# define view for random page
def random(request):
    # generate random number between 0 and number of entires minus 1
    entries = util.list_entries()
    rand = randint(0, len(entries) - 1)
    # find random entry and redirect
    entry = entries[rand]
    return redirect('wiki:entry', entry)