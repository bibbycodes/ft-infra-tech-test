<div align="center">
<img src="https://travis-ci.com/bibbycodes/ft-infra-tech-test-robert-griffith.svg?token=GtuEshpCkADdwz3Mtzd1&branch=master">
</div>

<h1 align=center>Robert Griffith - FT Cloud Engineer Tech Test Solution</h1>

<div align="center">

[Setup ](#setup) |
[Usage ](#usage) |
[Process ](#process) |
[Architecture ](#architecture)|
[Challenges ](#challenges) |
[Technologies ](#technologies) |
[What I Learned ](#what)|
[Extending](#extending)

</div>

## Setup
To fully use this code you must have an AWS account and credentials must be supplied. To check if you have credentials stored on your computer type in the following command into the terminal.
`cat ~/.aws/credentials`

If the credentials are not present, make sure you set up an AIM user and save your credentials in the following format:

```shell
[default]
aws_access_key_id = <YOUR_ACCESS_KEY>
aws_secret_access_key = <YOUR_SECRET_KEY>
```

Next you should clone this repo and change into the resulting directory.
Now you can start installing packages and setting up the virtual environment.

`npm install` <br>
`pip install -r requirements.txt` <br>

You must also install the sdynamoDB locally:
`sls dynamodb install`

#### Running The Api Locally
To run the app locally you will need two terminals. In the first terminal enter:
`sls dynamodb start`

In the second terminal enter:
`sls wsgi server`

You should now be able to visit `http://localhost:5000` and access the API.

#### Deploying to AWS
In order to deply to AWS you simply type in the following command:
`sls deploy`

This will deploy the database and static files to aws and provide you with a URL endpoint from which you can access the API.

## Usage
First activate the virtual environment and enter the python REPL:
```shell
(venv) (base) $>> source venv/bin/activate`
(venv) (base) $>> python
Python 3.7.4 (default, Aug 13 2019, 15:17:50) 
[Clang 4.0.1 (tags/RELEASE_401/final)] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
```
From here you can import the models and start interacting.
```shell
>>> from lib.Statement import Statement
>>> from lib.Account import Account
>>> my_account = Account(1000)
>>> my_account.balance
1000.0
```
Here we have made an account object and initialzed it a starting balance of 1000. If the starting balance is not supplied, the account will be initialzed with a balance of 0.
Every time we deposit or withdraw money from the account the balance is updated
```shell
>>> my_account.add_transaction("deposit", 1000)
<lib.Transaction.Transaction object at 0x10b66e210>
>>> my_account.add_transaction("withdraw", 500)
<lib.Transaction.Transaction object at 0x10b66e810>
>>> my_account.balance
1500.0
```
If we want to print a statement, we simply pass the account object to the statement class and print it.
```shell
>>> print(Statement.make(my_account))
date || credit || debit || balance
14/02/2020 || 1000.00 || || 2000.00
14/02/2020 || || 500.00 || 1500.00
```
`add_transaction` also accepts a third optional argument that specifies the transaction date. If this argument is not supplied, then the transaction date is set to today. The transaction date argument can be supplied in the format of dd/mm/yyy, dd-mm-yyyy or as an epoch timestamp.
```shell
>>> my_account.add_transaction("withdraw", 700, '10-10-2020')
>>> my_account.add_transaction("deposit", 800, '10-10-2020')
<lib.Transaction.Transaction object at 0x10b65fad0>
>>> print(Statement.make(my_account))
14/02/2020 || 1000.00 || || 2000.00
14/02/2020 || || 500.00 || 1500.00
10/10/2020 || || 700.00 || 800.00
15/10/2020 || 800.00 || || 1600.00
```

Please note that when supplying dates for each transaction it is assumed that these are added in order.

#### API
The API portion of this solution represents a single account. You can deposit and withdraw money as well as get a json file of all transaction and have a statement returned through the following 3 endpoints:

`POST /transactions/add`<br>
`GET /transactions/all`<br>
`GET /statement`

When adding transactions you must supply the transaction type and amount.

#### Tests

To run the tests simply enter `npm run test` into the console. This will provide a detailed overview of all the tests and show coverage. Please ensure that you have activated the virtual environment before runnning tests.

```shell
---------- coverage: platform darwin, python 3.7.4-final-0 -----------
Name                                                                 Stmts   Miss  Cover
----------------------------------------------------------------------------------------
tests/account_deposit_test.py                                           34      0   100%
tests/account_init_test.py                                              13      0   100%
tests/account_withdrawal_test.py                                        32      1    97%
tests/features/add_transaction_deposit_test.py                           7      0   100%
tests/features/add_transaction_withdraw_insufficient_funds_test.py       4      0   100%
tests/features/add_transaction_withdraw_test.py                          7      0   100%
tests/features/statement_no_date_feature_test.py                         9      0   100%
tests/features/statement_with_date_input_test.py                        14      0   100%
tests/statement_test.py                                                 41      0   100%
tests/validate_test.py                                                  42      0   100%
----------------------------------------------------------------------------------------
TOTAL                                                                  203      1    99%


=============================================== 47 passed in 7.11s ================================================
```
## Process

This app was created using TDD and SOLID principles. The first step was to create the models.

#### Account Class

Initially the Account class was made up of 4 functions: `deposit`, `withdraw`, `add_transaction` and `sufficient_funds`.
I noticed that the deposit and withdraw functions were very similar. As a result I decided to merge them into the add_transaction class. This made the code much more DRY and easier to maintain. The input is validated using the Validate Class.

```python
class Account:
  def __init__(self, start_bal = 0):
    self.balance = start_bal if Validate.is_number(start_bal) else 0
    self.ledger = []

  def add_transaction(self, transaction_type, amount, transaction_date=datetime.today()):
    if not transaction_date is self.add_transaction.__defaults__[0]:
      transaction_date = Validate.cast_to_datetime(transaction_date)
    if Validate.is_positive_number(amount) == True:
      if transaction_type == "withdraw":
        if self.sufficient_funds(amount):
          amount = float(amount) * -1
        else:
          return "Insufficient Funds"
      amount = float(amount)
      self.balance += amount
      transaction = Transaction(amount, transaction_type, transaction_date)
      self.ledger.append([transaction, self.balance])
      return transaction
    return "Invalid Input"

  def sufficient_funds(self, amount):
    return self.balance - amount >= 0
```

#### Transaction Class

The Transaction class simply consists of attributes representing the date the transaction was made, the transaction type and amount of money being handled. While this could have easily been handled using a python dictionary, extracting these elements into a class makes it easier to extend functionality should one choose to do so.
```python
class Transaction:
  def __init__(self, amount, transaction_type, date):
    self.date = date
    self.transaction_type = transaction_type
    self.amount = amount
```

#### Validate Class
This class was made specifically to Validate input. Initially input validation was implemented in the other models but as they grew it made sense to extract these functions into the Validate class. I did my best to make the functions semantic in order to make it more readable.

```python
Validate.is_positive_number(20) # => True
Validate.date_format("10-10-2020") # => True
Validate.date_format("10.10.2020") # => False
```

If I had more time I would have spent a bit more time refactoring some of the functions in this class and I would have used regex to check that the date input was valid. This would have been a more efficient use of code in my opinion.

#### Statement Class
This class returns a statement when passed an account object: <br>
It is comprised of 3 functions: <br>
  `headers()` returns the headers of the Statement. <br>
  `format_transaction(record)` formats a single transaction. <br>
  `format_items(record)` ensures that numbers are returned to 2 decimal places <br>
  `make(account)` returns a complete statement as a string. <br>

```python
class Statement:
  def headers():
    return 'date || credit || debit || balance\n'

  def format_transaction(record):
    items = Statement.format_items(record)
    if record[0].transaction_type == "deposit":
      return "{} || {} || || {}\n".format(items[0], items[1], items[2])
    elif record[0].transaction_type == "withdraw":
      return "{} || || {} || {}\n".format(items[0], items[1], items[2])
    return "Invalid Transaction Type"

  def format_items(record):
    date = record[0].date
    if type(date) == float:
      date = datetime.fromtimestamp(date)
    date = date.strftime("%d/%m/%Y")
    amount = ('%.2f' % abs(record[0].amount))
    balance = ('%.2f' % record[1])
    return [date, amount, balance]

  def make(account):
    headers = Statement.headers()
    output_string = ""
    for record in account.ledger:
      output_string += Statement.format_transaction(record)
    return (headers + output_string)[:-1]
```

## CI

## Architecture
The infrastructure for this app was created using the Serverless framework. While this took some time to learn, it allowed me to specify the elements of the infrastructure in a single file. Deployment is then handled with a single command. This allows you to modify the infrastructure with ease and makes maintaining the infrastructure simple.

The static files are stored in an AWS S3 container. The app is served using an API Gateway and executed within a Lambda function. All records are stored in a DynamoDB database
<img src="./graph.png">

#### Challenges

I faced numerous challenges while building this serverless app. Chief among them was having to learn so many new technologies in such a short timespan. Other than making Object Oriented Programs in python, almost everything else was new. I had never used flask before, AWS is brand new to me and Serverless is a framework I had never heard about before.

Another challenge was dealing with DynamoDB. DynamoDB is a noSQL database that uses a hash function to organise data accross partitions. This means that data is not necesarilly stored in the order in which it is inputed. In order to combat this I stored the dates in the database as timestamps which would theoretically allow me to order the records based on when they were entered. I used the boto3 client to interact with the database and stored each records ID as a UUID ensureing that records cannot be overwrriten by accident.

I also faced issues storing numbers in the database, the boto3 client was rejecting int and float values which meant that they had to be converted into string values going into the database and back to number values when coming out. This was not ideal and if I had more time I would have liked to conduct more research into this issue. 

I also would have probably used mongoDB instead of DynamoDB, given more time. Since the records are essentially a time series, a noSQL structure makes sense. MongoDB would have allowed me to sort values in the database by any of the attributes and this would have made more sense in hindsight.




