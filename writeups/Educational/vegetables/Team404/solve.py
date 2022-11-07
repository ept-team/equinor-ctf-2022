
import pickle
import base64
import fruits

class Rick:
    def __reduce__(self):
        return( fruits.Rick, () )

print( base64.b64encode( pickle.dumps(Rick()) ) )
