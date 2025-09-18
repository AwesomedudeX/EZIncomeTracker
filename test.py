import py7zr as zip

print("Extracting...")
zip.SevenZipFile("C:/Users/techn/Desktop/STALKER/Compressed Files/RTac GAMMA Large Mods.7z", "r").extractall("C:/Users/techn/Desktop/STALKER/Compressed Files")
print("Done!")