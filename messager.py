# Author : Brother
import discord
import json
import logging
import traceback

# -------------------------------
# ATTENTION :
# le token du bot doit se trouver dans un fichier TOKEN.txt (ou écrit en dur dans le code)
TOKEN = open('TOKEN.txt').read().strip()
# un fichier droit_de_parler.json doit se trouver à la racine (voir fichier example)
droit_de_parler_fichier="droit_de_parler.json"
# un fichier groupes_de_discussion.json doit se trouver à la racien (voir fichier example)
groupes_de_discussion_fichier="groupes_de_discussion.json"
# -------------------------------

def reload_droit_et_groupe():
    global droit_de_parler
    global groupes_de_discussion
    droit_de_parler=json.load(open(droit_de_parler_fichier))
    groupes_de_discussion=json.load(open(groupes_de_discussion_fichier))["groupes"]

# on charge les droit_de_parler et groupes_de_discussion à partir du fichier
reload_droit_et_groupe()

def verifier_droit_parler(parleur,ecouteur):
    reload_droit_et_groupe()
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
    msg='''Bonjour je suis le messager de Titania,

Pour parler à un peuple ou conseil en passant par moi, écrit : `@messager-titania nom_peuple_cible : message_a_envoyer`
- exemple: ```@messager-titania peuple-sirene : nous vous remercions pour les chants```
Tu dois ensuite recevoir un message de confirmation de ma part sinon, c'est que quelque chose s'est mal passé sur mon chemin. préviens vite ton MJ.

(tips): Pour écrire un message de plus d'une ligne, appuyer sur `shift+enter` pour ajouter une nouvelle ligne.

'''
    if parleur in droit_de_parler:
        if len(droit_de_parler[parleur]) > 0 :
            msg=msg+'''Tu as le droit de parler à:'''
            for groupe in droit_de_parler[parleur]:
                if groupe in groupes_de_discussion :
                    msg=msg+f"\n    [+] {groupe} -> {trouver_les_peuples_du_groupe(parleur,groupe)}"
                else:
                    msg=msg+f"\n    [+] {groupe}"
        else:
            msg=msg+'''Il semble que tu n'as le droit de parler à personne'''
    else:
        msg=msg+'''Il semble que tu n'as le droit de parler à personne'''
    return msg

client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    try :
        if not message.author.bot:
            reload_droit_et_groupe()
            if len(f"{message.content}") > 0:
                logger.info(f'channel:{message.channel} message from {message.author}: {message.content}')

                m=f"{message.content}".split(">")[1].strip()
                # on test si il n'y a que le nom du bot dans le message (vide)
                if len(m) == 0:
                    # on fait peter l'aide
                    logger.info(f"on envoit l'aide pour {message.channel}")
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
                                    resultat=f"Message bien envoyé à {channel_peuple_cible} par {channel_peuple_source}"
                                    logger.info(resultat)
                                    await message.channel.send(resultat)
                                    message_send=True
                        else :
                            message_fail_reason=f"interdit de parler à {channel_peuple_cible}"
                        if not message_send:
                            resultat=f"Message non envoyé à {channel_peuple_cible} par {channel_peuple_source}, à cause de: {message_fail_reason}"
                            logger.warning(resultat)
                            await message.channel.send(resultat)
    except:
        err = traceback.format_exc().replace("\n", "|")
        logger.error(err)

# on retrouve le logger de discord
logger = logging.getLogger('discord')

#on fabrique le bon handler + formatter pour les logs
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a+')
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    client.run(TOKEN)
except:
    err = traceback.format_exc().replace("\n", "|")
    logger.error(err)