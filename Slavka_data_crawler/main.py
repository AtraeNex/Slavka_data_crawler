import httpx
from selectolax.parser import HTMLParser
import time

#sukuriam f-ja isgauti html, kadangi noresim praplesti koda, sudeti daugiau f-ju
def get_html(baseurl, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }
    # str(page), kad galima butu sujungti puslapi ir URL; follow_redirects = True, kad gavus 301 error, sektume re-direct
    response = httpx.get(baseurl + str(page), headers=headers, follow_redirects=True)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"Gautas klaidos kodas {exc.response.status_code}, bandant pasiekti {exc.request.url!r}. Puslapiu limitas pasiektas.")
        return False #jeigu gausim klaida, nutrauksim 'for' loop'a main() funkcijoje
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
    #Parenkam(patikslinam) prekiu selektoriu
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")

    #Istraukiam visus produktus is vieno/pasirinkto puslapio
    for product in products:
        #Sukuriam dictionary informacijai atvaizduoti
        item = {
            "name": extract_text(product, ".Xpx0MUGhB7jSm5UvK2EY"),
            "price": extract_text(product, "span[data-ui=sale-price]"),
            "savings": extract_text(product, "div[data-ui=savings-percent-variant2]")
        }
        #naudojam yield vietoj list'o append, tam, kad netureti list'o list'u, produktu dictionaries
        yield item

#pagrindine f-ja, kuri viska paleidzia
def main():
    baseurl = "https://www.rei.com/c/camping-and-hiking?page="
    #lupinam per puslapius, ir istraukiam produktus
    for x in range(130,140):
        print(f"Surenkam info is puslapio: {x}")
        html = get_html(baseurl, x) #html failas = get_html f-jai
        if html is False:
            break
        data = parse_page(html)
        for item in data:
            print(item)
        #imetam uzdelsima 1sec, kad nesiusti per daug requestu vienu metu
        time.sleep(1)

#jeigu paleidziam si main.py tiesiogiai - iskvies sia funkcija, o jeigu importuosim main.py, tuomet - ne
if __name__ == "__main__":
    main()
