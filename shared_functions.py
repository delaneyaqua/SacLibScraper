# login to account
def login(session):
    # get username and password from login_info.txt
    login_file = open('login_info.txt', 'r')
    login_info = {'username':login_file.readline(), 
            'password':login_file.readline(),
            'submit': 'Login'
            }
    login_file.close()

    # log in to site
    login_req = session.post("https://catalog.saclibrary.org/MyAccount/Home", data=login_info)
    print(login_req.status_code)

# handles link plus books
# args: row html
# returns: (title, due_date)
def linkplus(row):
    title = row.find('span', {'class':'result-title'}).get_text()
    hold_info = row.findAll('div', {'class':'result-value'})
    due = hold_info[3].get_text()
    return (title, due)

# get the format of an item (Book, eBook, or AudioBook)
# currently only handles those three formats
def getFormat(hold_info):
    format_ = hold_info[1].get_text().split()

    if 'Book' in format_ or 'Graphic' in format_:
        format_ = 'Book'
    elif 'Audiobook' in format_ or 'Audiobook,' in format_:
        format_ = 'Audiobook'
    elif 'eBook' in format_ or 'eBook,' in format_:
        format_ = 'eBook'
    else:
        format_ = 'Format is not Book, Audiobook, or eBook'
    
    return format_

# get the status of a book (On Shelf, Checkout Out, etc)
def getStatus(main_content):
    # find status of physical book
    status = main_content.find('div', {'class':'related-manifestation-shelf-status'})

    # find status of ebook/audiobook
    if status is None:
        status = main_content.find('div', id='statusValue')

    return status