import psycopg2
import logging
import csv

# Make sure the database name is LOWERCASE!!


class DatabaseOperations:
    '''
    Class for creating a neolizard_db PostgreSQL database and adding data from the pipeline and prediction results.
    '''
    def __init__(self, username, password, host, name, pipeline_data, path_handler):
        self.username = username
        self.password = password
        self.host = host
        self.name = name
        self.pipeline_data = pipeline_data
        self.path_handler = path_handler
        self.data = []

    def createdb(self):
        """
        Create the database and subsequently the tables.
        """
        try:
            # Connect to the PostgreSQL server to create the database
            conn = psycopg2.connect(
                database="postgres",
                user=self.username,
                password=self.password,
                host=self.host,
            )
            conn.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
            )  # Set autocommit mode to create the database

            # Create a cursor
            cur = conn.cursor()

            # Create the database if it doesn't exist
            cur.execute(f"CREATE DATABASE {self.name}")

            # Close the communication with the PostgreSQL
            cur.close()
            conn.close()

            logging.info(f'Database "{self.name}" created successfully.')
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(e)
            raise

        # Call the method to create the database tables
        self.create_tables()

    def create_tables(self):
        """
        Create the database tables.
        """
        try:
            # Connect to the PostgreSQL server
            conn = psycopg2.connect(
                database=self.name,
                user=self.username,
                password=self.password,
                host=self.host,
            )

            # Create a cursor
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE Sample (
                    sample_id SERIAL PRIMARY KEY,
                    sample_name VARCHAR(255)
                )
            """
            )

            # Mutation table
            cur.execute(
                """
                CREATE TABLE Mutation (
                    mutation_id SERIAL PRIMARY KEY,
                    sample_id INTEGER REFERENCES Sample(sample_id),
                    mutation_name VARCHAR(255)
                )
            """
            )

            # Transcript table
            cur.execute(
                """
                CREATE TABLE Transcript (
                    transcript_id SERIAL PRIMARY KEY,
                    mutation_id INTEGER REFERENCES Mutation(mutation_id),
                    transcript_name VARCHAR(255)
                )
            """
            )

            # Peptide table
            cur.execute(
                """
                CREATE TABLE Peptide (
                    peptide_id SERIAL PRIMARY KEY,
                    transcript_id INTEGER REFERENCES Transcript(transcript_id),
                    pos INTEGER NOT NULL,
                    peptide VARCHAR(255) NOT NULL,
                    n_flank VARCHAR(255),
                    c_flank VARCHAR(255),
                    affinity FLOAT NOT NULL,
                    best_allele VARCHAR(255) NOT NULL,
                    affinity_percentile FLOAT NOT NULL,
                    processing_score FLOAT NOT NULL,
                    presentation_score FLOAT NOT NULL,
                    presentation_percentile FLOAT NOT NULL
                )
            """
            )

            # Commit the changes
            conn.commit()

            # Close the communication with the PostgreSQL
            cur.close()
            conn.close()

            logging.info("Database tables created successfully.")
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(e)
            raise

    def connect(self):
        """
        Connect to the PostgreSQL database server
        """
        conn = None
        try:
            # Connect to the PostgreSQL server
            logging.info("Connecting to the PostgreSQL server...")
            conn = psycopg2.connect(
                database="postgres",
                user=self.username,
                password=self.password,
                host=self.host,
            )

            # Create a cursor
            cur = conn.cursor()

            # Check if the specified database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.name,))
            db_exists = cur.fetchone()

            if not db_exists:
                logging.info(
                    f'Database "{self.name}" does not exist. Attempting to create it...'
                )
                # Close the current connection to the default 'postgres' database
                cur.close()
                conn.close()

                # Create the database using createdb method
                self.createdb()

            # Connect to the specified database
            logging.info(f'Connecting to the PostgreSQL database "{self.name}"...')
            conn = psycopg2.connect(
                database=self.name,
                user=self.username,
                password=self.password,
                host=self.host,
            )

            # Create a new cursor for the specified database
            cur = conn.cursor()

            # get version to ensure it works
            logging.info("PostgreSQL database version:")
            cur.execute("SELECT version()")

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            logging.info(db_version)

            # close the communication with the PostgreSQL
            cur.close()
            conn.close()
            logging.info(
                f'Successfully connected to the PostgreSQL database "{self.name}"'
            )
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(e)
            raise
        finally:
            if conn is not None:
                conn.close()
                logging.info("Database connection closed.")

    def insert_initial_data(self):
        """
        Add initial data to the database.
        """

        try:
            # Connect to the PostgreSQL server and database
            conn = psycopg2.connect(
                database=self.name,
                user=self.username,
                password=self.password,
                host=self.host,
            )
            conn.autocommit = True

            # Create a cursor
            cur = conn.cursor()

            # Insert data into the Sample table
            for sample_name in list(self.pipeline_data.sample_mutations.keys()):
                # Check if the sample with the same name already exists
                cur.execute(
                    "SELECT sample_id FROM Sample WHERE sample_name = %s",
                    (sample_name,),
                )
                existing_sample_id = cur.fetchone()

                if existing_sample_id is not None:
                    # Sample with the same name already exists, skip insertion
                    logging.warning(
                        f"Sample with name '{sample_name}' already exists in the Sample table. Skipping insertion."
                    )
                    continue

                # Insert the new sample
                cur.execute(
                    "INSERT INTO Sample (sample_name) VALUES (%s)",
                    (sample_name,),
                )

            # Insert data into the Mutation table and get mutation_id
            for (
                sample_name,
                mutation_names,
            ) in self.pipeline_data.sample_mutations.items():
                cur.execute(
                    "SELECT sample_id FROM Sample WHERE sample_name = %s",
                    (sample_name,),
                )
                sample_id = cur.fetchone()

                if sample_id is None:
                    logging.error(
                        f"Sample '{sample_name}' not found in the Sample table."
                    )
                    continue

                sample_id = sample_id[0]

                for mutation_name in mutation_names:
                    # Check if the mutation with the same sample_id and mutation_name already exists
                    cur.execute(
                        "SELECT mutation_id FROM Mutation WHERE sample_id = %s AND mutation_name = %s",
                        (sample_id, mutation_name),
                    )
                    existing_mutation_id = cur.fetchone()

                    if existing_mutation_id is not None:
                        # Mutation with the same sample_id and mutation_name already exists, skip insertion
                        logging.warning(
                            f"Mutation with name '{mutation_name}' and sample_id '{sample_id}' already exists in the Mutation table. Skipping insertion."
                        )
                        continue

                    # Insert the new mutation
                    cur.execute(
                        "INSERT INTO Mutation (sample_id, mutation_name) VALUES (%s, %s) RETURNING mutation_id",
                        (sample_id, mutation_name),
                    )
                    mutation_id = cur.fetchone()

                    if mutation_id is None:
                        logging.error(
                            f"Failed to insert Mutation '{mutation_name}' for Sample '{sample_name}'."
                        )
                        continue

                    mutation_id = mutation_id[0]

            # Commit the changes
            conn.commit()

            # Close the communication with the PostgreSQL
            cur.close()
            conn.close()

            logging.info("Data insertion into tables completed successfully.")
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(f"Error inserting data into tables: {e}")
            raise


    def read_predictions(self):
        """
        Read data from the predictions CSV file and insert it into the appropriate tables.
        """
        try:
            with open(self.path_handler.input_path, "r") as f:
                csvreader = csv.reader(f)
                header = next(csvreader)  # skip header

                # Create dictionaries to hold data for insertion
                peptide_data = (
                    {}
                )  # Dictionary for peptide data (sample_mutation_transcript -> [(peptide, affinity, presentation_score, ...)])

                # Loop through the rows in the CSV file
                for row in csvreader:
                    sample_mutation_transcript = row[0]
                    pos = int(row[1])
                    peptide = row[2]
                    n_flank = row[3]
                    c_flank = row[4]
                    affinity = float(row[6])
                    best_allele = row[7]
                    affinity_percentile = float(row[8])
                    processing_score = float(row[9])
                    presentation_score = float(row[10])
                    presentation_percentile = float(row[11])

                    # Check if the sample_mutation_transcript exists in the peptide_data dictionary
                    if sample_mutation_transcript not in peptide_data:
                        peptide_data[sample_mutation_transcript] = []
                    peptide_data[sample_mutation_transcript].append(
                        (
                            pos,
                            peptide,
                            n_flank,
                            c_flank,
                            affinity,
                            best_allele,
                            affinity_percentile,
                            processing_score,
                            presentation_score,
                            presentation_percentile,
                        )
                    )

            # Iterate through the dict and insert the data into the database
            for sample_mutation_transcript, peptide_list in peptide_data.items():
                sample, mutation, transcript = sample_mutation_transcript.split("_", 2)

                for peptide_data in peptide_list:
                    (
                        pos,
                        peptide,
                        n_flank,
                        c_flank,
                        affinity,
                        best_allele,
                        affinity_percentile,
                        processing_score,
                        presentation_score,
                        presentation_percentile,
                    ) = peptide_data
                    self.add_prediction_results(
                        sample,
                        mutation,
                        transcript,
                        pos,
                        peptide,
                        n_flank,
                        c_flank,
                        affinity,
                        best_allele,
                        affinity_percentile,
                        processing_score,
                        presentation_score,
                        presentation_percentile,
                    )

            # No need to separately call the insert_data_to_tables method, as we are inserting data directly above

        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(f"Error reading CSV file and inserting data into tables: {e}")
            raise

    def add_prediction_results(
        self,
        sample_name,
        mutation_name,
        transcript_name,
        pos,
        peptide,
        n_flank,
        c_flank,
        affinity,
        best_allele,
        affinity_percentile,
        processing_score,
        presentation_score,
        presentation_percentile,
    ):
        try:
            # Connect to the PostgreSQL server and database
            with psycopg2.connect(
                database=self.name,
                user=self.username,
                password=self.password,
                host=self.host,
            ) as conn:
                conn.autocommit = True
    
                # Create a cursor
                with conn.cursor() as cur:
                    # Get the sample_id from the Sample table based on the sample_name
                    cur.execute(
                        "SELECT sample_id FROM Sample WHERE sample_name = %s",
                        (sample_name,),
                    )
                    sample_id = cur.fetchone()
    
                    if sample_id is None:
                        # Sample with the provided sample_name does not exist
                        logging.warning(
                            f"Sample with name '{sample_name}' does not exist in the Sample table. Skipping peptide data insertion for {sample_name}_{mutation_name}_{transcript_name}."
                        )
                        return
    
                    sample_id = sample_id[0]
    
                    # Get the mutation_id from the Mutation table based on the mutation_name and sample_id
                    cur.execute(
                        "SELECT mutation_id FROM Mutation WHERE mutation_name = %s AND sample_id = %s",
                        (mutation_name, sample_id),
                    )
                    mutation_id = cur.fetchone()
    
                    if mutation_id is None:
                        # Mutation with the provided mutation_name and sample_id does not exist
                        logging.warning(
                            f"Mutation with name '{mutation_name}' and sample_id '{sample_id}' does not exist in the Mutation table. Skipping peptide data insertion for {sample_name}_{mutation_name}_{transcript_name}."
                        )
                        return
    
                    mutation_id = mutation_id[0]
    
                    # Check if the peptide already exists in the Peptide table for the given transcript
                    cur.execute(
                        """
                        SELECT peptide_id FROM Peptide
                        WHERE transcript_id IN (SELECT transcript_id FROM Transcript WHERE mutation_id = %s AND transcript_name = %s)
                        AND pos = %s AND peptide = %s AND affinity = %s
                        """,
                        (
                            mutation_id,
                            transcript_name,
                            pos,
                            peptide,
                            affinity,
                        ),
                    )
                    existing_peptide_id = cur.fetchone()
    
                    if existing_peptide_id is not None:
                        # Peptide with the same data already exists, handle it as needed (e.g., update or skip)
                        # For example, to update the existing peptide, you can use the UPDATE statement
                        # Here, I'll simply log a message and skip the insertion
                        logging.warning(
                            f"Peptide with the same data already exists in the Peptide table for {sample_name}_{mutation_name}_{transcript_name}. Skipping insertion."
                        )
                        return
    
                    # Insert data into the Transcript table
                    cur.execute(
                        """
                        INSERT INTO Transcript (
                            mutation_id,
                            transcript_name
                        )
                        VALUES (%s, %s)
                        """,
                        (mutation_id, transcript_name),
                    )
    
                    # Insert data into the Peptide table
                    cur.execute(
                        """
                        INSERT INTO Peptide (
                            transcript_id,
                            pos,
                            peptide,
                            n_flank,
                            c_flank,
                            affinity,
                            best_allele,
                            affinity_percentile,
                            processing_score,
                            presentation_score,
                            presentation_percentile
                        )
                        VALUES (
                            LASTVAL(),
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        RETURNING peptide_id
                    """,
                        (
                            pos,
                            peptide,
                            n_flank,
                            c_flank,
                            affinity,
                            best_allele,
                            affinity_percentile,
                            processing_score,
                            presentation_score,
                            presentation_percentile,
                        ),
                    )
    
                    peptide_id = cur.fetchone()[0]
    
                logging.info(
                    f"Peptide data (ID: {peptide_id}) for {sample_name}_{mutation_name}_{transcript_name} added to the database."
                )
        except (Exception, psycopg2.DatabaseError) as e:
            logging.error(f"Error adding peptide data to the database: {e}")
            raise


    def run_add_data_pipeline(self):
        '''
        Run the full pipeline.
        '''
        try:
            self.connect()
            self.insert_initial_data()
            self.read_predictions()
        except psycopg2.DatabaseError as e:
            logging.error(f"Database error: {e}")
        except Exception as e:
            logging.error(f"Error in the data pipeline: {e}")
