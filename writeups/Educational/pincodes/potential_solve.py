
from tensorflow import keras 
import numpy as np 

# Should probably install tensorflow for this to work, you can skip GPU as any CPU should do

my_model = keras.models.load_model('model.h5')

print(my_model.get_config())
print(my_model.summary())

# I think I've read somewhere about something called one-hot encoding. Might be worthwhile checking out

# Perhaps you can find some interesting functions here?
print(dir(my_model))
