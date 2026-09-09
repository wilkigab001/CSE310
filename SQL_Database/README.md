# Overview
I created an expense tracker that allows me to see my expenses and track them. It allows me to view between multiple dates, and uses a one to many relationship.

I wrote this software to experiment with relational databases and to track my expenses.


[Software Demo Video](https://www.loom.com/share/836f752e62cf48aa91e8b4d992cb4006)

# Relational Database

There are two tables I am using. There is 'Categories' and 'Expenses'. Expenses has a foreign key of categories_id, this is how they will join on categories. You can run a statement like ``` LEFT JOIN Expenses ON Expenses.categories_id = Categories.id ``` and this will join the two tables in a one to many relationship. The Foreign key of categories_id allows there to be a relationship between the two objects

# Development Environment

I used Python, VSCode and SQLLite3 to develop the software.

The two languages I used were Python and Sqllite3. Python is great at writing queries and working with data, meanwhile SQLlite3 is great at working with the data and the tables.

# Useful Websites


- [W3 Schools](https://www.w3schools.com/sql/)
- [Microsoft](https://www.microsoft.com/en-us/sql-server)

# Future Work


- I would like to make the tables bigger, have more columns and be able to keep track of more things
- I didn't use the 'cleanest' python code, i just wrote what I could come up with, so I would like to slim that down a little bit.
- I would like to use more advanced joins and functions within sql