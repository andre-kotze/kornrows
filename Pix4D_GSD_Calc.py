# Sw	= the sensor width of the camera (millimeters)
# FR	= the focal length of the camera (millimeters)
# H		= the flight height (meters)
# imW	= the image width (pixels)
# imH	= the image height (pixels)
# GSD	= Ground Sampling Distance (centimeters/pixel)
# Dw	= width of single image footprint on the ground (meters)
# DH	= height of single image footprint on the ground (meters)

Sw	= 7.6
FR	= 47.6
H	= 22.86
imW	= 5184
imH	= 3888


GSD	= (Sw*H*100)/(FR*imW)
Dw	= (imW*GSD)/100
DH	= (imH*GSD)/100

Area = Dw*DH