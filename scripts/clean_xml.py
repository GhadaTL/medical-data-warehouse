import os
from lxml import etree

SOURCE = "data/raw/pubmed_xml"
VALID = "data/processed"
REJECTED = "data/rejected"

os.makedirs(VALID, exist_ok=True)
os.makedirs(REJECTED, exist_ok=True)

valid_count = 0
rejected_count = 0

for filename in os.listdir(SOURCE):

    if not filename.endswith(".xml"):
        continue

    path = os.path.join(SOURCE, filename)

    try:
        parser = etree.XMLParser(recover=False)
        tree = etree.parse(path, parser)

        article = tree.find(".//PubmedArticle")

        if article is None:
            raise ValueError("Article absent")

        pmid = article.findtext(".//PMID")

        if not pmid:
            raise ValueError("PMID absent")

        valid_count += 1

    except Exception as e:

        print(filename, ":", e)
        rejected_count += 1

print("Fichiers valides :", valid_count)
print("Fichiers rejetés :", rejected_count)