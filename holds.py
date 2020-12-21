import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import shared_functions as sf

filename = 'holds.txt'

# Start the session
session = requests.Session()

# login to your account
sf.login(session)

# navigate to the hold page
s = session.get('https://catalog.saclibrary.org/MyAccount/Holds')

soup = BeautifulSoup(s.text, 'html.parser')

f = open(filename, 'w')
# loop through each hold item
for row in soup.findAll('div', {'class':'result row'}):
    title = row.find('a', {'class':'result-title'})
    if title is None:   # assume this is Link+ book
        (title, due) = sf.linkplus(row)
        f.write(title + '\n')
        f.write('Due: ' + due + '\n')
        continue
    f.write(title.get_text() + '\n')

    # check if book is available for pickup
    hold_info = row.findAll('div', {'class':'result-value'})
    position = hold_info[3].get_text()
    if position == 'Now':
        f.write(position + '\n\n')
        continue

    # determine format (Book, Audiobook, eBook)
    format_ = sf.getFormat(hold_info)
    f.write(format_ + '\n')
    if format_ == 'Format is not Book, Audiobook, or eBook':
        continue

    # get hold position
    if len(hold_info) > 4:  # books have position at [4], ebooks/audiobooks at [3]
        position = hold_info[4].get_text()
    f.write('Position: ' + position + '\n')
    position = position.split()
    '''
    if format_ == 'Book':
        f.write(position[0] + ' ' + position[2] + '\n')
    else:
        f.write(position[0] + ' ' + position[3] + '\n')
    '''

    # if not available, follow book's url
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

    # get details on copies
    if format_ == 'Book' and status.get_text() != 'On Shelf':
        # num copies, num people on the waitlist
        copies = sf.getCopiesBook(main_content)
        if copies is not None:
            copies = copies.get_text()
            f.write(copies)
            f.write('\n')
            #copies = copies.split()
            #f.write(copies[0] + ' ' + copies[2] + '\n')

        # print a list of statuses of all copies
        copiesPanel_list = sf.getCopiesPanel(soup2)
        f.write('Copies:\n')
        for copies_info in copiesPanel_list:
            f.write('  ' + copies_info.get_text() + '\n')
    elif format_ == 'eBook':
        info = sf.getCopiesEAudio(soup2, 'eBook')
        f.write(info)
    elif format_ == 'Audiobook':
        info = sf.getCopiesEAudio(soup2, 'eAudiobook')
        f.write(info)

    f.write('\n')
    time.sleep(0.5) #pause the code for a sec
f.close()