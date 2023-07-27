import logging

def configure_logger(logfile):
    '''
    Root logger.
    '''

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create a file handler
    file_handler = logging.FileHandler(logfile,mode='a')  
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def configure_lib_logger(logfile):
    '''
    Logger for lib module.
    '''
    logger = logging.getLogger('lib')
    logger.setLevel(logging.DEBUG)
    # Set the formatter to the same as the root logger
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler = logging.FileHandler(logfile, mode='a')  # Use the same file handler as the root logger
    handler.setFormatter(formatter)
    logger.addHandler(handler)
