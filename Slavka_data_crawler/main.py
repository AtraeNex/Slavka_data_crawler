import httpx
from selectolax.parser import HTMLParser

#sukuriam f-ja isgauti html, kadangi noresim praplesti koda, sudeti daugiau f-ju
def get_html():
    url = "https://www.rei.com/c/camping-and-hiking"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }

    response = httpx.get(url, headers=headers)
    html = HTMLParser(response.text)
    return html

#Sukuriam funkcija, kur grazins "None", jeigu neras "Sale-Price"
#kadangi nevisos kainos surasytos su nuolaida. Reikia ismesti klaida, kai kaina randama be nuolaidos
def extract_text(html, selector):
    try:
        return html.css_first(selector).text()
    except AttributeError:  #nereikia 'as err', nes returninam None
        return None

#sukuriam f-ja parsinti informacijai is puslapio
def parse_page(html):
    #Pasirenkam li.VcGDfKKy_dvNbxUqm29K, kadangi
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")

    #Istraukiam visus produktus is vieno/pasirinkto puslapio
    for product in products:
        #dictionary informacijai atvaizduoti
        item = {
            "name": extract_text(product, ".Xpx0MUGhB7jSm5UvK2EY"),
            "price": extract_text(product, "span[data-ui=sale-price]"),
            "savings": extract_text(product, "div[data-ui=savings-percent-variant2]")
        }
        print(item)

#pagrindine f-ja, kuri viska paleidzia
def main():
    html = get_html() #html failas = get_html f-jai
    parse_page(html)

#jeigu paleidziam si main.py tiesiogiai iskvies sia funkcija, o jeigu importuosim - ne
if __name__ == "__main__":
    main()
