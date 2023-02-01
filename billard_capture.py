import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.filters import try_all_threshold, threshold_triangle, threshold_minimum, threshold_mean, threshold_otsu,threshold_yen
from skimage.measure import label
from skimage import morphology, segmentation

import time


def policzBileNaZdjeciu(image):
    grayImage = image.astype(np.uint8)
    kernel = np.ones((7, 7), np.uint8)
    opening = cv2.morphologyEx(grayImage, cv2.MORPH_OPEN, kernel, iterations=1)
    cnts = cv2.findContours(opening, None, cv2.CHAIN_APPROX_NONE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    return len(cnts)


def dilatateImage(im):
    kernel = np.ones((7, 7), np.uint8)
    im = im.astype(np.uint8)
    im = cv2.dilate(im, kernel, iterations=1)
    return im.astype(np.bool_)


def czyZawieraKij(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hsv_l = np.array([90, 100, 100])
    hsv_h = np.array([125, 255, 255])
    return cv2.inRange(hsv, hsv_l, hsv_h).any()


def policzObiektyNaStole(stol):
    pusty = cv2.imread("pusty.png")

    stol = cv2.cvtColor(stol, cv2.COLOR_BGR2RGB)
    pusty = cv2.cvtColor(pusty, cv2.COLOR_BGR2RGB)

    wyizolowaneElementy = cv2.subtract(stol, pusty)#wyizolowane elementy
    wyizolowaneElementy = cv2.cvtColor(wyizolowaneElementy, cv2.COLOR_RGB2GRAY)
    threshBialeZolte = threshold_minimum(wyizolowaneElementy)#zolte+ biala threshold
    threshCzerwoneCzarna = threshold_otsu(wyizolowaneElementy)#czerwone i czarna
    if czyZawieraKij(stol):
        stol = {"czerwone": 0,
                "zolte": 0,
                "czarna": False,
                "biala": False,
                "kij": True}
        return (stol)
    else:
        wyizolowaneZolteBiale = wyizolowaneElementy > threshBialeZolte  # zolte + biala

        czerwone = wyizolowaneElementy > threshCzerwoneCzarna#czerwone i czarna
        czerwone = czerwone ^ wyizolowaneZolteBiale  # odejmowanie zoltej
        czerwone = morphology.remove_small_objects(czerwone, 300)
        czerwone = dilatateImage(czerwone)
        biala = morphology.remove_small_objects(wyizolowaneZolteBiale, 800)  # biala
        zolte = (wyizolowaneZolteBiale ^ biala)
        wyizolowaneElementy-=5
        wyizolowaneElementy = np.maximum(0.0, wyizolowaneElementy)
        black = morphology.remove_small_objects(~(((wyizolowaneElementy > threshold_mean(wyizolowaneElementy)) ^ wyizolowaneZolteBiale) ^ czerwone), 800)
        black = segmentation.clear_border(black)
        stol = {"czerwone": policzBileNaZdjeciu(czerwone),
                "zolte": policzBileNaZdjeciu(zolte),
                "czarna": policzBileNaZdjeciu(black) > 0,
                "biala": policzBileNaZdjeciu(biala) > 0,
                "kij": False}
        return (stol)



# print(policzStol(stol))
gracz1 = 0
gracz2 = 0
gracze = [gracz1, gracz2]
# czerwony - 1 zolty - 2
aktualnyGraczId = 0
czyPrzyznanoKolorGraczowi = 0
stolInfo = {"czerwone": 0,
            "zolte": 0,
            "czarna": False,
            "biala": False,
            "kij": False}
oldInfo = {"czerwone": 7,
           "zolte": 7,
           "czarna": True,
           "biala": True,
           "kij": False}

tempInfo = None

aktualnaKlatkaZFIlmu = cv2.VideoCapture('film2.avi')

stol = aktualnaKlatkaZFIlmu.read()

brakKijaNaStole=False
wyswietlonoInformacjeFlaga=0

while aktualnaKlatkaZFIlmu.isOpened():


    czyZdobytoPunkt = False
    quit = 1

    while (True):
        aktualnaKlatkaZFIlmu.isOpened()
        ret, stol = aktualnaKlatkaZFIlmu.read()
        if cv2.waitKey(1) == ord('q'):
            continue
        if ret:
            cv2.imshow('frame', stol)
        else:
            quit = 10

            break


        tempInfo = policzObiektyNaStole(stol)
        # print(tempInfo)
        if (stolInfo == None):
            stolInfo = tempInfo

        if tempInfo.get("kij") == True:

            if wyswietlonoInformacjeFlaga == 1:
                print(stolInfo, " aktualny gracz: ", aktualnyGraczId)
                wyswietlonoInformacjeFlaga=0
            # print("kij")

            break

        else:
            wyswietlonoInformacjeFlaga=1
            # print("nie kij")
            brakKijaNaStole = True
            stolInfo = tempInfo



    if quit == 10:
        print("koniec nagrania")
        break

    # print("wymszlo")

    if (czyPrzyznanoKolorGraczowi == 0 and oldInfo.get("czerwone") > stolInfo.get("czerwone")  # przyzanie koloru czerwonego
            and oldInfo.get("zolte") == stolInfo.get("zolte")
            and stolInfo.get("czarna") == True
            and stolInfo.get("biala") == True):
        gracze[aktualnyGraczId] = 1
        czyZdobytoPunkt = True
        czyPrzyznanoKolorGraczowi = 1
        if aktualnyGraczId == 1:
            gracze[0] = 2
        else:
            gracze[1] = 2
        print("wbito czerwona, zostalo: ", stolInfo.get("czerwone"), '\n')
        # print(stolInfo)

    if (czyPrzyznanoKolorGraczowi == 0 and oldInfo.get("czerwone") == stolInfo.get("czerwone")  # przyzanie koloru zoltego
            and oldInfo.get("zolte") > stolInfo.get("zolte")
            and stolInfo.get("czarna") == True
            and stolInfo.get("biala") == True):
        gracze[aktualnyGraczId] = 2
        czyZdobytoPunkt = True
        czyPrzyznanoKolorGraczowi = 1
        if aktualnyGraczId == 1:
            gracze[0] = 1
        else:
            gracze[1] = 1
        print("wbito zolta, zostalo: ", stolInfo.get("zolte"), '\n')
        # print(stolInfo)

    if (czyPrzyznanoKolorGraczowi == 1 and (
            oldInfo.get("czerwone") > stolInfo.get("czerwone")  # sprawdzanie czy zostaala poprawnie wbita bila
            or oldInfo.get("zolte") > stolInfo.get("zolte"))
            and stolInfo.get("czarna") == True
            and stolInfo.get("biala") == True):

        if gracze[aktualnyGraczId] == 1 and oldInfo.get("czerwone") > stolInfo.get("czerwone"):
            czyZdobytoPunkt = True
            print("wbito czerwona, zostalo: ", stolInfo.get("czerwone"), '\n')

        elif gracze[aktualnyGraczId] == 2 and oldInfo.get("zolte") > stolInfo.get("zolte"):
            czyZdobytoPunkt = True
            print("wbito zolta, zostalo: ", stolInfo.get("zolte"), '\n')



        if stolInfo.get("czarna") == False and czyPrzyznanoKolorGraczowi == 1:
            quit=10
            if stolInfo.get("czerwone") <= 0:
                if gracze[aktualnyGraczId] == 1 and stolInfo.get("biala") == False:
                    print("zolty wygral")
                    break
                print("czerwony wygral")
                break
            if stolInfo.get("zolte") <= 0:
                if gracze[aktualnyGraczId] == 2 and stolInfo.get("biala") == False:
                    print("czerwony wygral")
                    break
                print("zolty wygral")
                break

            if stolInfo.get("zolte") > 0:
                if gracze[aktualnyGraczId] == 1:
                    print("czerwony wygral")
                    break
                else:
                    print("zolty wygral")
                break

            if gracze[aktualnyGraczId] == 1:
                print("czerwony wygral")
                break
            else:
                print("zolty wygral")
                break

    if czyZdobytoPunkt == False and brakKijaNaStole:
        brakKijaNaStole = False
        if aktualnyGraczId == 1:
            aktualnyGraczId = 0
        else:
            aktualnyGraczId = 1

    if czyZdobytoPunkt:
        oldInfo = stolInfo
        if aktualnyGraczId == 1:
            aktualnyGraczId = 1
        else:
            aktualnyGraczId = 0

    flag = 2
    if cv2.waitKey(1) == ord('q'):
        continue

cv2.destroyAllWindows()
aktualnaKlatkaZFIlmu.release()

# po pojawieniu sie kija sprawdzamy poprzednie zdjeceie zeby okreslic co sie stalo
