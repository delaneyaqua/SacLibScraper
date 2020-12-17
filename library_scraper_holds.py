import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import shared_functions as sf

filename = 'holds.txt'

# Start the session
session = requests.Session()

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
    copies = main_content.find('div', {'class':'smallText'})
    if copies is not None:
        copies = copies.get_text()
        f.write(copies)
        f.write('\n')
        copies = copies.split()
        #f.write(copies[0] + ' ' + copies[2] + '\n')

    # get details on copies
    if format_ == 'Book' and status.get_text() != 'On Shelf':
        copiesPanel = soup2.find(id='copiesPanel')
        f.write('Copies:\n')
        for copies_info in copiesPanel.findAll('span', {'class':'checkedout'}):
            f.write('  ' + copies_info.get_text() + '\n')
    elif format_ == 'eBook':
        panel = soup2.find(id = 'otherEditionsPanel')
        if panel is None:
            panel = soup2.find(id = 'copyDetailsPanelBody')
            table = panel.findAll('tr')
            num_copies = table[1].get_text()[:-1]
            num_holds = panel.find('p').get_text().split()[2]
            f.write(num_copies)
            if num_copies == '1':
                f.write(' copy, ')
            else:
                f.write(' copies, ')
            f.write(num_holds + ' people are on the wait list.\n')
        else:
            for copy_row in panel.findAll(class_='row related-manifestation'):
                copy = copy_row.find(id=re.compile('eBook'))
                if copy is not None:
                    copy_info = copy_row.find('div', {'class':'smallText'}).get_text()
                    f.write(copy_info + '\n')
    elif format_ == 'Audiobook':
        panel = soup2.find(id = 'otherEditionsPanel')
        if panel is None:
            panel = soup2.find(id = 'copyDetailsPanelBody')
            table = panel.findAll('tr')
            num_copies = table[1].get_text()[:-1]
            num_holds = panel.find('p').get_text().split()[2]
            f.write(num_copies)
            if num_copies == '1':
                f.write(' copy, ')
            else:
                f.write(' copies, ')
            f.write(num_holds + ' people are on the wait list.\n')
        else:
            for copy_row in panel.findAll(class_='row related-manifestation'):
                copy = copy_row.find(id=re.compile('eAudiobook'))
                if copy is not None:
                    copy_info = copy_row.find('div', {'class':'smallText'}).get_text()
                    f.write(copy_info + '\n')

    f.write('\n')
    time.sleep(0.5) #pause the code for a sec
f.close()