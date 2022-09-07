# Author : Brother
import os
import inspect
import discord

# -------------------------------
# ATTENTION :
# le token du bot doit se trouver dans un fichier TOKEN.txt (ou écrit en dur dans le code)
TOKEN = open('TOKEN.txt').read().strip()
# -------------------------------

#TODO librairie de logs : création d'un fichier de logs sur le fonctionnement+ fichier erreur séparé plutôt que des print

droit_de_parler = {
    'orc-gordunn' : ['elf-truc','homme-poule','conseil-havresac'],
    'elf-truc' : ['orc-gordunn','conseil-havresac'],
    'homme-poule' : ['orc-gordunn','conseil-havresac'],
    'homme-bidulle' : []
}
groupes_de_discussion = ['conseil-havresac']

def verifier_droit_parler(parleur,ecouteur):
    if parleur in droit_de_parler:
        return ecouteur in droit_de_parler[parleur]
    else:
        return False

def trouver_les_peuples_du_groupe(parleur,groupe):
    peuple_target=[]
    for peuple in droit_de_parler:
        if parleur != peuple:
            if groupe in droit_de_parler[peuple]:
                peuple_target.append(peuple)
    return peuple_target


def help_message(parleur):
    msg='''Pour parler à un peuple ou conseil en passant par le messager, écrit : `@messager-titania1 nom_peuple_cible : message_a_envoyer`
- exemple: ```@messager-titania1 peuple-sirene : nous vous remercions pour les chants```
Tu dois ensuite recevoir un message de confirmation du messager sinon, préviens ton MJ.

(tips): Pour écrire un message de plus d'une ligne, prépare le message quelque part sur un brouillon, et copie/colle le après les ':'

'''
    if parleur in droit_de_parler:
        if len(droit_de_parler[parleur]) > 0 :
            msg=msg+'''Tu as le droit de parler à:'''
            for i in droit_de_parler[parleur]:
                msg=msg+"\n    [+] "+i
        else:
            msg=msg+'''Il semble que tu n'as le droit de parler à personne'''
    else:
        msg=msg+'''Il semble que tu n'as le droit de parler à personne'''
    return msg

client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if not message.author.bot:
        if len(f"{message.content}") > 0:
            print(f'channel:{message.channel} message from {message.author}: {message.content}')

            m=f"{message.content}".split(">")[1].strip()
            # on test si il n'y a que le nom du bot dans le message (vide)
            if len(m) == 0:
                # on fait peter l'aide
                await message.channel.send(help_message(str(message.channel)))
            else:
                # on récupére les infos du message
                channel_peuple_source= str(message.channel)
                cible=f"{message.content}".split(":")[0].split(">")[1].strip()
                message_txt=":".join(f"{message.content}".split(":")[1:]).strip()
                
                # on regarde si c'est un message à destination d'un groupe ou non
                if cible in groupes_de_discussion:
                    # on retrouve tout les peuples destinataires
                    liste_peuple_cible=trouver_les_peuples_du_groupe(channel_peuple_source,cible)
                    groupe=f"(envoyé à tout {cible}) "
                    message_de_groupe=True
                else:
                    # message uniquement pour 1 peuple
                    liste_peuple_cible=[cible]
                    groupe=""
                    message_de_groupe=False

                # on envoit à tout les peuples, un par un
                for channel_peuple_cible in liste_peuple_cible:
                    message_send=False
                    message_fail_reason='raison inconnue'
                    if verifier_droit_parler(str(channel_peuple_source),channel_peuple_cible) or message_de_groupe:
                        for channel in client.get_all_channels():
                            # on trouve le channel cible
                            if channel.name==channel_peuple_cible:
                                await channel.send( f"Message provenant de {channel_peuple_source} {groupe}: {message_txt}")
                                resultat=f"Message bien envoyé à {channel_peuple_cible}"
                                print(resultat)
                                await message.channel.send(resultat)
                                message_send=True
                    else :
                        message_fail_reason=f"interdit de parler à {channel_peuple_cible}"
                    if not message_send:
                        resultat=f"Message non envoyé à {channel_peuple_cible}, à cause de: {message_fail_reason}"
                        print(resultat)
                        await message.channel.send(resultat)

client.run(TOKEN)