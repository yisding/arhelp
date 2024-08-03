from PIL import Image

# transparent RGBA
rgba = (0, 0, 0, 0)

transparent_image = Image.new('RGBA', [512, 512], rgba)

# Save the transparent image
transparent_image_path = 'transparent.png'
transparent_image.save(transparent_image_path)