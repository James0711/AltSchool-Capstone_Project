from fastapi import Request
from app.logger import logger
import time
import logging

# Configure logger to use a standard logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def log_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process the request and get the response
    response = await call_next(request)
    
    # Calculate the processing time
    elapsed_time = time.time() - start_time
    
    # Create a log dictionary with the request and response details
    log_data = {
        'url': str(request.url),
        'method': request.method,
        'status_code': response.status_code,
        'process_time': round(elapsed_time * 1000, 2)  # Convert to milliseconds
    }
    
    # Log the information with the logger
    logger.info('Request Info: %s', log_data, extra=log_data)
    
    return response
