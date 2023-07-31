import psycopg2
import logging

class DatabaseOperations:
    def __init__(self,username, password, host, name):
        self.username = username
        self.password = password
        self.host = host
        self.name = name

    def connect(self):
        """
        Connect to the PostgreSQL database server
        """
        conn = None
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(database=self.name, user=self.username, password=self.password, host = self.host)
    
            # create a cursor
            cur = conn.cursor()
            
            # get version to ensure it works
            logging.info('PostgreSQL database version:')
            cur.execute('SELECT version()')
    
            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            logging.info(db_version)
           
	    # close the communication with the PostgreSQL
            cur.close()
        except psycopg2.OperationalError as e:
            # Catch the specific exception for a failed connection attempt
            logging.error(e)
            logging.info('Attempting to create the database...')
            # Attempt to create the database and tables using the createdb method
            self.createdb()
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(e)
        finally:
            if conn is not None:
                conn.close()
                logging.info('Database connection closed.')


    def createdb(self):
        """
        Create the database tables
        """
        try:
            # Connect to the PostgreSQL server
            conn = psycopg2.connect(database='postgres', user=self.username, password=self.password, host=self.host)

            # Create a cursor
            cur = conn.cursor()

            # Sample table
            cur.execute("""
                CREATE TABLE Sample (
                    sample_id SERIAL PRIMARY KEY
                )
            """)

            # Mutation table
            cur.execute("""
                CREATE TABLE Mutation (
                    mutation_id SERIAL PRIMARY KEY,
                    sample_id INTEGER REFERENCES Sample(sample_id)
                )
            """)

            # Transcript table
            cur.execute("""
                CREATE TABLE Transcript (
                    transcript_id SERIAL PRIMARY KEY,
                    mutation_id INTEGER REFERENCES Mutation(mutation_id)
                )
            """)

            # Peptide table
            cur.execute("""
                CREATE TABLE Peptide (
                    peptide_id SERIAL PRIMARY KEY,
                    transcript_id INTEGER REFERENCES Transcript(transcript_id),
                    pos INTEGER NOT NULL,
                    peptide VARCHAR(255) NOT NULL,
                    n_flank VARCHAR(255),
                    c_flank VARCHAR(255),
                    sample_name VARCHAR(255) NOT NULL,
                    affinity FLOAT NOT NULL,
                    best_allele FLOAT NOT NULL,
                    affinity_percentile FLOAT NOT NULL,
                    processing_score FLOAT NOT NULL,
                    presentation_score FLOAT NOT NULL,
                    presentation_percentile FLOAT NOT NULL
                )
            """)

            # Commit the changes
            conn.commit()

            # Close the communication with the PostgreSQL
            cur.close()
            conn.close()

            logging.info('Database tables created successfully.')
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(e)


    def add_results(self,pipelinedata):
        """
        Add prediction data to the database.
        """
        pass