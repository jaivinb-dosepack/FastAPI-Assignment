from fastapi import Request
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware


#get logger
logger = logging.getLogger()

#create formatter

formatter = logging.Formatter(fmt= '%(asctime)s %(message)s' )


# Handler


# stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')


# set Format

file_handler.setFormatter(formatter)


# add handler to the logger

logger.handlers = [file_handler]

logger.setLevel(logging.INFO)


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request ,call_next):
        start_time = datetime.now()
        
        response =  await call_next(request)
        process_time = (datetime.now()- start_time).total_seconds()
        log_dict = {
            'url':request.url.path,
            'method':request.method,
            'client_IP':request.client.host,
            'response_time':process_time
        }

        logger.info(log_dict)


        return response
