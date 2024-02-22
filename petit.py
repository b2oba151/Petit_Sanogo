from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import json
import time
import os
import requests
import wget
from youtube_dl import YoutubeDL
from tqdm import tqdm

def configurer_driver_firefox_avec_profil(chemin_profil):
    options = webdriver.FirefoxOptions()
    options.profile = chemin_profil
    driver = webdriver.Firefox(options=options)
    return driver

def open_link(url, driver=None, custom_timeout=50):
    if driver is None:
        driver = configurer_driver_firefox_avec_profil(r"/home/b2oba/.mozilla/firefox/mpdj4ica.dev-edition-default")

    try:
        driver.set_page_load_timeout(custom_timeout)
        driver.get(url)
        return driver
    except TimeoutException:
        print(f"Le chargement de la page a dépassé le délai de {custom_timeout} secondes. Vérifiez le lien et réessayez.")

def ecrire_dans_fichier(texte, mode='a',filename="output.txt"):
    with open(filename, mode, encoding="utf-8") as fichier:
        fichier.write(texte)

def download_video_requests(url, destination_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

def download_video_wget(url, destination_path):
    wget.download(url, out=destination_path)

def download_video_ytdl(url, destination_path):
    ydl_opts = {'outtmpl': destination_path}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
def to_snake_case(input_string):
    input_string = input_string.replace(" ", "_")
    input_string = input_string.lower()
    return input_string


datas=[]
ecrire_dans_fichier("\n",'w')

# infos_formations = {}
# id_formations = 1

# links=("https://www.linkedin.com/learning/les-fondements-de-la-programmation-19374003?contextUrn=urn%3Ali%3AlyndaLearningPath%3A57f2308692015a98782809c6",
# "https://www.linkedin.com/learning/les-fondements-de-la-programmation-les-bases-de-donnees-8977696?contextUrn=urn%3Ali%3AlyndaLearningPath%3A57f2308692015a98782809c6")


# infos_formations = {}
# id_formations = 1

# driver = open_link("https://www.linkedin.com/learning/paths/devenir-developpeur-developpeuse-web-full-stack")

# WebDriverWait(driver, 50).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, "h1._displayText_1mzada._default_1i6ulk"))
# )

# liste_divs = driver.find_elements(By.CSS_SELECTOR, "div.lls-card-detail-card__main")

# for div in liste_divs:
#     lien_formation = div.find_element(By.CSS_SELECTOR, "a")
#     nom_formation = div.find_element(By.CSS_SELECTOR, "span.lls-card-headline")
#     image_formation = div.find_element(By.CSS_SELECTOR, "div.lls-card-entity-thumbnails__image img.evi-image")

#     infos_formations[id_formations] = {
#         "nom_formation": nom_formation.text,
#         "image_formation": image_formation.get_attribute("src"),
#         "lien_formation": lien_formation.get_attribute("href")
#     }
#     id_formations += 1

# driver.quit()


with open('f.json', 'r') as fichier:
    donnees = json.load(fichier)

# with open('f.json', 'w', encoding='utf-8') as json_file:
#     json.dump(infos_formations, json_file, ensure_ascii=False, indent=2)

for id, infos in tqdm(donnees.items(), desc="Traitement des formations"):
    driver=open_link(infos["lien_formation"])
    WebDriverWait(driver, 50).until( EC.presence_of_element_located((By.CSS_SELECTOR, "a.ember-view.instructor__link>div.instructor__name")))
    instructeur_name=driver.find_element(By.CSS_SELECTOR, "a.ember-view.instructor__link>div.instructor__name")
    sections=driver.find_elements(By.CSS_SELECTOR, "section.classroom-toc-section")
    instructeur_name=driver.find_element(By.CSS_SELECTOR, "a.ember-view.instructor__link>div.instructor__name").text.strip().replace('\n', ' ')
    try:
        instructeur_headline=driver.find_element(By.CSS_SELECTOR, "a.ember-view.instructor__link>div.instructor__headline").text.strip().replace('\n', ' ')
        duree_Total=driver.find_element(By.CSS_SELECTOR, "div.classroom-workspace-overview__header ul li:nth-of-type(1)").text.strip().replace('\n', ' ')
        niveau=driver.find_element(By.CSS_SELECTOR, "div.classroom-workspace-overview__header ul li:nth-of-type(2)").text.strip().replace('\n', ' ')
        upload=driver.find_element(By.CSS_SELECTOR, "div.classroom-workspace-overview__header ul li:nth-of-type(3)").text.strip().replace('\n', ' ')
    except Exception as e:
        instructeur_headline=""
        duree_Total=""
        niveau=""
        upload=""
        #print(f"Exception: {e}")
        pass
    ecrire_dans_fichier(f" \n######### {id} ###########\nNom Formation : {infos['nom_formation']}\nLien Formation : {infos['lien_formation']}\nImage Formation : {infos['image_formation']}\nNom Formateur : {instructeur_name}\nDescription Formateur : {instructeur_headline}\nDurée Total : {duree_Total}\nNiveau : {niveau}\nDate Upload : {upload}\n")

    sections_boutons=[]
    sections_lis=[]
    resultats = []
    i=1
    for section in tqdm(sections, desc="Traitement des sections"):
        section = driver.find_element(By.CSS_SELECTOR, f"section.classroom-toc-section:nth-of-type({i})")
        video_section_name = section.find_element(By.CSS_SELECTOR, "span.classroom-toc-section__toggle-title._bodyText_1e5nen._default_1i6ulk._sizeSmall_1e5nen._default_1i6ulk._weightBold_1e5nen").text
        btn = section.find_element(By.CSS_SELECTOR, "button.classroom-toc-section__toggle")
        btn_aria_expand=btn.get_attribute("aria-expanded")
        btn_span =btn.find_element(By.CSS_SELECTOR, "span.classroom-toc-section__toggle-state")
        ecrire_dans_fichier(f" \n================ {video_section_name} ================\n")

        if(btn_aria_expand == "false"):
            btn_span.click()
            #print("click effecter")
            
        
        sections_lis = section.find_elements(By.CSS_SELECTOR, " ul li")
        z=1
        for li in sections_lis:
            try:
                li.click()
                time.sleep(5)
                WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".classroom-toc-item__title"))
                )
                titre = li.find_element(By.CSS_SELECTOR, ".classroom-toc-item__title").text.strip().replace('\n', ' ')
                duree = li.find_element(By.CSS_SELECTOR, "._sizeXSmall_1e5nen").text.strip().replace('\n', ' ')
                video_link=driver.find_element(By.CSS_SELECTOR, "video.vjs-tech").get_attribute('src')
                resultat = {"Titre": str(z) + " " + titre, "Durée": duree, "Chapitre": video_section_name, "Lien_video": video_link}
                resultats.append(resultat)
                ecrire_dans_fichier(f"Titre : {str(z) + " " + titre}\nDurée : {duree} \nLien video: {video_link}\n\n")
            except StaleElementReferenceException as e:
                #print(f"StaleElementReferenceException")
                pass
            except TimeoutException as e:
                #print(f"TimeoutException")
                pass
            except Exception as e:
                #print(f"Exception")
                pass
            z += 1
        ecrire_dans_fichier(f"**********************************************************\n")
        i +=1
    driver.quit()

    info_generales ={ 
                        "Infos_Generales": {
                            "Nom_Formation" : infos['nom_formation'], 
                            "Lien_Formation": infos['lien_formation'], 
                            "Image_Formation": infos['image_formation'], 
                            "Instructeur": instructeur_name, 
                            "Duree_Total": duree_Total, 
                            "Niveau": niveau, 
                            "Upload": upload 
                        },
                        "resultats":resultats
                        }
    datas.append(info_generales)
    
    with open('output.json', 'a', encoding='utf-8') as json_file:
        json.dump([info_generales], json_file, ensure_ascii=False, indent=2)

    dossier_formation = to_snake_case(info_generales['Infos_Generales']['Nom_Formation'])
    
    if not os.path.exists(dossier_formation):
        os.makedirs(dossier_formation)
        
    ecrire_dans_fichier(f" \n######### {id} ###########\nNom Formation : {info_generales['Infos_Generales']['Nom_Formation']}\nLien Formation : {info_generales['Infos_Generales']['Lien_Formation']}\nImage Formation : {info_generales['Infos_Generales']['Image_Formation']}\nNom Formateur : {instructeur_name}\nDescription Formateur : {instructeur_headline}\nDurée Total : {duree_Total}\nNiveau : {niveau}\nDate Upload : {upload}\n",'w',os.path.join(dossier_formation, "infos.txt"))
    
    for donnee in tqdm(info_generales['resultats'], desc="Téléchargement des Videos"):
        chapitre = to_snake_case(donnee['Chapitre'])
        nom_video = to_snake_case(donnee['Titre'])
        lien_video = donnee['Lien_video']

        formation_path = os.path.join(dossier_formation, chapitre)
        os.makedirs(formation_path, exist_ok=True)

        try:
            # download_video_requests(lien_video, os.path.join(formation_path, nom_video))
            download_video_wget(lien_video, os.path.join(formation_path, nom_video))
            # download_video_ytdl(lien_video, os.path.join(formation_path, nom_video))
        except Exception as e:
            print(f"video non télécharger ")
            pass

# with open('output.json', 'w', encoding='utf-8') as json_file:
#     json.dump(datas, json_file, ensure_ascii=False, indent=2)