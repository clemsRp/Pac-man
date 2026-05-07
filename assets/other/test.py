from PIL import Image

# Charger le GIF
gif = Image.open("ghost.gif")

frames = []

# Extraire toutes les frames
try:
    index = 0
    while True:
        frame = gif.copy().convert("RGBA")

        # Sauvegarde temporaire
        frame.save("temp_frame{}.png".format(index))
        index += 1

        gif.seek(gif.tell() + 1)

except EOFError:
    pass
