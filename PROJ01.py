import picamera     #camera library
import pygame as pg #audio library
import os           #communicate with os/command line

from google.cloud import vision  #gcp vision library
from time import sleep
from adafruit_crickit import crickit
from PIL import Image
import time
import signal
import sys
import re           #regular expression lib for string searches!
import socket

from process_image import process_image
from blackjack_pi import BlackjackPi

#set up your GCP credentials - replace the " " in the following line with your .json file and path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/DET-2019-d3b82e6383ae.json"

# this line connects to Google Cloud Vision! 
client = vision.ImageAnnotatorClient()

blackjack = BlackjackPi()

# global variable for our image file - to be captured soon!
image = 'image.jpg'

def takephoto(camera):
# status: TESTED    
    # this triggers an on-screen preview, so you know what you're photographing!
#    camera.start_preview() 
    sleep(.5)                   #give it a pause so you can adjust if needed
    camera.capture('image.jpg') #save the image
#    crop('image.jpg', (0,0,1920,540), 'dealer_image.jpg')
#    crop('image.jpg', (0,540,1920,1080), 'player_image.jpg')
#    camera.stop_preview()       #stop the preview

def crop(image, coords, new_image):
# status: TESTED
    image_obj = Image.open(image)
#    image_obj = image_obj.rotate(90)
    cropped_image = image_obj.crop(coords)
    cropped_image.save(new_image)
    cropped_image.show()
    
def detect_hand(image):
    """Takes an image and uses GCV to detect valid cards in the image

    Arguments:
        image {Image} -- a GCV friendly image type

    Returns:
        [str] -- array of cards in hand
    """

    validCards = ['A', 'K', 'Q', 'J', '10',
                  '9', '8', '7', '6', '5', '4', '3', '2']
    hand = []

#    context = vision.types.ImageContext(language_hints="en-t-i0-plain")
    response = client.text_detection(image = image)
 #   response = client.text_detection(
 #       image=image, image_context=context)
    texts = response.text_annotations

    for text in texts:
        letter = text.description
        print(letter)
        if letter in validCards:
            hand.append(letter)

    return hand
'''
def capture_initial_hands(camera):
# status: TESTED
    player_hand = []
    dealer_hand = []
            
    # Keep taking pictures if the correct number of cards isn't detected
    while len(player_hand) is not 2 or len(dealer_hand) is not 1:
        takephoto(camera) # Capture a picture

        with open('player_image.jpg', 'rb') as image_file:
            #read the image file
            content = image_file.read()
            #convert the image file to a GCP Vision-friendly type
            image = vision.types.Image(content=content)
            player_hand = detect_hand(image)
            print("Player hand: ")
            for card in player_hand:
                print(card)
                print("Number of player cards: " + str(len(player_hand)))
                    
        with open('dealer_image.jpg', 'rb') as image_file:
            #read the image file
            content = image_file.read()
            #convert the image file to a GCP Vision-friendly type
            image = vision.types.Image(content=content)
            dealer_hand = detect_hand(image)
            print("Dealer hand: ")
            for card in dealer_hand:
                print(card)
                print("Number of dealer cards: " + str(len(dealer_hand)))
        
        time.sleep(0.1)
        
    return [player_hand, dealer_hand]

def capture_new_hand(camera, old_hand, image):
# status: UNTESTED
# call this upon a hit to tell what the new card/hand is
# the 'image' argument is either 'player_image.jpg' or 'dealer_image.jpg'
    new_hand = []
    
    # Keep taking pictures if the correct number of cards isn't detected
    while len(new_hand) is not (len(old_hand)+1):
        takephoto(camera) # Capture a picture

        with open(image, 'rb') as image_file:
            #read the image file
            content = image_file.read()
            #convert the image file to a GCP Vision-friendly type
            image = vision.types.Image(content=content)
            new_hand = detect_hand(image)
    return new_hand

def sum_hand(hand):
# status: TESTED
    sum = 0
    num_aces = 0
    for card in hand:
        if card == 'A':
            sum += 11
            num_aces += 1
        elif card == 'K' or card == 'Q' or card == 'J':
            sum += 10
        else:
            sum += int(card)
    return sum

def count_cards(count, new_cards):
# status: TESTED
    for card in new_cards:
        if card == '2' or card == '3' or card == '4' or card == '5' or card == '6':
            count += 1
        elif card == '10' or card == 'J' or card == 'Q' or card == 'K' or card == 'A':
            count -= 1
    return count
    '''
