## Load in credentials
import json
import mysql.connector
import sqlalchemy
import pymysql

import string

def get_databases(cur,verbose=True):
    """[summary]

    Args:
        cur ([type]): [description]
        verbose (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    cur.execute("SHOW DATABASES")
    databases = cur.fetchall()

    if verbose:
        print(f"[i] DATABASES FOUND:")
        [print(f"{db}") for db in databases];
    # print(databases)
    return databases



def get_sql_connectors(auth_path="/Users/jamesirving/.secret/mysql_login.json",
host='localhost',database = "lessons"):
    """Connects to my_sql server using myswl.connector and rloads the database and cursor

    Args:
        auth_path (str, optional): json file with mysql_login. Defaults to "/Users/jamesirving/.secret/mysql_login.json".
                                    Must have 'user' and 'passwd' keys.
        host (str, optional): Server to connect to. Defaults to 'localhost'.
        database (str, optional): database to connect to. Defaults to "lessons".
    
    Returns:
        mydb (from mysql.connect)
        cur (mydb cursor)
        engine (sqlalchemy engine for pandas)

    """
    with open(auth_path,'r+') as f:
        my_login = json.loads(f.read())

    mydb =  mysql.connector.connect( host=host,  user = my_login['user'], 
    passwd=my_login['passwd'],
    database = database)
    cur = mydb.cursor()
    get_databases(cur)


    cmd = f"mysql+pymysql://{my_login['user']}:{my_login['passwd']}@{host}/{database}"
    engine = sqlalchemy.create_engine(cmd)

    return mydb, cur,engine


def clean_df_columns_for_sql(df,replace_dict = {
    "Type":"Repo_Type",'index':'number index'},space_replace='_'):

    
    df = df.rename(replace_dict,axis=1).copy()

    # Remove punctuation/spaces
    bad_chars = string.punctuation

    fixed_cols = []
    for c in df.columns:
        for char in bad_chars:
            c = c.replace(char,'')
        # print(c_new)

        c_new = c.replace(' ',space_replace)
        fixed_cols.append(c_new)

    df.columns = fixed_cols
    return df
