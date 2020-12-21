# SacLibScraper
A tool to gather information about you holds and checked out items from the Sacramento Public Library website. This tool might also be usable for other libraries if they are built similarly to SacLib, but I don't know.

To allow this program to access your account, you should create a file called login_info.txt with the two lines:
```
<username>
<password>
```

## Holds
For each item on hold, the output fill will contain:
```
Title
Format (Book, eBook, Audiobook)
Position
Satus (Now, In Transit, On Holdshelf, Checked Out, On Hold, On Order, In Processing)
num copies, num people on the waitlist
```

ex.
```
The republic for which it stands : the United States during Reconstruction and the Gilded Age, 1865-1896
eBook
Position: 2 out of 3
Status: Checked Out
2 copies, 3 people are on the wait list.
```

## Checked Out
For each checked out item, the output fill will contain:
```
Title
Format (Book, eBook, Audiobook)
Due Date
Satus (On Shelf, In Transit, Checked Out, On Hold)
num copies, num people on the waitlist. <(SHOULD BE RENEWABLE) or (UNLIKELY TO BE RENEWABLE)>
A list of all copies of this item and their statuses. Next to your copy will be (MY COPY)
```

ex.
```
Watchmen
Book
Due: Dec 19, 2020
Status: Checked Out
5 copies, 5 people are on the wait list. (UNLIKELY TO BE RENEWABLE)
Copies:
  Due Dec 26, 2020
  Due Jan 12, 2021
  Due Dec 19, 2020 (MY COPY)
  On Holdshelf
  On Holdshelf
```


## Limitations
For both holds and checked out items, this code has been tested for a decent amount of physical books, eBooks, and audioBooks. It was tested for one Link+ book. It has not been tested for any other items (movies, cds, etc). Untested items may crash the program, or the program may skip the item and continue running when it does not identify a recognized format (Book, eBook, Audiobook).

For checked out items, the estimation of renewability is a very rough estimate.