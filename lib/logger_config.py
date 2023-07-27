import logging

def configure_logger(logfile):
    '''
    Root logger.
    '''

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s:%(name)s] %(message)s')

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
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

    # Create a formatter with the package name
    formatter = logging.Formatter('%(asctime)s [%(levelname)s:%(name)s] %(message)s')

    # Create a file handler
    handler = logging.FileHandler(logfile, mode='a')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

