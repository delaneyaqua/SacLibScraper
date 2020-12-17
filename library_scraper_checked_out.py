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
        copiesPanel = soup2.find(id='copiesPanel')
        copiesPanel_list = copiesPanel.findAll('span', {'class':'checkedout'})

        # get my due date to later determine which copy is mine
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        my_due_date = ('Due ' + hold_info[4].get_text()).split()
        my_due_date_datetime = datetime.datetime(int(my_due_date[3]),months.index(my_due_date[1])+1,int(my_due_date[2][:-1]))

        copies = main_content.find('div', {'class':'smallText'})
        if copies is not None:
            copies = copies.get_text()
            f.write(copies)
            copies = copies.split()
            if int(copies[0]) <= int(copies[2]):
                f.write(' (UNLIKELY TO BE RENEWABLE)')
            else:
                count = 0
                for copy_status in copiesPanel_list:
                    copy_status_text = copy_status.get_text()
                    if copy_status_text == 'In Transit' or copy_status_text == 'On Holdshelf' or copy_status_text == 'On Shelf':
                        count += 1
                    else:
                        due_split = copy_status_text.split()
                        due_datetime = datetime.datetime(int(due_split[3]),months.index(due_split[1])+1,int(due_split[2][:-1]))
                        if due_datetime < my_due_date_datetime:
                            count += 1
                if count < int(copies[0]):
                    f.write(' (SHOULD BE RENEWABLE)')
                else:
                    f.write(' (UNLIKELY TO BE RENEWABLE)')
            f.write('\n')

        f.write('Copies:\n')
        found_mine = False
        for copies_info in copiesPanel_list:
            f.write('  ' + copies_info.get_text())
            copy_due_date = copies_info.get_text().split()
            if copy_due_date[:4] == my_due_date[:4] and found_mine == False:
                f.write(' (MY COPY)')
                found_mine = True
            f.write('\n')
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