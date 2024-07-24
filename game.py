import random #rastgele sayılar üretmek
import cv2 #OpenCV kütüphanesinin Python arabirimi olan cv2 modülünü içeri aktarır.
from cvzone.HandTrackingModule import HandDetector #El izleme
import math  #matematiksel işlemler
import numpy as np
import cvzone #Bu, ek işlevsellikler ve araçlar sağlayan OpenCV kütüphanesinin bir genişlemesidir.
import time #Zaman işlemleri


# Kamera
#Bilgisayarınıza bağlı olan birincil video cihazını (genellikle bir web kamerası) açar.
cap = cv2.VideoCapture(0)
# Bu komutlar, video akışının genişlik
# ve yükseklik değerlerini ayarlar.
cap.set(3, 1280)
cap.set(4, 720)

# Detector
#Belirli bir algılama güveni ve maksimum el sayısı ile oluşturulur.
# Bu nesne daha sonra el izleme işlevselliğini kullanmak için kullanılabilir.
detector = HandDetector(detectionCon=0.8, maxHands=1)

# İşlev Bul
# x  mesafedir y cm cinsinden değerdir.
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
#Bu satır, numpy kütüphanesinin polyfit fonksiyonunu kullanarak verilen
# veri setine en uygun ikinci dereceden (quadratic) polinomu hesaplar.
coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C

# Oyun Değişkenleri
cx, cy = 250, 250 #Merkez koordinatları belirlemek için kullanılır.
color = (255, 0, 255) #pembe
counter = 0 #sayaç
score = 0 #skor
timeStart = time.time() #zamanın başlangıç noktasını kaydeder.
totalTime = 20 #Oyunun toplam süresini belirler.
max_score = 0

# Loop
while True:
    success, img = cap.read() #Video akışından bir kareyi okur.
    img = cv2.flip(img, 1) #fonksiyonu, bir görüntüyü belirli bir eksende (burada yatay eksende) yansıtarak döndürür.
    # Bu ifade, mevcut zamandan (time.time()) başlangıç zamanını (timeStart) çıkararak geçen süreyi hesaplar.
    if time.time()-timeStart < totalTime:
        # Bu ifade, belirli bir görüntü üzerinde el tespiti işlemini gerçekleştirir.

        hands,img = detector.findHands(img, draw=False)

        if hands:
            lmList = hands[0]['lmList'] #'hands' listesindeki ilk elin landmark (yer işaretçisi) listesini (lmList) alır.
            x, y, w, h = hands[0]['bbox']
            # hands listesindeki ilk elin sınırlayıcı kutusunun (bounding box) koordinatlarını (x, y, w, h) alır.
            # lmList listesinden 5. ve 17. landmark'ların (x1, y1) ve (x2, y2) koordinatlarını alır. Bu, elin belirli parçalarının koordinatlarını temsil eder.
            # Örneğin, 5. landmark genellikle elin başparmağının ucu, 17. landmark ise elin serçe parmağının ucu olabilir.
            x1, y1 = lmList[5][:2]
            x2, y2 = lmList[17][:2]

            # İki nokta arasındaki öklid uzaklığını hesaplar.
            distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C
            # print(distanceCM, distance)

            if distanceCM < 40: #Bu ifade, bir noktanın (cx, cy) belirli bir dikdörtgen bölgesi içinde mi olup olmadığını kontrol eder.
                if x < cx < x + w and y < cy < y + h: #Bu satır, bir dikdörtgeni çizer.
                    counter = 1
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)  #Bu satır, bir metni bir dikdörtgen içine ekler ve bu metni bir görüntü üzerinde çizer.
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x, y ))

        if score > max_score:
            max_score = score

        if counter:
            counter += 1 #değişkeninin değeri 1 artırılır.
            color = (0, 255, 0)
            if counter == 3:
                cx = random.randint(100, 1100) #cx değişkeninin değeri, rastgele bir sayı aralığında (100 ile 1100 arasında) belirlenir.
                cy = random.randint(100, 600) #cy değişkeninin değeri, rastgele bir sayı aralığında (100 ile 600 arasında) belirlenir.
                color = (255, 0, 255)
                score +=1
                counter = 0



        # Draw Button
        cv2.circle(img, (cx, cy), 30, color, cv2.FILLED)#Bu satır, bir dolgu rengiyle doldurulmuş bir daire çizer.
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED) #Bu satır, beyaz renkte ve dolu bir daire çizer.
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2) #Bu satır, beyaz renkte ve kalınlığı 2 piksel olan bir daire çizer.
        cv2.circle(img, (cx, cy), 30, (50, 50, 50), 2) # Bu satır, gri renkte ve kalınlığı 2 piksel olan bir daire çizer.

        # Bu kod parçacığı, oyunun ekran üstünde (HUD - Head-up Display) belirli bilgileri görüntülemek için kullanılır.
        # Game HUD
        cvzone.putTextRect(img, f'Time: {int(totalTime-(time.time()-timeStart))}', #Oyunun süresini görüntüler.
                           (1000, 75), scale=3, offset=20)

        cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (60, 75), scale=3, offset=20) #Oyuncunun skorunu görüntüler.
    else:
        cvzone.putTextRect(img, 'Game Over', (400, 250), scale=5, offset=30) #Oyunun sona erdiğini belirten bir metni görüntüler.
        cvzone.putTextRect(img, f'Your Score: {score}', (390, 450), scale=3, offset=20) #Oyuncunun skorunu görüntüler.
        cvzone.putTextRect(img, 'Press r to restart', (380, 525), scale=3, offset=10) #Oyuncuya yeniden başlatma talimatını görüntüler.
           #Bu kod parçacığı, işlenmiş görüntüyü ekranda görüntüler ve kullanıcıdan bir tuş girişi bekler.
        cvzone.putTextRect(img, f'Max Score: {max_score}', (400, 350), scale=3, offset=30)



    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    if key == ord('r'): #Bu ifade, kullanıcının girdiği tuşun 'r' harfi olup olmadığını kontrol eder.
        timeStart = time.time() # Bu satır, zamanın başlangıç noktasını yeniden ayarlar. Yani, oyunun süresi tekrar başlar.
        score = 0 #Bu satır, oyuncunun skorunu sıfırlar.
        counter = 0