import cv2
import numpy as np
import matplotlib
import base64
import re
import socket
import nclib
import matplotlib.colors as mcolors

def get_shape_location( image_data, shape, color ):
    nparr = np.frombuffer(image_data, np.uint8)
    # reading image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # converting image into grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # setting threshold of gray image, fairly easy when background is black
    _, threshold = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
    # find contours of shapes
    # this creates a lot of points along the edges of the shape
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    i = 0    
    for contour in contours:
        # approximate the shape
        # this will reduce the number of contour points to only contain corners (circle will still have many  points though :P )
        approx = cv2.approxPolyDP(
            contour, 0.01 * cv2.arcLength(contour, True), True)
    
        # for the shape we are looking for, we'll check if the current shape has the correct amount of corners
        if( 'triangle' == shape ):
            if( len(approx) == 3 ) : # 3 corners
                #print( "triangle found" )
                pass
            else: # skip the rest and look at the next shape
                continue    
    
        elif( 'rectangle' == shape ):
            if(  len(approx) == 4 ): # 4 corners
                #print( "rectangle found" )
                pass
            else:
                continue  

        elif( 'hexagon' == shape ):
            if( len(approx) == 6 ): # 6 corners
                #print( "hexagon found" )
                pass
            else:
                continue  
    
        elif( 'circle' == shape ):
            if( len(approx) > 6 ):
                #print( "circle found" )
                pass
            else:
                continue  
        
        # finding height and width of image
        height, width, channels = img.shape

        # finding center point of shape
        # this is used for 2 things:
        #       This should be a good place to get the color of the shape
        #       This makes it easy to figure out if the shape is located ne/nw/se/sw as the image is split into 4 equal parts with one shape in each part
        M = cv2.moments(contour)
        if M['m00'] != 0.0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])

        # If we're looking for a specific color for the shape
        if( color ):
            #print( color )
            # get RGB values from a string e.g. "brown"
            rgb_wanted = matplotlib.colors.to_rgb( color )
            # allow +- 5 for each channel (this could be done in numpy to beautify)
            rgb_wanted_min = [
                ( rgb_wanted[0] * 255 ) - 5,
                ( rgb_wanted[1] * 255 ) - 5,
                ( rgb_wanted[2] * 255 ) - 5
            ]
            rgb_wanted_max = [
                ( rgb_wanted[0] * 255 ) + 5,
                ( rgb_wanted[1] * 255 ) + 5,
                ( rgb_wanted[2] * 255 ) + 5
            ]
            
            # OBS! cv2 using BGR, and also when getting the color of a pixel the y and x are reversed!
            shape_color = img[ y, x ]
            #print( "BGR", shape_color )
            if( 
                shape_color[2] >= rgb_wanted_min[0] and shape_color[2] <= rgb_wanted_max[0] and 
                shape_color[1] >= rgb_wanted_min[1] and shape_color[1] <= rgb_wanted_max[1] and
                shape_color[0] >= rgb_wanted_min[2] and shape_color[0] <= rgb_wanted_max[2]
            ):
                #print( "Color found!")
                pass
            else: # if this was not the correct color, we move on to the next shape
                continue

        # At this point we have the correct shape and color, so just checking which part of the image it is in
        if( x < width/2 and y < height/2 ):
            # top left / nw
            placement = "nw"
        elif( x > width/2 and y < height/2 ):
            # top right / ne
            placement = "ne"
        elif( x < width/2 and y > height/2 ):
            # bottom left / sw
            placement = "sw"
        elif( x > width/2 and y > height/2 ):
            # bottom left / se
            placement = "se"
        return placement

# regex to get color and shape requested
questionRe = re.compile( "([A-Za-z]+)? *(rectangle|circle|hexagon|triangle)")

# split a server response into lines and then get the request for color, shape and the base64 dencoded image
def get_decoded_response( response ):
    data = response.decode( 'utf-8' ).splitlines()
    # just getting different number of lines as we suddenly get "correct!" or "LEVEL 2!" and so on from the server ><
    for i in range( len( data ) ):
        match = questionRe.search( data[i] )
        if( match ):
            color = None
            if( match[1] in mcolors.CSS4_COLORS ):
                color = match[1]
            return color, match[2], base64.b64decode( data[i+1] )

def connect():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #clientSocket.connect(("io.ept.gg",30047)) # Let's play
    clientSocket.connect(("io.ept.gg",30049)) # Let's play harder
    nc = nclib.netcat.Netcat(sock=clientSocket, verbose=False)

    response = nc.recv()
    print( response )
    print( "Sending: Yes" )
    nc.send( "Yes\n" )

    counter = 1
    while( True ):
        print( f"This is image #{counter}" )
        response = nc.recv_all(timeout=2)
        color, shape, imageData = get_decoded_response(response)
        print( f"Asking for location of: {shape} :: {color}" )

        shape_location = get_shape_location( imageData, shape, color )

        print( "Sending: ", shape_location )
        nc.send( f"{shape_location}\n" )
        counter += 1

connect()