import discord

def tutorial():
    embed = discord.Embed(
        title="📌 Bem-vindo ao tutorial da Aiko!",
        description=(
            "Aqui você vai aprender a usar o sistema de tickets, embeds e economia da Aiko "
            "de forma simples e rápida.\n\n"
            "Prometo que tudo será fácil de entender, então vamos lá! :3"
        ),
        color=discord.Color.pink()
    )

    return embed

def tutorial_embed():
    embed2 = discord.Embed(
        title="🎫 Sistema de Tickets",
        description=(
            "O sistema de tickets da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros criem tickets para suporte enquanto a staff gerencia tudo facilmente.\n\n"
            "📌 Quando um ticket é fechado, um **transcript** é enviado para o usuário e a equipe."
        ),
        color=discord.Color.pink()
    )

    # Criar ticket
    embed2.add_field(
        name="🛠️ Como criar um ticket",
        value=(
            "`/tickets criar` → cria um ticket padrão\n"
            "`/tickets editar <id>` → personaliza o ticket\n\n"
            "**Você pode alterar:**\n"
            "• Título\n"
            "• Descrição\n"
            "• Cor\n"
            "• Cargo responsável\n"
            "• Imagem"
        ),
        inline=False
    )

    # Enviar painel
    embed2.add_field(
        name="📤 Enviando o painel",
        value=(
            "`/tickets enviar <id> <canal>`\n\n"
            "Envia o painel de ticket para o canal desejado."
        ),
        inline=False
    )

    # Interface
    embed2.add_field(
        name="✨ Interface",
        value=(
            "O sistema utiliza botões para abrir, fechar e editar tickets,\n"
            "tornando tudo mais prático e intuitivo."
        ),
        inline=False
    )

    embed2.set_footer(text="Aiko • Sistema de Tickets")

    return embed2

def tutorial_embed2():
    embed3 = discord.Embed(
        title="📋 Sistema de Embeds",
        description=(
            "O sistema de embeds da Aiko é simples, intuitivo e eficiente.\n"
            "Ele permite que membros criem embeds personalizados para comunicação com os usuários.\n\n"
            "📌 Os embeds podem conter título, descrição, cor, imagens e campos personalizados."
        ),
        color=discord.Color.pink()
    )
    
    embed3.add_field(
        name="🛠️ Como criar um embed",
        value=(
            "`/embeds criar` → cria um embed padrão\n"
            "`/embeds editar <id>` → personaliza o embed\n\n"
            "**Você pode alterar:**\n"
            "• Título\n"
            "• Descrição\n"
            "• Cor\n"
            "• Imagem"
        ),
        inline=False
    )

    embed3.add_field(
        name="📤 Enviando o embed",
        value=(
            "`/embeds enviar <id> <canal>`\n"
            "Envia o embed para o canal desejado.\n\n"
        ),
        inline=False
    )
    embed3.add_field(
        name="✨ Interface",
        value=(
            "O sistema utiliza botões para editar os embeds,\n"
            "tornando tudo mais prático e intuitivo."
        ),
        inline=False
    )

    embed3.set_footer(text="Aiko • Sistema de Embeds")

    return embed3

def tutorial_embed3():
    embed4 = discord.Embed(
        title="💰 Sistema de Economia",
        description=(
            "O sistema de economia da Aiko é simples, intuitivo e eficiente.\n"
            "Ganhe moedas através de atividades no servidor e utilize-as em recompensas personalizadas.\n\n"
            
            "📌 Ganhe moedas jogando minigames, trabalhando ou coletando recompensas diárias.\n"
            "Use como quiser: cargos personalizados, conteúdos exclusivos e muito mais!\n\n"
            
            "⚠️ **Aviso:** A Aiko não se responsabiliza por trocas ou negociações entre membros.\n"
            "Fique atento a golpes e nunca compartilhe informações pessoais."
        ),
        color=discord.Color.pink()
    )

    embed4.add_field(
        name="🪙 Como ganhar coins",
        value=(
            "• `/eco diario` → Recompensa diária + streak 🔥\n"
            "• `/eco work` → Trabalhe e ganhe coins\n"
            "• `/box abrir` → Abra lootboxes\n"
            "• `/casino` → Aposte e tente multiplicar suas moedas"
        ),
        inline=False
    )

    embed4.add_field(
        name="🎲 Jogos disponíveis",
        value=(
            "• Coinflip\n"
            "• Dice\n"
            "• Slots\n"
            "• Blackjack"
        ),
        inline=True
    )

    embed4.add_field(
        name="📌 Outros comandos",
        value=(
            "• `/eco carteira`\n"
            "• `/eco pay`\n"
            "• `/eco rank`\n"
            "• `/box comprar`"
        ),
        inline=True
    )

    embed4.add_field(
        name="⏳ Dicas",
        value=(
            "• Alguns comandos possuem cooldown\n"
            "• Aposte apenas o que você possui\n"
            "• Nem sempre a sorte está do seu lado :3"
        ),
        inline=False
    )

    embed4.set_footer(text="Aiko • Sistema de Economia")

    return embed4

def setupfinal():
    embed5 = discord.Embed(
        title="**Sobre esse chat**",
        description=(
            "O use como painel de comandos para os comandos de tickets e embeds"
        ),
        color=discord.Color.pink()
    )

    embed5.set_footer(text="Aiko • Chat de cmd")
