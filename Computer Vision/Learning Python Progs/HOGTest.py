#importing required libraries
from skimage.io import imread
from skimage.transform import resize
from skimage.feature import hog
from skimage import exposure
import matplotlib.pyplot as plt

# reading the image
img = imread('image_testing/Hand_0000058.jpg')
img2 = imread('image_testing/Face.jpg')
img3 = imread('image_testing/Book.jpg')
#plt.axis("off")
#plt.imshow(img)
print(img.shape)

# resizing image
resized_img2 = resize(img2, (1200, 1600))
resized_img3 = resize(img3, (1200, 1600))
#plt.axis("off")
#plt.imshow(resized_img)
#print(resized_img.shape)

#creating hog features
fd, hog_image = hog(img, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                	cells_per_block=(2, 2), 
                    visualize=True, channel_axis = -1)
plt.axis("off")
plt.imshow(hog_image, cmap="gray")
plt.savefig("image_testing/handHOG.png")

fd, hog_image = hog(resized_img2, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                	cells_per_block=(2, 2), 
                    visualize=True, channel_axis = -1)
plt.axis("off")
plt.imshow(hog_image, cmap="gray")
plt.savefig("image_testing/faceHOG.png")


fd, hog_image = hog(resized_img3, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                	cells_per_block=(2, 2), 
                    visualize=True, channel_axis = -1)
plt.axis("off")
plt.imshow(hog_image, cmap="gray")
plt.savefig("image_testing/bookHOG.png")
print("done")