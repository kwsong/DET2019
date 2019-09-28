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

camera = picamera.PiCamera()

# global variable for our image file - to be captured soon!
image = 'image.jpg'

def takephoto(camera): 
    # this triggers an on-screen preview, so you know what you're photographing!
    camera.start_preview() 
    sleep(.5)                   #give it a pause so you can adjust if needed
    camera.capture('image.jpg') #save the image
    camera.stop_preview()       #stop the preview
    
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
#    response = client.text_detection(image=image, image_context=context)
    texts = response.text_annotations

    for text in texts:
        letter = text.description
        print(letter)
        if letter in validCards:
            hand.append(letter)

    return hand

def capture_initial_hands(camera, image = image):
    player_hand = []
    dealer_hand = []
            
    # Keep taking pictures if the correct number of cards isn't detected
    while len(player_hand) is not 2 or len(dealer_hand) is not 1:
        takephoto(camera) # Capture a picture
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
            
        time.sleep(0.1)
        
    return [player_hand, dealer_hand]

def capture_new_card(camera, old_hand, player, image = image):
# status: UNTESTED
# call this upon a hit to tell what the new card/hand is
# player should be 1 if player, 0 if dealer
    new_hand = []
    
    # Keep taking pictures if the correct number of cards isn't detected
    while len(new_hand) is not (len(old_hand)+1):
        takephoto(camera) # Capture a picture
        dealer_image, player_image, processed_image = process_image(image)
        
        if player == 1:
            hand_image = player_image
        else:
            hand_image = dealer_image
            
        with open(hand_image, 'rb') as image_file:
            #read the image file
            content = image_file.read()
            #convert the image file to a GCP Vision-friendly type
            new_hand = detect_hand(vision.types.Image(content=content))
    
    for card in new_hand:
        if card not in old_hand:
            new_card = card
    return new_card

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

def dealer_turn(dealer_hand):
# dealer's turn
    
    player_total, dealer_total = blackjack.get_totals()
    # The dealer draws cards until the sum >= 17
    while dealer_total < 17:
        print("Dealer needs a new card")
        time.sleep(3)

        new_card = capture_new_card(camera, dealer_hand, 0)
        
        blackjack.add_dealer_card(new_card)
        dealer_hand.append(new_card)
        player_total, dealer_total = blackjack.get_totals() 
        
        
    return dealer_hand

def main():

    while True:
        if crickit.touch_1.value == 0: # beginning of round indicated by a touch
            if blackjack.best_bet() == 'high':
                act_bet_high()
            else:
                act_bet_low()
            
            # take a photo of the hand
            [player_hand, dealer_hand] = capture_initial_hands(camera)      
            
            blackjack.deal_cards(player_hand, dealer_hand)

            print(blackjack.best_bet(), blackjack.best_move())
            
            # keep hitting if relevant
            while blackjack.best_move() == 'hit' and not blackjack.did_bust(1):
                act_hit()
                time.sleep(3) # wait 3 seconds for card to be dealt

                added_card = capture_new_card(camera, player_hand, 1, image)
                blackjack.add_player_card(added_card)
                player_hand.append(added_card)
                player_total, dealer_total = blackjack.get_totals()
                print("Player total: " + str(player_total))
                print("Dealer total: " + str(dealer_total))
                
            if blackjack.did_bust(1):
                act_lost()                
            elif blackjack.best_move() == 'stand':
                act_stand()
            elif blackjack.best_move() == 'blackjack':
                act_won()
                
            # Dealer's turn
            dealer_turn(dealer_hand)
            if blackjack.best_move() == 'dealer_blackjack':
                act_lost()
            elif blackjack.did_bust(0):
                act_won()
            else:
                player_total, dealer_total = blackjack.get_totals()
                if player_total >= dealer_total:
                    act_won()
                else:
                    act_lost()
                
    
if __name__ == '__main__':
        main()    
