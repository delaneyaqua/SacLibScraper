import re

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

# for Book format, returns the string 'num copies, num people on the waitlist'
def getCopiesBook(main_content):
    copies = main_content.find('div', {'class':'smallText'})
    return copies

# for eBook or AudioBook format, returns the string 'num copies, num people on the waitlist'
# etype is 'eBook' or 'eAudiobook'
def getCopiesEAudio(soup, etype):
    info = ''

    panel = soup.find(id = 'otherEditionsPanel')
    if panel is None:
        panel = soup.find(id = 'copyDetailsPanelBody')
        table = panel.findAll('tr')
        num_copies = table[1].get_text()[:-1]
        num_holds = panel.find('p').get_text().split()[2]
        info = num_copies
        if num_copies == '1':
            info += ' copy, '
        else:
            info += ' copies, '
        info = info + num_holds + ' people are on the wait list.\n'
    else:
        for copy_row in panel.findAll(class_='row related-manifestation'):
            copy = copy_row.find(id=re.compile(etype))
            if copy is not None:
                copy_info = copy_row.find('div', {'class':'smallText'}).get_text()
                info = copy_info + '\n'
    
    return info

# get a list of copies of the item
def getCopiesPanel(soup):
    copiesPanel = soup.find(id='copiesPanel')
    copiesPanel_list = copiesPanel.findAll('span', {'class':'checkedout'})
    return copiesPanel_list

# rough estimate of renewability of checked out item
def estimateRenewable(copies, copiesPanel_list, my_due_date_datetime):
    renewable = ''

    copies = copies.split()
    if int(copies[0]) <= int(copies[2]):
        renewable = '(UNLIKELY TO BE RENEWABLE)'
    # count how many copies should be returned before your copy is due
    # this does not take into account the fact that other patrons may later renew their copy
    else:
        count = 0
        for copy_status in copiesPanel_list:
            copy_status_text = copy_status.get_text()
            due_split = copy_status_text.split()
            #if copy_status_text == 'In Transit' or copy_status_text == 'On Holdshelf' or copy_status_text == 'On Shelf':
            if due_split[0] != 'Due':   # copies without a due date should be automatically counted (they are In Transit, On Holdshelf, or On Shelf)
                count += 1
            else:   # copies due before my copy are added to the count
                due_datetime = datetime.datetime(int(due_split[3]),months.index(due_split[1])+1,int(due_split[2][:-1]))
                if due_datetime < my_due_date_datetime:
                    count += 1
        if count < int(copies[0]):
            renewable = '(SHOULD BE RENEWABLE)'
        else:
            renewable = '(UNLIKELY TO BE RENEWABLE)'

    return renewable

