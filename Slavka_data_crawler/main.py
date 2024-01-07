import httpx
from selectolax.parser import HTMLParser
import time
from urllib.parse import urljoin
from dataclasses import dataclass, asdict, fields
import json
import csv


#nauja dataclass, info rusiavimui
@dataclass
class Item:
    #str | None, nes produktui gali buti nepriskirta kazkuri reiksme
    name: str | None
    item_number: str | None
    price: str | None
    rating: float |None


#sukuriam f-ja isgauti html, kadangi noresim praplesti koda, sudeti daugiau f-ju
def get_html(url, **kwargs): #kad neperrasinet f-jos, jeigu url turi puslapi, pvietoj puslapiu paduosim keyword argumentus
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }

    #print(kwargs.get("page"))-> patikrinom, ar veikia;
    #naudojam taip, nes naudojant ["page"], jeigu kas nepavyks - ismes errora
    if kwargs.get("page"):
        #str(page), kad galima butu sujungti puslapi ir URL; follow_redirects = True, kad gavus 301 error, sektume re-direct
        #str(page)->str(kwargs.get("page"))
        response = httpx.get(url + str(kwargs.get("page")), headers=headers, follow_redirects=True)
    else:
        response = httpx.get(url, headers=headers, follow_redirects=True)

    #HTTP Error handling'as
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"Gautas klaidos kodas {exc.response.status_code}, bandant pasiekti {exc.request.url!r}. Puslapiu limitas pasiektas.")
        return False #jeigu gausim puslapio statuso klaida, nutrauksim 'for' loop'a main() f-joje
    html = HTMLParser(response.text)
    return html

#f-ja pagrindinio puslapio produktu URL surinkimui
def parse_search_page(html: HTMLParser):
    #Parenkam(patikslinam) prekiu selektoriu
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")
    #surenkam kiekvieno atskiro produkto URL is pagr. paieskos puslapio, kad galetume pasiekti daugiau info apie produkta is jo URL
    for product in products:
        yield urljoin("https://www.rei.com", product.css_first("a").attributes["href"])

#f-ja paciu produktu ULR, surenkam pavadinima, produkto numeri, kaina, reitinga
def parse_item_page(html):
    new_item = Item(
        name=extract_text(html, "h1#product-page-title"),
        item_number=extract_text(html, "span#product-item-number"),
        price=extract_text(html, "span#buy-box-product-price"),
        rating=extract_text(html, "span.cdr-rating__number_13-5-3")
    )
    return asdict(new_item)

#Sukuriam funkcija, kuri parsins/extractins texta is html puslapio pagal css selektoriu
def extract_text(html, selector):
    #grazins "None", jeigu neras prasomos grazinti informacijos, t.y. pavadinimo, produkto numerio, kainos arba reitingo
    try:
        #grazinam sutvarkyta teksta
        text = html.css_first(selector).text()
        return clean_data(text)
    except AttributeError:  #nereikia 'as err', nes returninam None
        return None

#eksportuojam produktu sarasa i json
def export_to_json(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("saved to json")

#eksportuojam produktu sarasa i csv
def export_to_csv(products):
    #sukuriam laukeliu pavadinimus, naudojant dataclass fields
    field_names = [field.name for field in fields(Item)]
    #surasomi produktai i csv faila
    with open ("products.csv", "w") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerows(products)
    print("saved to csv")

#f-ja isvalyti nereikalingus/papildomus simbolius is gautos informacijos produktu sarase
def clean_data(value):
    chars_to_remove = ["$", "Item", "#"]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    #nepriklausomai nuo to, radom kokius simbolius pasalint, ar ne - grazinam reiksmes be nereikalingu tarpu
    return value.strip()

#f-ja irasyti papildomus produktus i csv faila
#def append_to_csv(products):
    #sukuriam laukeliu pavadinimus, naudojant dataclass fields
#    field_names = [field.name for field in fields(Item)]
    #pridedami papildomi produktai, neperrasat pagr. csv failo
#    with open ("append.csv", "a") as f:
#        writer = csv.DictWriter(f, field_names)
#        writer.writerows(products)

#pagrindine f-ja, kuri viska paleidzia
def main():
    products = []
    baseurl = "https://www.rei.com/c/camping-and-hiking?page="
    #lupinam per puslapius, ir istraukiam produktus
    for x in range(134,136):
        print(f"Surenkam info is puslapio: {x}")
        html = get_html(baseurl, page=x) #html failas = get_html f-jai; x -> page=x, nes tai tapo keyword argumentu get_html f-joje

        if html is False:
            break
        product_urls = parse_search_page(html)
        for url in product_urls:
            print(url)
            html = get_html(url)

            products.append(parse_item_page(html)) #-> nebereikia, kai turim append_to_csv f-ja
            #append_to_csv(parse_item_page(html)) #kiekviena karta grazins dictionary
            #imetam uzdelsima 0.1sec, kad nesiusti per daug requestu vienu metu
            #ikeliam uzdelsima i produkto loop'a, kad uzdelsimas butu kiekviename PRODUKTO puslapyje, o ne PRODUKTU puslapyje
            time.sleep(0.1)

    export_to_json(products)
    export_to_csv(products)

#jeigu paleidziam si main.py tiesiogiai - iskvies sia funkcija, o jeigu importuosim main.py, tuomet - ne
if __name__ == "__main__":
    main()
