import httpx
from selectolax.parser import HTMLParser


url = "https://www.rei.com/c/camping-and-hiking"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"}

response = httpx.get(url, headers=headers)
html = HTMLParser(response.text)

#Sukuriam funkcija, kur grazins "None", jeigu neras "Sale-Price"
#kadangi nevisos kainos surasytos su nuolaida. Reikia ismesti klaida, kai kaina randama be nuolaidos
def extract_text(html, selector):
    try:
        return html.css_first(selector).text()
    except AttributeError:  #nereikia 'as err', nes returninam None
        return None

#Pasirenkam li.VcGDfKKy_dvNbxUqm29K, kadangi
products = html.css("li.VcGDfKKy_dvNbxUqm29K")

#Istraukiam visus produktus is vieno/pasirinkto puslapio
for product in products:
    #dictionary informacijai atvaizduoti
    item = {
        "name": extract_text(product, ".Xpx0MUGhB7jSm5UvK2EY"),
        "price": extract_text(product, "span[data-ui=sale-price]")
    }
    print(item)