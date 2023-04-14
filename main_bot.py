# coding : utf-8

"""programme principal du bot discord "bot_test"
24 août 2022, Léo Gaspari
"""



import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
from discord.utils import get
import csv
import random
from time import time
import yt_dlp as youtube_dl
import asyncio
from os import path



file = path.dirname(__file__)
point = 0
ready = False
liste_exp_joueurs = []
fichier_csv_exp = file + "/exp_user_bot.csv"
levels = [200, 300, 450, 850, 1000, 1500, 2200, 3350, 4500, 5600, 6700, 7800, 8900, 10000]
max_levels = len(levels) - 1

default_intents = discord.Intents.default()
default_intents.members = True
default_intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=default_intents) #create commands

musics = {}


#####--Commands--#####

#-Commands !clear-#
@bot.command(brief='Cette commande permet de supprimer un nombre de messages donnés.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, number: int, mention: Optional[discord.User]):
	"""Cette fonction permet de supprimer un nombre de messages d'un utilisateur.

	Permission requise : `gérer les messages`
	
	Arguments:
	`number` (obligatoire): entier positif 
	`mention` (optionnel): mention utilisateur (@Utilisateur)
	"""
	messages = [message async for message in ctx.channel.history(limit=number + 1)]
	compteur = 0
	for each_message in messages:
			await each_message.delete()
			compteur += 1
	if len(messages) < number + 1: 

		#embed = discord.Embed(title="Information", description=f"{compteur - 1} message(s) supprimé(s).\nIl n'y a plus rien a supprimer.", color=0xffcd00)
		embed = create_embed("Information", f"{compteur - 1} message(s) supprimé(s).\nIl n'y a plus rien a supprimer.", 0xffcd00, None, None, None)
		await ctx.send(embed=embed, delete_after=5)
	else:

		#embed = discord.Embed(title="Information", description=f"{compteur - 1} message(s) supprimé(s).", color=0xffcd00)
		embed = create_embed("Information", f"{compteur - 1} message(s) supprimé(s).", 0xffcd00, None, None, None)
		await ctx.send(embed=embed, delete_after=5)


#-Commands !kick-#
@bot.command(brief="Cette commande permet d'exclure un utilisateur du serveur.")
@commands.has_permissions(kick_members = True)
async def kick(ctx, user : discord.User, *reason: Optional[str]):
	"""Cette commande permet d'exclure un'utilisateur utilisateur du serveur pour une certaine raison (optionnelle).
	
	Permissions requises : `Kick des membres`

	Arduments:
	`user`: Mention utilisateur (@Utilisateur)
	`reason` (optionnel): Texte
	"""
	reason = (" ".join(reason)) if len(reason) != 0 else "Non spécifiée"

	fields = [("Utilisateur", f"{user.name} aka {user.display_name}", True),
			  ("Expulsé par", f"{ctx.author.name}", True),
			  ("Raison", f"{reason}", False)]

	embed = create_embed(f"{user} a été expulsé", None, 0xf83030, datetime.utcnow(), fields, user.avatar)
	await ctx.send(embed=embed)
	await ctx.guild.kick(user, reason=reason)



#-Commands !ban-#
@bot.command(brief="Cette commande permet de bannir un membre du serveur.")
@commands.has_permissions(ban_members = True)
async def ban(ctx, member:discord.Member, *reason: Optional[str]):
	"""Cette comande permet de bannir un membre pour une raison (optionnelle).

	Permisson(s) requise(s): `Banir des membres`

	Arguments:
	`member`: Mention utilisateur (@Utilisateur)
	`reason` (optionnel): Texte
	"""
	reason = (" ".join(reason)) if len(reason) != 0 else "Non spécifiée"

	fields = [("Utilisateur", f"{member.name} aka {member.display_name}", True),
			  ("Banni par", f"{ctx.author.name}", True),
			  ("Raison", f"{reason}", False)]

	embed = create_embed(f"{member} a été banni", None, 0xf83030, datetime.utcnow(), fields, member.avatar)
	await ctx.send(embed=embed)
	await ctx.guild.ban(member, reason = reason)



#-Commands !unban-#
@bot.command(brief="Cette commande permet de bannir un membre du serveur.")
@commands.has_permissions(ban_members = True)
async def unban(ctx, user, *reason: Optional[str]):
	"""Cette comande permet de bannir un membre pour une raison (optionelle).

	Permisson(s) requise(s): `Banir des membres`

	Arguments:
	`member`: Utlisateur (ex: Utlisateur#1234)
	`reason` (optionnel): Texte
	"""
	reason = (" ".join(reason)) if len(reason) != 0 else "Non spécifiée"
	
	UserName, UserId = user.split("#")
	bannedUsers = [entry async for entry in ctx.guild.bans()]
	for i in bannedUsers:
		if i.user.name == UserName and i.user.discriminator == UserId:
			await ctx.guild.unban(i.user)
			fields = [("Utilisateur", f"{i.user.name} aka {i.user.display_name}", True),
						("Banni par", f"{ctx.author.name}", True),
						("Raison", f"{reason}", False)]
			
			embed = create_embed(f"{i.user.name}#{i.user.discriminator} a été unban.", None, 0xf83030, datetime.utcnow(), fields, i.user.avatar)
			await ctx.send(embed=embed)
			return
	embed = create_embed(None , f"L'utilisateur `{user}` n'est pas dans la liste des bannissements.", 0xf83030, None, None, None)
	await ctx.send(embed=embed)
	

#-Commands !user_info-#
@bot.command(name="userinfo", aliases=["memberinfo", "ui", "mi"], brief='Cette commande donne des informations sur un utilisateur (vous si non précisé).')
async def user_info(ctx, member: Optional[str]):
	"""Donne les information de `member`. Par défault,`target = auteur du message`"""
	target = ctx.author if member==None else await commands.MemberConverter().convert(ctx,member)

	fields = [("Name", str(target), True),
				("ID", target.id, True),
				("Bot?", target.bot, True),
				("Top role", target.top_role.mention, True),
				("Status", str(target.status).title(), True),
				("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
				("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				("Joined at", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				("Boosted", bool(target.premium_since), True)]

	embed = create_embed("User information", None, target.colour, datetime.utcnow(), fields, target.avatar)

	await ctx.send(embed=embed)


#-Commands !server_info-#
@bot.command(name="serverinfo", aliases=["guildinfo", "si", "gi"], brief='Cette commande donne les informations du serveur.')
async def server_info(ctx):
	"""Donne les informations du serveur"""
	statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
				len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
				len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
				len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

	bans = [entry async for entry in ctx.guild.bans(limit=2000)]
	fields = [("ID", ctx.guild.id, True),
				("Owner", ctx.guild.owner, True),
				#("Region", ctx.guild.region, True),
				("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				("Members", len(ctx.guild.members), True),
				("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
				("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
				("Banned members", len(bans), True),
				("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
				("Text channels", len(ctx.guild.text_channels), True),
				("Voice channels", len(ctx.guild.voice_channels), True),
				("Categories", len(ctx.guild.categories), True),
				("Roles", len(ctx.guild.roles), True),
				("Invites", len(await ctx.guild.invites()), True),
				("\u200b", "\u200b", True)]

	embed = create_embed("Server information", None, ctx.guild.owner.colour, datetime.utcnow(), fields, ctx.guild.icon)

	await ctx.send(embed=embed)	



#-Commande !close-#
@bot.command(brief='Cette commande permet de déconnecter le bot.')
@commands.has_permissions(administrator = True)
async def close(ctx):
	"""Cette fonction permet de déconnecter le bot.
	
	Permisson(s) requise(s): `Administrateur`
	"""
	global ready
	embed = create_embed("Bot Offline", "Le bot est maintenant hors ligne.", 0xffcd00, None, None, None)
	await ctx.send(embed=embed)
	ready = False
	await bot.close()



#-Commande !help-#
bot.remove_command("help")
@bot.command(name="help", brief="Commande d'aide", aliases=["aide"])
async def aide(ctx, cmd : Optional[str] = None):
	"""La commande `!help` à pour but d'aider l'utlisateur dans les commandes.
	Essayer `!help <commande>` pour plus d'informations sur une commande.
	"""
	if cmd == None: #Si aucune commande n'est précisé
		menu = menu_help_every_commands(ctx) #On affiche le menu d'aide de toutes les commandes
		await ctx.send(embed=menu) 

	else:
		if (command := get(bot.commands, name=cmd)): #Si la commande existe
			await cmd_help(ctx, command) #On affiche l'aide de la commande
		else:
			await ctx.send(embed=create_embed(None, ":rotating_light: Cette commande n'existe pas", 0xf83030, None, None, None)) #Sinon on affiche un message d'erreur


async def cmd_help(ctx, command):
	fields = [("Commande description", command.help, False)] #On ajoute la description de la commande
	embed = create_embed(f"Aide pour la commande `!{command}`",syntax(command), ctx.author.colour, None, fields, None) #On crée l'embed d'aide de la commande
	await ctx.send(embed=embed)


def syntax(command):
	cmd_and_aliases = " / !".join([("!"+str(command)), *command.aliases]) #On récupère la commande et ses alias avec une syntaxe du type : `!commande / !alias1 / !alias2`
	params = []

	for key, value in command.params.items(): #On récupère les paramètres de la commande
		if key not in ("self", "ctx"): #On ignore les paramètres `self` et `ctx`
			params.append(f"[{key}]" if "Optional" not in str(value) else f"(optional {key})") #On ajoute le paramètre entre crochet si il est  optionnel, sinon entre parenthèse

	params = " ".join(params) 

	return f"`{cmd_and_aliases} {params}`" #On retourne la syntaxe de la commande



def menu_help_every_commands(ctx):
	liste_commande = list(bot.commands) #On récupère la liste de toutes les commandes 
	fields = []
	for command in liste_commande: #Pour chaque commande
			fields.append((syntax(command), command.brief or "No description", False)) #On ajoute une ligne dans le menu d'aide avec la syntaxe de la commande, sa description et si elle n'en a pas, on met "No description"

	embed = create_embed("Menu d'aide.","Voici la liste de toutes les commandes existantes",ctx.author.colour, None, fields, ctx.guild.me.avatar) #On crée l'embed du panneau d'aide
	return embed


#-Commande !rank-#
@bot.command(brief="Cette commande permet de connaitre l'exp d'un membre.", aliases=["rang"])
async def rank(ctx, membre: Optional[discord.Member]):
	"""Cette fonction permet de connaitre le score et le rank d'un membre.
	
	Argument:
	`membre` (optionnel): Utilisateur (@Utilisateur)
	"""
	message = ctx.message.content.split(" ")
	if membre != None:
		exp, rang, level, next_level = info_carte_rang(membre)
	elif membre == None and len(message) == 1:
		membre = ctx.author
		exp, rang, level, next_level = info_carte_rang(membre)
	else:
		await ctx.send(embed=create_embed(None, ":rotating_light: Cet utilisateur ne fait pas parti du serveur (ou il s'agit d'une mention de rôle).", 0xf83030, None, None, None))
		return


	fields = [("Rang", (f"{rang}"+("er" if rang==1 else "eme")), True),("Level", level, True),("Progression", f"{exp} / {next_level}", False)]
	embed = create_embed(f"Rang de {membre.display_name}", None, membre.colour, None, fields, membre.avatar)
	await ctx.send(embed=embed)


def info_carte_rang(membre):
	"""Cette fonction permet de connaitre le score et le rank d'un membre, ainsi que le niveau et la progression à l'étape suivante."""
	
	ordre = tri_table()  #On trie le tableau des scores et on le récupère

	rank = trouve_rang(membre, ordre) #On trouve le rang du membre
	if rank != None: #si le membre est dans le tableau
		niveau = 0
		nb_exp = int(ordre[rank][0]) #On récupère le nombre d'expérience du membre

		for niv in range(len(levels)): #On trouve le niveau du membre
			niveau += levels[niv] #On ajoute le nombre d'expérience nécessaire pour passer au niveau suivant
			if nb_exp - levels[niv] >= 0: #Si le nombre d'expérience du membre est supérieur au nombre d'expérience nécessaire pour passer au niveau suivant
				nb_exp -= levels[niv] #On enlève le nombre d'expérience nécessaire pour passer au niveau suivant
			if int(ordre[rank][0]) < niveau: #Si le nombre d'expérience du membre est inférieur au nombre d'expérience nécessaire pour passer au niveau suivant
				level = niv #On récupère le niveau du membre
				next_level = levels[niv] #On récupère le nombre d'expérience nécessaire pour passer au niveau suivant
				return nb_exp, (rank + 1), level , next_level

		return nb_exp, (rank + 1), len(levels)-1 , ":infinity:"

	else: #si le membre n'est pas dans le tableau
		#On ouvre le fichier d'exp des membres et on ajoute le membre qui n'y est pas encore
		fic = open(fichier_csv_exp, "a", encoding="utf-8", newline="")
		objet = csv.writer(fic)
		objet.writerow([0, membre.id, time()])
		fic.close()

		#On réouvre le fichier pour récupérer les informations du membre (le rank ici)
		ordre = tri_table() #On trie le tableau des scores et on le récupère
		rank = trouve_rang(membre, ordre) #On trouve le rang du membre
		return 0, (rank + 1), 0, levels[0]


def trouve_rang(membre, ordre):
	"""Cette fonction permet de connaitre le rang d'un membre dans le serveur."""
	
	for rang in range(len(ordre)):
		if int(ordre[rang][1]) == membre.id:
			return rang

"""def trouve_level(ordre, rank):
	\"""Cette fonction permet de connaitre le niveau d'un membre dans le serveur.\"""
	niveau = 0
	nb_exp = int(ordre[rank][0]) #On récupère le nombre d'expérience du membre

	for niv in range(len(levels)): #On trouve le niveau du membre
		niveau += levels[niv] #On ajoute le nombre d'expérience nécessaire pour passer au niveau suivant
		if nb_exp - levels[niv] >= 0: #Si le nombre d'expérience du membre est supérieur au nombre d'expérience nécessaire pour passer au niveau suivant
			nb_exp -= levels[niv] #On enlève le nombre d'expérience nécessaire pour passer au niveau suivant
		if int(ordre[rank][0]) < niveau: #Si le nombre d'expérience du membre est inférieur au nombre d'expérience nécessaire pour passer au niveau suivant
			level = niv #On récupère le niveau du membre
			next_level = levels[niv] #On récupère le nombre d'expérience nécessaire pour passer au niveau suivant
			return level , next_level """


#-Commande !leaderboard-#
@bot.command(brief="Cette commande permet de connaitre le classement des membres.", aliases=["lb", "classement"])
async def leaderboard(ctx):
	"""Cette fonction permet de connaitre le classement des membres."""

	ordre = tri_table() #On trie le tableau des scores et on le récupère
	fields = []
	for rang in range(len(ordre)):
		membre = bot.get_user(int(ordre[rang][1]))
		fields.append((f"{rang+1}"+("er" if rang+1==1 else "eme")+f" - {membre.display_name}:", f"{ordre[rang][0]}exp", False))

	embed = create_embed("Classement des membres", None, 0x00ffa6, None, fields, ctx.guild.me.avatar)
	await ctx.send(embed=embed)


def tri_table():
	"""Cette fonction permet de trier le tableau des scores des membres."""
	table = tableCSV_t(fichier_csv_exp)
	ordre = sorted(table, reverse=True, key=lambda colonne: int(colonne[0])) #On trie le tableau par ordre décroissant de l'expérience
	return ordre



#-Commande !gift-#
@bot.command(brief="Cette commande permet de donner de l'exp à un membre/une mention.", aliases=["don"])
@commands.has_permissions(administrator=True)
async def give(ctx, membre: str, nb_points: int):
	"""Cette fonction permet de donner de l'exp à un membre.

	Permissions requises : `Administrateur`
	
	Argument:
	`membre`: Utilisateur ou mention (@Utilisateur ou @mention)
	`nb_points`: Nombre de points à donner
	"""
	niv = 0
	table = tableCSV_t(fichier_csv_exp) #tableau de la table csv
	if membre != "@everyone": #si le membre n'est pas @everyone
		role = ctx.guild.get_role(int(membre[3:-1]))
	else:
		role = discord.utils.get(ctx.guild.roles, name=membre)

	if role != None or membre == "@everyone": #si le membre est un rôle ou @everyone
		await ctx.send(embed=create_embed("Give", f"{ctx.author.mention} a donné {nb_points} point(s) à {membre}", role.color, None, None, ctx.author.avatar))
		for ligne in range(len(table)):
			niv = trouve_level(int(table[ligne][0])) #on récupère le niveau du membre

			table[ligne][0] = int(table[ligne][0]) + nb_points #on ajoute le nombre de points au membre
			if niv != max_levels: #si le membre est déjà au niveau max
				niv2 = trouve_level(int(table[ligne][0])) #on récupère le nouveau niveau du membre après l'ajout des points
				if niv2 > niv: #si le niveau du membre a augmenté
					nom = bot.get_user(int(table[ligne][1]))
					if niv2 == 5: #si le niveau du membre est 5
						role = discord.utils.get(ctx.guild.roles, name="Giga bg")
						await ctx.send(embed=create_embed(":tada::tada: Félicitations ! :tada::tada:", f"{nom.display_name} vient de passer level {level} ! Il est donc félicité et obtient le rôle {role.mention} !", role.colour, None, None, nom.avatar))
						await nom.add_roles(role)
					elif niv2 == max_levels: #si le niveau du membre est maximum
						await ctx.send(embed=create_embed(f"Félicitation {nom.display_name}", f"Tu es désormais level maximum !", nom.colour, None, None, nom.avatar))
					else:
						await ctx.send(embed=create_embed(f"Félicitation {nom.display_name}", f"Tu es désormais level {niv2} !", nom.colour, None, None, nom.avatar))
			
		
		fic = open(fichier_csv_exp, "w", encoding="utf-8", newline="") #ouverture du fichier csv en écriture
		objet = csv.writer(fic) #création d'un objet csv
		objet.writerows(table) #écriture du tableau dans le fichier csv
		fic.close() #fermeture du fichier csv
		return
	else:
		guild = ctx.guild
		member = guild.get_member(int(membre[2:-1]))
		for ligne in range(len(table)):
			if int(table[ligne][1]) == member.id:
				niv = trouve_level(int(table[ligne][0])) #on récupère le niveau du membre
				table[ligne][0] = int(table[ligne][0]) + int(nb_points) #on ajoute les points au membre
				fic = open(fichier_csv_exp, "w", encoding="utf-8", newline="") #ouverture du fichier csv en écriture
				objet = csv.writer(fic) #création d'un objet csv
				objet.writerows(table) #écriture du tableau dans le fichier csv
				fic.close() #fermeture du fichier csv
				await ctx.send(embed=create_embed("Give", f"{ctx.author.mention} a donné {nb_points} points à {member.mention}", member.color, None, None, member.avatar))
				action, role, level = gere_recompenses_niv(member) #action à effectuer sur le rôle du membre, rôle à modifier, niveau du membre
				if action == "add":
					await ctx.send(embed=create_embed(":tada::tada: Félicitations ! :tada::tada:", f"{member.display_name} vient de passer level {level} ! Il est donc félicité et obtient le rôle {role.mention} !", role.colour, None, None, member.avatar))
					await member.add_roles(role)
				elif action == "remove":
					await member.remove_roles(role)

					if level != niv:
						await ctx.send(embed=create_embed(f"Félicitation {member.display_name}", f"Tu es désormais level {level} !", member.colour, None, None, member.avatar))
				return


ytdl = youtube_dl.YoutubeDL()
class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

def play_song(client, queue, song):
	source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
	
	def next(_):
		if len(queue) > 0:
			new_song = queue[0]
			del queue[0]
			play_song(client, queue, new_song)
		else:
			asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)
			
	client.play(source, after=next)
	

#-Commands !playmusic-#
@bot.command(brief="Cette commande permet au bot de rejoindre le salon vocal de l'utilisateur et de jouer la musique voulu.")
async def playmusic(ctx, url: str):
	"""Cette commande permet au bot de rejoindre le salon vocal de l'utilisateur et de jouer la musique donnée.

    Argument:
    `url`: Lien vers la musique à jouer (YouTube ou autre plateforme de streaming musical)
	"""

	"""voice_channel_connected = ctx.author.voice

	if voice_channel_connected is not None:
		voice_channel = voice_channel_connected.channel
		client = await voice_channel.connect()
		video = Video(url)
		musics[ctx.guild].append(video)
		await ctx.send(f"Je lance : {video.url}")
		play_song(client, video, video)"""

	client = ctx.guild.voice_client

	if client and client.channel:
		video = Video(url)
		musics[ctx.guild].append(video)
	else:
		channel = ctx.author.voice.channel
		video = Video(url)
		musics[ctx.guild] = []
		client = await channel.connect()
		await ctx.send(f"Je lance : {video.url}")
		play_song(client, musics[ctx.guild], video)

"""		await ctx.send(f"En train de jouer la musique dans le salon vocal `{voice_channel.name}`.")
	else:
		await ctx.send("Vous n'êtes pas dans un salon vocal.", delete_after=15)"""


#-Commands !stopmusic-#
@bot.command(brief="Cette commande permet au bot de quitter le salon vocal et d'arrêter la musique.")
async def stopmusic(ctx):
	"""Cette commande permet au bot de quitter le salon vocal et d'arrêter la musique.
	"""
	client = ctx.voice_client
	if client is not None:
		await client.disconnect()
		musics[ctx.guild] = []
		await ctx.send("Musique arrêtée.")
	else:
		await ctx.send("Le bot n'est pas dans un salon vocal.")




#----------------------------------------------------------------------------------------------------#


#####--Events--#####

#bot conecté
@bot.event
async def on_ready():
	"""Quand le bot est prêt, on envoie un message dans le salon général"""
	global ready
	if ready == False:
		ready = True
		general_channel: discord.TextChannel = bot.get_channel(1011574336399880294)
		fields = [("Nom", "Bot test", True),("Créateur", "Skyway#1798", True),("Utilité","modération, commandes, exp", True)]
		embed = create_embed("Bot Online !", "Ce bot intègre de nombreuses fonctionnalités permettant la modération ainsi que des fonctionnalité à un but récréatif.", 0x00ffa6, None, fields, None)
		await general_channel.send(embed=embed)


#quand un membre rejoint le serveur
@bot.event
async def on_member_join(member: discord.Member):
	"""Quand un membre rejoint le serveur, on lui donne le rôle Testeurs et on l'ajoute au tableau des scores"""
	role = discord.utils.get(member.guild.roles, name="Testeurs")
	await member.add_roles(role)

	ordre = tri_table() #On trie le tableau des scores et on le récupère

	rank = trouve_rang(member, ordre) #On trouve le rang du membre
	if rank != None:
		fic = open(fichier_csv_exp, "a", encoding="utf-8", newline="")
		objet = csv.writer(fic)
		objet.writerow([0, member.id, time()])
		fic.close()

	general_channel: discord.TextChannel = bot.get_channel(1011574336399880294)
	embed = create_embed("Annonce de bienvenue", f"Bienvenue à toi{member.mention}. Tu fais désormais parti des {role}",0x00ffa6,datetime.utcnow(),None, member.avatar)
	await general_channel.send(embed=embed)
	


#quand un message est envoyé
@bot.event
async def on_message(message):
	
	points_message = random.randint(2,6)
	temps = time()
	
	if message.author.id != 1011574876148084866: #id du bot
		if "https://discord.com/channels/" in message.content or "https://media.discordapp.net/attachments/" in message.content or "https://tenor.com/view/" in message.content:
			await message.delete()
			await message.channel.send(f"{message.author.mention}, tu ne peux pas poster de liens/memes dans ce salon.", delete_after=5)
			return

		member = message.author #id du membre ayant envoyé le message
		table = tableCSV_t(fichier_csv_exp) #tableau de la table csv
		if len(table) != 0: #si la table n'est pas vide
			for ligne in range(len(table)): #pour chaque ligne du tableau
				if int(table[ligne][1]) == member.id: #si l'id du membre ayant envoyé le message est égal à l'id du membre dans la table
					if (temps - float(table[ligne][2])) > 60: #si le temps écoulé depuis le dernier message est supérieur à 60 secondes
						niv = trouve_level(int(table[ligne][0])) #on récupère le niveau du membre
						points_membre = int(table[ligne][0]) #points du membre
						table[ligne][0] = points_membre + points_message #ajout des points du message
						table[ligne][2] = temps #remplacement du temps par le temps actuel
						fic = open(fichier_csv_exp, "w", encoding="utf-8", newline="") #ouverture du fichier csv en écriture
						objet = csv.writer(fic) #création d'un objet csv
						objet.writerows(table) #écriture du tableau dans le fichier csv
						fic.close() #fermeture du fichier csv

						action, role, level = gere_recompenses_niv(member) #action à effectuer sur le rôle du membre, rôle à modifier, niveau du membre
						if action == "add":
							general_channel: discord.TextChannel = bot.get_channel(1011574336399880294)
							await general_channel.send(embed=create_embed(":tada::tada: Félicitations ! :tada::tada:", f"{member.mention} vient de passer level {level} ! Il est donc félicité et obtient le rôle {role.mention} !", role.colour, None, None, member.avatar))
							await member.add_roles(role)
						elif action == "remove":
							await member.remove_roles(role)
						
						if level != niv:
							await message.channel.send(embed=create_embed(f"Félicitation {member.mention}", f"Tu es désormais level {level} !", member.colour, None, None, member.avatar))

						await bot.process_commands(message) #traitement des commandes
						return
					else: #si le temps écoulé depuis le dernier message est inférieur à 60 secondes
						await bot.process_commands(message) #traitement des commandes
						return

			table.append([points_message, member.id, temps]) #ajout d'une ligne dans le tableau
			fic = open(fichier_csv_exp, "w", encoding="utf-8", newline="") #ouverture du fichier csv en écriture
			objet = csv.writer(fic) #création d'un objet csv
			objet.writerows(table) #écriture du tableau dans le fichier csv
			fic.close()
			await bot.process_commands(message)

		else: 
			fic = open(fichier_csv_exp, "a", encoding="utf-8", newline="") #ouverture du fichier csv en écriture
			objet = csv.writer(fic) #création d'un objet csv
			objet.writerow([points_message, member.id, temps]) #écriture de la ligne à la fin dans le fichier csv
			fic.close() #fermeture du fichier csv
			await bot.process_commands(message) #traitement des commandes

def trouve_level(point):
	for niv in range(len(levels)):
		if point < levels[niv]:
			return niv
		elif point >= levels[niv]:
			point -= levels[niv]
	return max_levels
		

def tableCSV_t(nom_fichier : str) -> list:
    """Cette fonction va renvoyer une table de dictionnaire, issue du contenu de fichier.csv."""
    f = open(nom_fichier, "r", encoding="utf-8")
    table_t = list(csv.reader(f))
    f.close()
    return table_t

def gere_recompenses_niv(member):
	exp, rang, level, next_level = info_carte_rang(member)
	if level >= 5:
		role = discord.utils.get(member.guild.roles, name="Giga bg")
		return "add", role, 5
	else:
		role = discord.utils.get(member.guild.roles, name="Giga bg")
		return "remove", role, level


#-Gestionnaire d'erreurs-#
"""@bot.event
async def on_command_error(ctx, error):
	colour_error = 0xf83030
	if isinstance(error, commands.MissingRequiredArgument):
		command = ctx.message.content
		liste_commande = list(bot.commands)
		for commande in liste_commande:
			if command[1:] == str(commande):
				help_command = syntax(commande)
				field = [("Description de la commande", commande.help or "No description", False)]
				break
		embed = create_embed(None, f"Il manque des arguments! Essaye d'utiliser la commande comme ça:\n{help_command}",colour_error, None, field, None)
		await ctx.send(embed=embed)
	elif isinstance(error, commands.MissingPermissions):
		embed = create_embed(None, ":rotating_light: Vous n'avez pas les permissions pour faire cette commande.",colour_error, None, None, None)
		await ctx.send(embed=embed)
	if isinstance(error, commands.CommandNotFound):
		
		embed = create_embed(None, ":rotating_light: Commande inconnue.",colour_error, None, None, None)
		await ctx.send(embed=embed)
	if isinstance(error, commands.UserNotFound):
		embed = create_embed(None, ":rotating_light: Utilisateur inconnu.",colour_error, None, None, None)
		await ctx.send(embed=embed)
	if isinstance(error, commands.MemberNotFound):
		fields = [("Cause(s) possible(s):","Cet utilisateur n'existe pas ou ne fait pas partie du serveur.\nEssayez avec une orthographe comme ceci : `@mention`.", False)]
		embed = create_embed(None, ":rotating_light: Membre introuvable.",colour_error, None, fields, None)
		await ctx.send(embed=embed)
	if isinstance(error, commands.CommandInvokeError):
		message = ctx.message.content
		command = message.split(" ")[0]
		liste_commande = list(bot.commands)
		for commande in liste_commande:
			if command[1:] == str(commande):
				help_command = syntax(commande)
				field = [("Description de la commande", commande.help or "No description", False)]
				break
		embed = create_embed(None, f"Commande invalide, essaie de l'utiliser comme ça:\n{help_command}",colour_error, None, field, None)
		await ctx.send(embed=embed)
	if isinstance(error, commands.BadArgument):
		message = ctx.message.content
		command = message.split(" ")[0]
		liste_commande = list(bot.commands)
		for commande in liste_commande:
			if command[1:] == str(commande):
				help_command = syntax(commande)
				field = [("Description de la commande", commande.help or "No description", False)]
				break
		embed = create_embed(None, f"Mauvais arguments! Ils sont peut-être inversés :upside_down: ? Essaye d'utiliser la commande comme ça:\n{help_command}",colour_error, None, field, None)
		await ctx.send(embed=embed)"""


#----------------------------------------------------------------------------------------------------#


def create_embed(title, description, colour, timestamp, fields, thumbnail):
	"""Cette fonction permet de créer et d'envoyer une embed avec les informations mises en paramètre."""
	embed = discord.Embed(title=title, description=description, colour=colour, timestamp=timestamp)
	if thumbnail != None:
		embed.set_thumbnail(url=thumbnail)
	if fields != None:
		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)
	return embed



bot.run("") #ajouter le token de votre bot