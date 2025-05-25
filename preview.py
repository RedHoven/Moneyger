from PIL import Image

# Load the 4 images
images = [
    Image.open("preview/welcome.png").convert("RGBA"),
    Image.open("preview/transaction.png").convert("RGBA"),
    Image.open("preview/modify-text.png").convert("RGBA"),
    Image.open("preview/stats.png").convert("RGBA")
]

# Resize all images to the same size (optional but recommended)
size = (822, 567)
images = [img.resize(size) for img in images]

# Create a blank canvas for a 2x2 grid
grid_img = Image.new("RGBA", (size[0]*2, size[1]*2), (0, 0, 0, 0))

# Paste the images
grid_img.paste(images[0], (0, 0), mask=images[0])
grid_img.paste(images[1], (size[0], 0), mask=images[1])
grid_img.paste(images[2], (0, size[1]), mask=images[2])
grid_img.paste(images[3], (size[0], size[1]), mask=images[3])

# Save the result
grid_img.save("preview/preview-grid.png")