'''
def hit_or_stand(player_hand, dealer_hand):
# status: UNTESTED
# return True if player should hit
    dealer_card = dealer_hand[0]
    player_sum = sum_hand(player_hand)
    dealer_sum = sum_hand(dealer_hand) #this is actually just the dealer_card
    # Stand conditions
    if player_sum >= 17:
        return False
    elif dealer_sum <= 6 and player_sum >= 13:
        return False
    
    # Hit conditions (from casinobonusking.com)
    elif dealer_card == '7' or dealer_card == '8' or dealer_card == '9' or dealer_card == '10' or dealer_card == 'A':
        if player_sum == 8 or (player_sum >= 12 and player_sum <= 16):
            return True
        elif dealer_card == 'A' and player_sum == 11:
            return True
        elif dealer_card == '10' and player_sum == 10:
            return True
        elif (dealer_card == '7' or dealer_card == '8' or dealer_card == '9') and player_sum == 9:
            return True
    
    else:
        return False
        '''
'''
def dealer_turn(dealer_hand):
# status: UNTESTED
# return the final dealer_hand

    # First, the dealer's face-down card is flipped, and the new hand is captured
    dealer_hand = capture_new_hand(camera, dealer_hand, 'dealer_image.jpg')
    
    # Next, the dealer draws cards until the sum >= 17
    while sum_hand(dealer_hand) < 17:
        print("Dealer needs a new card")
        time.sleep(3)
        dealer_hand = capture_new_hand(camera, dealer_hand, 'dealer_image.jpg')
        print("New card successfully detected")
        time.sleep(1)
        
    return dealer_hand   
'''
def act_bet_low():
    # do some stuff for a low bet
    print("Spitting out min bet")
    crickit.continuous_servo_1.throttle = 1.0
    time.sleep(3)
    crickit.continuous_servo_1.throttle = 0.0

def act_bet_medium():
    # do some stuff for a "normal" bet
    print("Betting normally")
    crickit.continuous_servo_2.throttle = 1.0
    time.sleep(3)
    crickit.continuous_servo_2.throttle = 0.0
    
def act_bet_high():
    # do some stuff for a high bet
    print("BETTING LOTS OF MONEY")
    crickit.continuous_servo_2.throttle = 1.0
    time.sleep(6)
    crickit.continuous_servo_2.throttle = 0.0
    
def act_won():
    # do some stuff if player won (or if there's a standoff)
    print("I won")
    
def act_lost():
    # do some stuff if player goes bust or loses
    print("I lost")
    
def act_stand():
    # tap left hand (fist) 3 times for a stand
    print("I stand. No more cards")
    for i in range(3):
        crickit.servo_3.angle = 90
        time.sleep(0.2)
        crickit.servo_3.angle = 0
        time.sleep(0.2)
    
def act_hit():
    # tap right hand 3 times for a hit
    print("I hit. Give me card.")
    for i in range(3):
        crickit.servo_4.angle = 90
        time.sleep(0.2)
        crickit.servo_4.angle = 180
        time.sleep(0.2)
    
def main():

    camera = picamera.PiCamera()   #generate a camera object
    takephoto(camera)

    
    global image

    dealer_image, player_image, processed_image = process_image(image)

    with open(dealer_image, 'rb') as image_file:
        content = image_file.read()

    dealer_hand = detect_hand(vision.types.Image(content=content))
    print("Dealer hand: ")
    for card in dealer_hand:
        print(card)
        print("Number of dealer cards: " + str(len(dealer_hand)))

    with open(player_image, 'rb') as image_file:
        content = image_file.read()

    player_hand = detect_hand(vision.types.Image(content=content))
    print("Player hand: ")
    for card in player_hand:
        print(card)
        print("Number of player cards: " + str(len(player_hand)))

    blackjack.deal_cards(player_hand, dealer_hand)

    print(blackjack.best_bet(), blackjack.best_move())
'''    
    while True:
        if crickit.touch_1.value==1: # cap touch indicates that a round has been dealt
            [player_hand, dealer_hand] = capture_initial_hands(camera)
            print("Place your bet")
            # place a bet depending on the card count.
            # TO-DO: FIX THIS!
            if count == 0:
                bet_medium()
            elif count < 0:
                bet_low()
            else:
                bet_high()
            
            print("Deal cards")
            time.sleep(5)
            # determine what the hands are. player has 2 cards, dealer has 1 (+1 face-down one)
            [player_hand, dealer_hand] = capture_initial_hands(camera)
            player_sum = sum_hand(player_hand)
            dealer_sum = sum_hand(dealer_hand)
 
            # player's turn
            while hit_or_stand(player_hand):
                hit()
                time.sleep(3)
                player_hand = capture_new_hand(camera, player_hand, 'player_image.jpg')
            
            stand()
            
            print("Dealer's turn")
            time.sleep(3)
            dealer_hand = dealer_turn()
            
            print("Who won this round???")
            if dealer_hand < 21 and player_hand < 21:
                if sum_hand(player_hand) >= sum_hand(dealer_hand):
                    won_round()
                else:
                    lost_round()
            elif player_hand == 21 and dealer_hand != 21:
                won_round()
            elif player_hand == 21 and dealer_hand == 21: # standoff
                print("Standoff")
            else:
                lost_round()
                            
            # updating count should be the last thing done in the round
            count = count_cards(count, player_hand + dealer_hand)
'''
    
if __name__ == '__main__':
        main()    
