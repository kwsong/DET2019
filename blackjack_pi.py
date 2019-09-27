FACE_CARDS = ['J', 'Q', 'K']
CARDS = ['2', '3', '4', '5', '6', '7', '8', '9', '10']


class BlackjackPi:

    current_count = 0

    player_hand = []
    dealer_hand = []

    # hard total that if breaks 21, then hand is busted
    player_total = 0
    dealer_total = 0

    # hard total if no ace present, soft total differs from other total if ace present
    player_soft_total = 0
    dealer_soft_total = 0

    player_bust = False
    dealer_bust = False

    player_soft_bust = False
    dealer_soft_bust = False

    player_blackjack = False
    dealer_blackjack = False

    def deal_cards(self, player_hand, dealer_card):

        self.player_hand = player_hand
        self.dealer_hand = [dealer_card]

        self.player_total = 0
        self.player_soft_total = 0
        self.player_bust = False
        self.player_soft_bust = False
        self.player_blackjack = False

        self.dealer_total = 0
        self.dealer_soft_total = 0
        self.dealer_bust = False
        self.dealer_soft_bust = False
        self.dealer_blackjack = False

        for card in self.player_hand:
            self.calc_total(card, True)

        for card in self.dealer_hand:
            self.calc_total(card, False)

        self.check_blackjack()

    def add_player_card(self, card):
        self.player_hand.append(card)
        self.calc_total(card, True)

    def add_dealer_card(self, card):
        self.dealer_hand.append(card)
        self.calc_total(card, False)

    def lookup_card_value(self, card):
        if card in FACE_CARDS:
            return (10, False)
        elif card == 'A':
            return (1, True)
        else:
            return (int(card), False)

    def update_count(self, card):
        if card in FACE_CARDS or card == 'A':
            self.current_count -= 1
        elif int(card) in range(2, 6):
            self.current_count += 1

    def check_bust(self):
        if self.player_total > 21:
            self.player_bust = True
        if self.dealer_total > 21:
            self.dealer_bust = True
        if self.player_soft_total > 21:
            self.player_soft_bust = True
        if self.dealer_soft_total > 21:
            self.dealer_soft_bust = True

    def calc_total(self, card, player):
        if player:
            val, is_soft = self.lookup_card_value(card)
            self.player_total += val
            if is_soft:
                self.player_soft_total += 11
            else:
                self.player_soft_total += val
        else:
            val, is_soft = self.lookup_card_value(card)
            self.dealer_total += val
            if is_soft:
                self.dealer_soft_total += 11
            else:
                self.dealer_soft_total += val
        self.update_count(card)
        self.check_bust()

    def check_blackjack(self):
        if self.player_soft_total == 21:
            self.player_blackjack = True
        if self.dealer_soft_total == 21:
            self.dealer_blackjack = True

    def hit(self, card, player):
        if player:
            self.add_player_card(card)
        else:
            self.add_dealer_card(card)

    def stand(self):
        while self.dealer_total < 17 or (self.dealer_total != self.dealer_soft_total and 17 < self.dealer_soft_total <= 21):
            self.hit(False)

    def best_move(self):
        dealer_card_val = self.lookup_card_value(self.dealer_hand[0])[0]
        if dealer_card_val == 1:
            dealer_card_val = 11

        if self.dealer_blackjack:
            return 'dealer_blackjack'

        if self.player_blackjack:
            return 'blackjack'
        elif self.player_total != self.player_soft_total:
            if self.player_soft_total <= 17 or (dealer_card_val in range(9, 11) and self.player_soft_total == 18):
                return 'hit'
            else:
                return 'stand'
        else:
            if self.player_total <= 11 or (self.player_total in range(12, 17) and dealer_card_val > 6) or (self.player_total == 12 and dealer_card_val in range(2, 4)):
                return 'hit'
            else:
                return 'stand'

    def did_bust(self, player):
        if player:
            return self.player_bust
        else:
            return self.dealer_bust

    def get_totals(self):
        player_best = self.player_total if self.player_soft_total > 21 else self.player_soft_total
        dealer_best = self.dealer_total if self.dealer_soft_total > 21 else self.dealer_soft_total
        return (player_best, dealer_best)

    def best_bet(self):
        if self.current_count > 0:
            return 'high'
        else:
            return 'low'

    def get_current_count(self):
        return self.current_count

    def __str__(self):
        return f"""
        Player hand: {self.player_hand}
        Player total: (hard) {self.player_total} (soft) {self.player_soft_total}
        Player bust? {self.player_bust}
        Player blackjack? {self.player_blackjack}

        Dealer hand: {self.dealer_hand}
        Dealer shows: {self.dealer_hand[0]}
        Dealer total: (hard) {self.dealer_total} (soft) {self.dealer_soft_total}
        Dealer bust? {self.dealer_bust}
        Dealer blackjack? {self.dealer_blackjack}
        """
