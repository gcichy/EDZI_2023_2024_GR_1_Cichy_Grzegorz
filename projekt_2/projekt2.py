import pandas as pd
import numpy as np
import pymssql

class DBServer:  
    def __init__(self,server, user, password, database):
            
        self.server_name = server
        self.user_name = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
    def db_connect(self):
        try:
            
            conn = pymssql.connect(
                server = self.server_name,
                user = self.user_name,
                password = self.password,
                database = self.database
            )
            self.connection = conn
        except Exception as e:
            raise Exception(f'DBServer.db_connect method: Failed to connect to the database: {e}')
    
    def db_create_cursor(self):
        if not isinstance(self.connection,pymssql._pymssql.Connection):
            raise Exception(f"DBServer.db_create_cursor method: connection is not established properly - self.connection must be of class 'pymssql._pymssql.Connection'")   
        else:
            try:
                self.cursor = self.connection.cursor()
            except Exception as e:
                raise Exception(f"DBServer.db_create_cursor method: failed to create cursor: {e}")

    def execute_command(self,command):
        if self.connection == None or self.cursor == None:
            raise Exception('DBServer.execute_command method: Connection and cursor for DBServer object must be initialized')
        try:
            self.cursor.execute(command)
            rows = self.cursor.fetchall() if self.cursor.rowcount == -1 else None
            
            return rows
        
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"DBServer.execute_command method: failed to execute command: {e}")
        
    def db_close_connection(self):
        self.connection.close()    


def create_tables(db):
    db_validation(db)
    
    try:
        db.cursor.execute('''
                        create table job_title (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            job_title nvarchar(100) UNIQUE
                        )
                          ''')
        db.cursor.execute('''
                        create table skill (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            skill nvarchar(100) UNIQUE
                        )                          
                          ''')
        db.cursor.execute('''
                        CREATE TABLE currency (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            currency nvarchar(3) UNIQUE,
                            currency_full_name nvarchar(100)
                        )                          
                          ''')
        db.cursor.execute('''
                        CREATE TABLE source (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            source nvarchar(100) UNIQUE,
                        )                          
                          ''')
        
        db.cursor.execute('''
                        CREATE TABLE category (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            category nvarchar(100) UNIQUE,
                        )                          
                          ''')
        db.cursor.execute('''
                        CREATE TABLE company (
                            ID int PRIMARY KEY IDENTITY(1,1),
                            name nvarchar(100) UNIQUE
                        )                          
                          ''')
        db.cursor.execute('''
                        CREATE TABLE offer (
                            ID int PRIMARY KEY,
                            job_title_ID int NOT NULL,
                            currency_ID int NOT NULL,
                            category_ID int NOT NULL,
                            company_ID int NOT NULL,
                            source_ID int NOT NULL,
                            link nvarchar(max),
                            seniority nvarchar(100),
                            salary_min float,
                            salary_max float,
                            FOREIGN KEY (job_title_ID) REFERENCES job_title(ID),
                            FOREIGN KEY (currency_ID) REFERENCES currency(ID),
                            FOREIGN KEY (category_ID) REFERENCES category(ID),
                            FOREIGN KEY (company_ID) REFERENCES company(ID),
                            FOREIGN KEY (source_ID) REFERENCES source(ID)
                        )                          
                          ''')
        db.cursor.execute('''
                        CREATE TABLE offer_skill (
                            offer_ID int,
                            skill_ID int,
                            PRIMARY KEY (offer_ID, skill_ID),
                            FOREIGN KEY (offer_ID) REFERENCES offer(ID),
                            FOREIGN KEY (skill_ID) REFERENCES skill(ID),
                        )                           
                          ''')
        
        
    except Exception as e:
        db.connection.rollback()
        raise Exception(f"failed to create database tables: {e}")
        

    
def drop_tables(db):
    db_validation(db)  
    try:
        db.cursor.execute('drop table offer_skill')
        db.cursor.execute('drop table offer')
        db.cursor.execute('drop table job_title')
        db.cursor.execute('drop table skill')
        db.cursor.execute('drop table currency')
        db.cursor.execute('drop table source')
        db.cursor.execute('drop table category')
        db.cursor.execute('drop table company')
    except Exception as e:
        db.connection.rollback()
        raise Exception(f"failed to drop database tables: {e}")


def db_validation(db):
    if not isinstance(db, DBServer):
        raise Exception('Provided db must be of class DBServer')
    if db.connection == None or db.cursor == None:
        raise Exception('Connection and cursor for DBServer object must be initialized')

        
