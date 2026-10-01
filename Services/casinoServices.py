from Services.database import Coins, Infos
from cogs.casino import Games

def validarCoinAmout(aposta: int, coins: int) -> bool:
    if aposta <= 0:
        return False
    if aposta > coins:
        return False
    return True

async def startCoinFlipGame(user_id: int, aposta: int, escolha: str):
    user_id = user_id
    aposta = aposta
    coins = await Coins.get(user_id)

    if not validarCoinAmout(aposta, coins):
        return False, {"error": "Aposta inválida."}

    game = Games.CoinFlipGame()
    sucesso, resultado = game.play(escolha)

    if not sucesso:
        return False, {"error": resultado}
    if resultado["venceu"]:
        await Coins.add(user_id, aposta)
        return True, {"message": f"Você venceu! Ganhou {aposta} coins."}
    else:
        await Coins.remove(user_id, aposta)
        return True, {"message": f"Você perdeu! Perdeu {aposta} coins."}
