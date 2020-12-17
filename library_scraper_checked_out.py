import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import datetime
import shared_functions as sf

filename = 'checkedOut.txt'

# Start the session
session = requests.Session()

# login to your account
sf.login(session)

# Nnvigate to checked out page
s = session.get('https://catalog.saclibrary.org/MyAccount/CheckedOut')

soup = BeautifulSoup(s.text, 'html.parser')

f = open(filename, 'w')
# loop through eash checked out item
for row in soup.findAll('div', {'class':'result row'}):
    title = row.find('a', {'class':'result-title'})
    if title is None:   # assume this is Link+ book
        (title, due) = sf.linkplus(row)
        f.write(title + '\n')
        f.write('Due: ' + due + '\n')
        continue
    f.write(title.get_text() + '\n')

    hold_info = row.findAll('div', {'class':'result-value'})

    # determine format (Book, Audiobook, eBook)
    format_ = sf.getFormat(hold_info)
    f.write(format_ + '\n')
    if format_ == 'Format is not Book, Audiobook, or eBook':
        continue


    # write the due date
    f.write('Due: ' + hold_info[4].get_text() + '\n')
    if len(hold_info) > 5:  # write number of times item has been renewed
        f.write('Renewed: ' + hold_info[5].get_text() + '\n')

    # follow book's url
    link = title['href']
    book_url = 'https://catalog.saclibrary.org'+ link
    s2 = session.get(book_url)
    soup2 = BeautifulSoup(s2.text, 'html.parser')
    main_content = soup2.find(id='main-content')
    if main_content is None:
        f.write('\n')
        continue

    # get the status of a book
    status = sf.getStatus(main_content)
    f.write('Status: ' + status.get_text() + '\n')
    if status.get_text() == 'On Shelf':
        f.write('(SHOULD BE RENEWABLE)\n')
    '''
    copies = main_content.find('div', {'class':'smallText'})
    if copies is not None:
        copies = copies.get_text()
        f.write(copies)
        copies = copies.split()
        if int(copies[0]) <= int(copies[2]):
            f.write(' (UNLIKELY TO BE RENEWABLE)')
        else:
            f.write(' (SHOULD BE RENEWABLE)')
        f.write('\n')
    '''

    # get details on copies
    if format_ == 'Book':
        copiesPanel_list = sf.getCopiesPanel(soup2)

        # get my due date to later determine which copy is mine
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        my_due_date = ('Due ' + hold_info[4].get_text()).split()
        my_due_date_datetime = datetime.datetime(int(my_due_date[3]),months.index(my_due_date[1])+1,int(my_due_date[2][:-1]))

        copies = sf.getCopiesBook(main_content) # num copies, num people on the waitlist
        if copies is not None:
            copies = copies.get_text()
            f.write(copies + '\n')

            # give a rough indication of renewability
            renewable = sf.estimateRenewable(copies, copiesPanel_list, my_due_date_datetime)
            f.write(renewable + '\n')

        # print a list of statuses all copies, with your copy marked
        f.write('Copies:\n')
        found_mine = False  # there might be other copies with your same due date, so only mark the first one as yours
        for copies_info in copiesPanel_list:
            f.write('  ' + copies_info.get_text())
            copy_due_date = copies_info.get_text().split()
            if copy_due_date[:4] == my_due_date[:4] and found_mine == False:
                f.write(' (MY COPY)')
                found_mine = True
            f.write('\n')
    elif format_ == 'eBook':
        info = sf.getCopiesEAudio(soup2, 'eBook')
        f.write(info)
    elif format_ == 'Audiobook':
        info = sf.getCopiesEAudio(soup2, 'eAudiobook')
        f.write(info)
    
    f.write('\n')
    time.sleep(0.5) #pause the code for a sec
f.close()
