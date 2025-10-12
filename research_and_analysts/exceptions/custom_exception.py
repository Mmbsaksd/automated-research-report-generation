import sys
import traceback
from typing import Optional, cast

class ResearchAnalystException(Exception):
    def __init__(self, error_message, error_details:Optional[object]=None):
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)
        
        exc_type, exc_value, exc_tb = None

        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details,"exc_info"):
                exc_info_obj = cast(sys,error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details,BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details,error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()