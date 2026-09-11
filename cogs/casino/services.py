from database import get_connection
from . import embeds
import random
import discord
from discord import app_commands
from discord.ext import commands

class CardGame:
    def draw_card():
        suits = ["♣️", "♠️", "♥️", "♦️"]
        values = [
            ("A", 11),
            ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("J", 10), ("Q", 10), ("K", 10)
        ]

        value, points = random.choice(values)
        suit = random.choice(suits)

        return {"display": f"{value}{suit}", "value": points}

    def calculate_hand(hand):
        total = sum(card["value"] for card in hand)

        # tratar Ás
        aces = sum(1 for card in hand if card["value"] == 11)

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def start_game():
        player = [CardGame.draw_card(), CardGame.draw_card()]
        dealer = [CardGame.draw_card(), CardGame.draw_card()]

        return player, dealer

class SlotGame:
    def spin_slots(aposta: int):
            EMOJIS = ["🍒", "🍋", "🍉", "⭐", "💎", "💶", "🪙"]
            r1 = random.choice(EMOJIS)
            r2 = random.choice(EMOJIS)
            r3 = random.choice(EMOJIS)
    
            if r1 == r2 == r3:
                return (r1, r2, r3), aposta * 6, "jackpot"
            elif r1 == r2 or r2 == r3 or r1 == r3:
                return (r1, r2, r3), aposta * 3, "win"
            else:
                return (r1, r2, r3), -aposta, "lose"

class CoinFlipGame:
    def __init__(self):
        self.options = ["cara", "coroa"]

    def play(self, escolha: str, aposta: int, coins: int):

        escolha = escolha.lower()

        if escolha not in self.options:
            return False, "escolha invalida"

        if aposta <= 0:
            return False, "A aposta deve ser maior que 0"

        if aposta > coins:
            return False, "Você não tem dinheiro suficiente"

        resultado = random.choice(self.options)
        venceu = escolha == resultado

        return True, {"escolha": escolha, "aposta": aposta, "resultado": resultado, "venceu": venceu}