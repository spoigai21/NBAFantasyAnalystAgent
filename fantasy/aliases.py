#!/usr/bin/env python3
"""Map real player names to how Lloyd's auto-captioner mangles them.

Without this, searching "Buzelis" returns nothing because the transcript says
"Bazales". A silent zero-hit search is how a fabricated quote gets through.
Rebuild: python3 fantasy/aliases.py
"""
import sqlite3, re

ALIASES = {
 'Matas Buzelis':['Bazales','Bazala','Bazale','Buzelis','Matas Bala','Bazalis','Bisellis','Masalis','Bizales','Bales','Bisales','Bzalis','Buzzales'],
 'Collin Murray-Boyles':['Murray Boils','Colin Murray Boils','Murray Boyles','Murray-Boyles','CMB','Mari Boils','Colin Mari boils','Mari boils','CMBB','Colinary Boils','Colin Marary Boils'],  # CMB is MY shorthand, 0 FTS hits by design
 'Giannis Antetokounmpo':['Jiannis','Giannis','Antetokounmpo','Yani Ant Kmpo','Yani Ant','Yanni'],
 'Victor Wembanyama':['Wembanyama','Wemby','Wemi','Victoryama','Yama','Weby','Webby','Wmanyama','WBY','WMY','Wimby'],  # 'Wmanyama','WBY' from 5 Nov Thursday recap
 'Nikola Jokic':['Jokic','Jokich','Joker'],
 'Luka Doncic':['Doncic','Donic','Donuch','Luca'],
 'Shai Gilgeous-Alexander':['Gilgeous','Sheay','Shay'],
 'Jakob Poeltl':['Poeltl','Purle','Purdle','Yaka Purle','Yaka Purdle','Yakaple'],  # NOT mine -- tracked because Lloyd ties his revival to Murray-Boyles's outlook
 'Zach Edey':['Edey','Edy','Zack Edy','Zakit','Zack Edi','Zakid','Zakiti','Zack Ed','Zack Edit'],
 'Darius Acuff Jr.':['Acuff','Akoff','Akuff','Akaf','Auff'],
 'Tyrese Haliburton':['Haliburton','Hallebertton','Hallebert','Torres Hallebertton'],
 'AJ Dybantsa':['Dybantsa','Debansa','Debanser','Deansa','Dybansa'],
 'Paolo Banchero':['Banchero','Bonero','Bunker'],
 'Jonathan Kuminga':['Kuminga','Kaminga','Johnny Kaminga'],
 'Alperen Sengun':['Sengun','Shenu'],
 'Alex Sarr':['Alex Sar','Alexar','Sarr','Ansar'],
 'Walker Kessler':['Kessler','Kesler','Walker Kesler'],
 "Day'Ron Sharpe":['Dron Sharp','Don Sharp','Sharpe','Sharpie'],
 'Rui Hachimura':['Hachimura','Hutchimura','Ruie','Ruy Hachimura'],
 'Zach LaVine':['LaVine','Lavine','Zack Lavine'],
 'Domantas Sabonis':['Sabonis','Saboni','Deanna Sabonis','Demon Sabonis'],
 'Trae Young':['Trae Young','Trey Young','Ice Trae'],
 'Kawhi Leonard':['Kawhi','Kawawaii','Kawai','Kawhai'],
 'Isaiah Hartenstein':['Hartenstein','Isaiah Hartenstein'],
 'Dennis Schroder':['Schroder','Schroer','Shruder','Schröder'],
 'Scottie Barnes':['Scottie Barnes','Scott Barnes','Barzie','Barnesy'],  # NOT mine -- tracked because Barnes OUT drives Murray-Boyles usage
 'Deandre Ayton':['Ayton','Aton','Eighton','DeAndre Aton'],
 'Jaren Jackson Jr.':['Jiren Jackson','Jaren Jackson'],
 'Cedric Coward':['Coward','the chicken','Cedric Carol'],
 'Kon Knueppel':['Knueppel','Kon Knueppel','Conquer Nipple','Coniple','Koniple'],  # captioner mangles him badly; 'Coniple' = 5 Nov mailbag, drives Brandon Miller's usage
 # ⚠ 5 Nov 2026: 'Keshan George' was mapped here and it is KYSHAWN George (WAS) --
 # 10 of its hits are in the HOU-WAS team preview. User caught the misattribution.
 'Keyonte George':['Keyonte George','Keonte George','Kee George'],
 'Kyshawn George':['Kyshawn George','Keshan George','Kishan George'],
 'Noa Essengue':['Essengue'],
 'Caleb Wilson':['Caleb Wilson'],
 'Leonard Miller':['Leonard Miller'],
 'Brandon Miller':['Brandon Miller'],
 'Jalen Williams':['Jaylen Williams','Jalen Williams','the Bronco'],
 'Jalen Suggs':['Jaylen Suggs','Jalen Suggs'],
 'Ivica Zubac':['Zubats','Zubac'],
 'Tyrese Maxey':['Maxey','Maxi','Tyres Maxi'],
 'Franz Wagner':['Fran Vagna','Franz Wagner','Vagna','Vagnner','Frzagna','France Vagner'],
 'Desmond Bane':['Desbane','Dez Bane','Desmond Bane'],
 'Anthony Edwards':['Anthony Edwards','Anthony Ed Woods'],  # NOT 'Ant ' — matches 'anti', 'want'
 'Karl-Anthony Towns':['Karl-Anthony Towns','Carlton Towns','KAT','Towns'],
 'Josh Giddey':['Giddey','Josh Giddey','Giddy','Joshy Giddy','Josh Giddy'],
 'Anthony Davis':['Anthony Davis','Anthony Tony Davis'],  # NOT 'AD' — collides with waiver 'add'/'ad'
 'Amen Thompson':['Amen Thompson','a men Thompson','Aymen','a man Thompson','the men Thompson'],  # 'Amen' alone matches the word "amen"
 'Tari Eason':['Tari E','Trey Een','Tari Eason'],
 'Fred VanVleet':['Van Vleet','Vanble','Van Vele','VanVleet','Fleet'],
 'Jabari Smith Jr.':['Jabari Smith','Jabar Smith'],
 'Darius Garland':['Garland','Gallo Garland','Daryus Garland','Darius Gard'],
 'Donovan Clingan':['Clingan','Klingan','Don Klingan','Donnie Klingan','Donovan Klingan'],
 'Deni Avdija':['Avdija','Abdia','Abda','Abia','Denny Abda'],
 'Jalen Brunson':['Brunson','Jaylen Brunson','Bronson','Bunson'],
 'LaMelo Ball':['LaMelo','Melo Ball'],
 'Mikal Bridges':['Mikal Bridges','Mikuel Bridges','Muel Bridges'],
 'Ryan Rollins':['Ryan Rollins','Rollins','Rollands','Rolland'],  # 'Rolland' = 10 Nov Tuesday recap
 'Darryn Peterson':['Darryn Peterson','Darren Peterson','Kmart Thong'],
 'Paul Reed':['Paul Reed','Reed'],
 'Paul George':['Paul George'],
 'Jeremiah Fears':['Fears','Jeremiah Fears','Jeremiah','Fierce'],  # 'Fierce' = 4 Nov recap
 # 5 Nov 2026 mailbag -- user identified both of these for me. 'Superman' is Lloyd's
 # nickname for Ware and it was returning ZERO hits on his real name for weeks.
 "Kel'el Ware":['Superman','Ware','Kelel Ware','Callware','Callaway','Superman wear'],
 'Jusuf Nurkic':['Nerkage','Nerkish','Yousef Nerkish','Ysef Nerkage'],
 'Brayden Burries':['Burries','Brayden Burries','Braden Barry'],  # 'Barry's' in 5 Nov mailbag
 # 9 Nov 2026 buy-low show -- new names. Captioner: 'Damen Lillard', 'Lilard', 'Kobe White'
 # (= COBY White, NOT Kobe), 'Tai Jerome'/'milk Jerome', 'Nars Reed', 'Scott Barnes'/'Scotty Barnes'.
 # ⚠⚠ REVERSED 11 NOV 2026 -- 'Dame' IS NOW IN, AND HERE IS WHY THE 9 NOV DECISION WAS WRONG.
 # On 9 Nov I left bare 'Dame' out because it matches 'Dame Mitchell' (= DAVION Mitchell) in the
 # 8 Nov recap, and wrote that 'Lillard'/'Lilard' "already catch every real passage, since Lloyd
 # names him before using the nickname." THE 10 NOV TUESDAY RECAP BROKE THAT: its entire Dame
 # paragraph ("Dame continues to play much better in only 24 minutes... I feel like he's going to
 # get to top 30 this year") never says Lillard once, so it was UNREACHABLE under his real name --
 # the exact silent-zero-hit failure rule 19 exists to prevent, on the player I am actively
 # trading for. Measured cost of adding it: 'Dame' = 20 hits, 'Dame Mitchell' = 1. So it buys 20
 # passages and risks ONE known-contaminated one, which is logged below so it can be checked.
 # ⚠ THE ONE BAD PASSAGE: 8 Nov Sunday recap, 'Dame Mitchell' = Davion Mitchell, NOT Lillard.
 # Davion is tracked separately so the collision is visible rather than silent.
 'Damian Lillard':['Damian Lillard','Damen Lillard','Lillard','Lilard','Dame Lillard','Dame'],
 'Davion Mitchell':['Davion Mitchell','Dame Mitchell','Davian Mitchell'],
 'Coby White':['Kobe White','Coby White','Koby White'],
 'Ty Jerome':['Tai Jerome','Ty Jerome','milk Jerome','Jerome'],
 'Naz Reid':['Nars Reed','Naz Reid','Nars Reid','Nas Reid','Naz Reed'],
 'Jalen Johnson':['Jaylen Johnson','Jalen Johnson'],
 # ⚠ 9 Nov 2026: Keegan Murray was NEVER in this file -- my own IR player, every search
 # silently returned nothing. NOT bare 'Murray': it collides with Dejounte, Jamal Murray
 # and Murray-Boyles. Lloyd says the full name ("Keonte, not Kee, Keegan Murray").
 # ⚠ 10 Nov 2026: 'Kambooza' = CAMERON BOOZER (MEM rookie, rostered by 'Why so serious',
 # 36.6/g on 32.1 mpg). I could not identify the name on first read of the Monday recap.
 # He matters because he is the named competitor for Zach Edey's frontcourt touches.
 'Cameron Boozer':['Kambooza','Cam Boozer','Cameron Boozer','Boozer','Kam Booza'],
 'Keegan Murray':['Keegan Murray','Keagan Murray','Kegan Murray'],
 'Dejounte Murray':['Dejonte','Dejante','Dejonte Murray','Dejante Murray','Dejonte Mari','Deontay Murray','Deonte Murray','Deonte M','Jonte Murray'],  # 'Jonte Murray' = 9 Nov Monday recap, 'the Jonte Murray'  # real name -> 0 hits; 'Deonte Murray' = 8 Nov Sunday recap, the marginalization note
}
con=sqlite3.connect("fantasy/league.db")
con.execute("ATTACH DATABASE 'fantasy/lloyd.db' AS lloyddb")  # gitignored transcript index
con.executescript("""
DROP TABLE IF EXISTS name_aliases;
CREATE TABLE name_aliases(player TEXT, alias TEXT, hits INT);
CREATE INDEX idx_alias ON name_aliases(player);
""")
n=0
for player,als in ALIASES.items():
    for a in als:
        q=a.replace('"','')
        try:
            hits=con.execute("SELECT COUNT(*) FROM lloyddb.lloyd_fts WHERE lloyd_fts MATCH ?",
                             (f'"{q}"',)).fetchone()[0]
        except Exception:
            hits=0
        con.execute("INSERT INTO name_aliases VALUES (?,?,?)",(player,a,hits))
        n+=1
con.commit()
print(f"{n} aliases stored")
print("\nplayers whose REAL name finds nothing but an alias does (the trap):")
for p,als in ALIASES.items():
    sur=p.split()[-1]
    real=con.execute("SELECT COUNT(*) FROM lloyddb.lloyd_fts WHERE lloyd_fts MATCH ?",(f'"{sur}"',)).fetchone()[0]
    best=con.execute("SELECT alias,hits FROM name_aliases WHERE player=? ORDER BY hits DESC LIMIT 1",(p,)).fetchone()
    if real==0 and best and best[1]>0:
        print(f"   {p:<26} '{sur}' -> 0 hits,  '{best[0]}' -> {best[1]}")
con.close()
