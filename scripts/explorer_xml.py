import os
from lxml import etree

DATA_PATH = "data/raw/pubmed_xml"

files = [
    f for f in os.listdir(DATA_PATH)
    if f.endswith(".xml")
]

print("Nombre de fichiers :", len(files))

# Lire un premier document
file_path = os.path.join(DATA_PATH, files[0])

tree = etree.parse(file_path)
root = tree.getroot()

print("Racine :", root.tag)

# Afficher les principales balises
for element in root.iter():
    print(element.tag, element.text)