def insert_currency(db,df):
    db_validation(db)
    
    currencies = df['currency'].unique()
    curr_names = np.array(['Złoty polski'])
    currencies = np.column_stack((currencies, curr_names))
    insert_statement = "INSERT INTO currency values  "
    
    for cur in currencies:
        insert_statement += "('" + cur[0] + "','" + cur[1] + "')"
        
    db.execute_command(insert_statement)
 
    
def insert_dim_table(db, df, db_table_name, df_column_name):
    db_validation(db)
    
    values_to_insert = df[df_column_name].unique()
    
    insert_statement = f"INSERT INTO {db_table_name} values  "
    for i, val in enumerate(values_to_insert):
        if i == len(values_to_insert) - 1:
            insert_statement += "('" + val + "')"
        else:
            insert_statement += "('" + val + "'), "
    
    db.execute_command(insert_statement)   

    
def insert_skill(db, df):
    db_validation(db)
    
    values_to_insert = pd.Series(np.concatenate(df['technologies'].values)).unique()
    
    insert_statement = f"INSERT INTO skill values  "
    for i, val in enumerate(values_to_insert):
        if i == len(values_to_insert) - 1:
            insert_statement += "('" + val + "')"
        else:
            insert_statement += "('" + val + "'), "
    
    db.execute_command(insert_statement)  
 
    
def insert_offer(db,df):
    db_validation(db)
    
    insert_statement = f"""
        INSERT INTO offer (
            ID,
            job_title_ID,
            currency_ID,
            category_ID,
            company_ID,
            source_ID,
            link,
            seniority,
            salary_min,
            salary_max
        ) values  """
        
    for i, row in df.iterrows():
        if i == df.shape[0] - 1:
            insert_statement += f""" ({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},'{row[6]}','{row[7]}',{row[8]},{row[9]})"""
        else:
            insert_statement += f""" ({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},'{row[6]}','{row[7]}',{row[8]},{row[9]}), """
            
    db.execute_command(insert_statement)
 
 
def insert_offer_skill(db,df,skill_df):
    db_validation(db)
    
    insert_statement = "INSERT INTO offer_skill values "
    for i, row in df.iterrows():
        
        skills_id =skill_df[skill_df['skill'].isin(row['technologies'])]['skill_ID']
        for sid in skills_id:
            insert_statement += f"({row['ID']}, {sid})," 
        
    insert_statement = insert_statement[:-1]
    db.execute_command(insert_statement)

    
def create_df_from_table(db,table_name,columns):
    db_validation(db)  
    rows = db.execute_command(f'select * from {table_name} order by ID')
    df = pd.DataFrame(data=rows)
    df.columns = columns
    
    return df



def main():
    try:
        df = pd.read_json('job_offers.json',orient='records',lines=True)
        df['category'] = 'Data'
        
        server = DBServer(
            server='DESKTOP-SFO3K5V',
            user = 'user_1',
            password = '9',
            database = 'EDZI_projekt2'
        )
        server.db_connect()
        server.db_create_cursor()
        # drop_tables(server)
        create_tables(server)
        server.connection.commit()
        print('Tables created.')

        insert_dim_table(server,df,'job_title', 'job_title')
        insert_dim_table(server,df,'company', 'company')
        insert_dim_table(server,df,'source', 'source')
        insert_dim_table(server,df,'category', 'category')
        insert_skill(server,df)
        insert_currency(server,df)   
        server.connection.commit()
        print('Data inserted into dim tables.')
 
        company_df = create_df_from_table(server,'company', ['company_ID','company'])
        job_title_df = create_df_from_table(server,'job_title', ['job_title_ID','job_title'])
        source_df = create_df_from_table(server,'source', ['source_ID','source'])
        category_df = create_df_from_table(server,'category', ['category_ID','category'])
        skill_df = create_df_from_table(server,'skill', ['skill_ID','skill'])
        currency_df = create_df_from_table(server,'currency', ['currency_ID','currency','currency_full_name'])

        df_joined = df.merge(currency_df, right_on='currency',left_on='currency')
        df_joined = df_joined.merge(company_df, right_on='company',left_on='company')
        df_joined = df_joined.merge(source_df, right_on='source',left_on='source')
        df_joined = df_joined.merge(category_df, right_on='category',left_on='category')
        df_joined = df_joined.merge(job_title_df, right_on='job_title',left_on='job_title')
        
        insert_offer(server,df_joined.iloc[:,[0,16,11,15,13,14,2,9,4,5]])
        insert_offer_skill(server,df_joined[['ID','technologies']],skill_df)
        server.connection.commit()
        print('Data inserted into offer and offer_skill tables.')  
            
        server.db_close_connection()
        print('Connection closed, program ended with success.')
                    
    except Exception as e:
        print(f'Error caught: {e}')
           
if __name__ == "__main__":
 main()



