
from deta import Deta
import os
from dotenv import load_dotenv

# load the environment variables
load_dotenv(".env.txt")
DETA_KEY =os.getenv("DETA_KEY")

#DETA_KEY = "a0i75qej_BD6xWQsspT5JCZtSNHbcnmfYEDxDuByi"      #os.getenv("DETA_KEY")

#initialize with a project key
deta = Deta(DETA_KEY)

# Create/connect a database
db =deta.Base("Personal_budget_report")

def insert_period(period, incomes, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)



