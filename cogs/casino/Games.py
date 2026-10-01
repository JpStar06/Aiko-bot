import random
import discord
from cogs.casino import embeds

class CardGame():
    """Regras de baralho usadas pelo Blackjack."""

    _NAIPES = ["♣️", "♠️", "♥️", "♦️"]
    _VALORES = [
        ("A", 11),
        ("2", 2), ("3", 3), ("4", 4), ("5", 5),
        ("6", 6), ("7", 7), ("8", 8), ("9", 9),
        ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
    ]

    @staticmethod
    def draw_card() -> dict:
        """Compra uma carta aleatória: ``{"display": "A♠️", "value": 11}``."""
        valor, pontos = random.choice(CardGame._VALORES)
        naipe = random.choice(CardGame._NAIPES)

        return {"display": f"{valor}{naipe}", "value": pontos}

    @staticmethod
    def calculate_hand(hand: list[dict]) -> int:
        """Soma a mão tratando o Ás (11 -> 1) para evitar estourar 21."""
        total = sum(card["value"] for card in hand)
        ases = sum(1 for card in hand if card["value"] == 11)

        while total > 21 and ases:
            total -= 10
            ases -= 1

        return total

    @staticmethod
    def start_game() -> tuple[list[dict], list[dict]]:
        """Compra as duas cartas iniciais do jogador e do dealer."""
        player = [CardGame.draw_card(), CardGame.draw_card()]
        dealer = [CardGame.draw_card(), CardGame.draw_card()]

        return player, dealer


class SlotGame():
    """Regras do caça-níquel."""

    _EMOJIS = ["🍒", "🍋", "🍉", "⭐", "💎", "💶", "🪙"]

    @staticmethod
    def spin_slots(aposta: int) -> tuple[tuple[str, str, str], int, str]:
        """Gira os 3 rolos e devolve ``(rolos, variação_de_coins, tipo)``.

        ``variação_de_coins`` já vem com o sinal certo: positiva em caso de
        vitória/jackpot, negativa (``-aposta``) em caso de derrota — basta
        somar direto ao saldo do jogador, sem descontar a aposta à parte.
        """
        r1, r2, r3 = (random.choice(SlotGame._EMOJIS) for _ in range(3))

        if r1 == r2 == r3:
            return (r1, r2, r3), aposta * 6, "jackpot"
        elif r1 == r2 or r2 == r3 or r1 == r3:
            return (r1, r2, r3), aposta * 3, "win"
        else:
            return (r1, r2, r3), -aposta, "lose"


class CoinFlipGame:
    """Regras do cara ou coroa."""

    OPCOES = ("cara", "coroa")

    @classmethod
    def play(cls, escolha: str):
        escolha = escolha.lower()

        choice = random.choice(cls.OPCOES)
        venceu = escolha == choice

        return True, {
            "escolha": escolha,
            "resultado": choice,
            "venceu": venceu,
        }

class DiceGame:
    """Regras do jogo de dados."""

    @staticmethod
    def roll_dice() -> int:
        """Rola um dado de 6 lados."""
        return random.randint(1, 6)

    @classmethod
    def play(cls, aposta: int, escolha: int, coins: int) -> tuple[bool, dict | str]:

        player_roll = cls.roll_dice()
        bot_roll = cls.roll_dice()
