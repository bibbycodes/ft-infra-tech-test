from lib.Account import Account

def test_init_account_instance():
  account = Account()
  assert account.balance == 0

def test_init_account_instance_with_starting_balance():
  account = Account(300)
  assert account.balance == 300

def test_init_account_with_string_as_balance():
  account = Account("hello")
  assert account.balance == 0

def test_init_account_with_none_value():
  account = Account(None)
  assert account.balance == 0