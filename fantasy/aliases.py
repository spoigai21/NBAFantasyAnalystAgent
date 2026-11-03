#!/usr/bin/env python3
"""Map real player names to how Lloyd's auto-captioner mangles them.

Without this, searching "Buzelis" returns nothing because the transcript says
"Bazales". A silent zero-hit search is how a fabricated quote gets through.
Rebuild: python3 fantasy/aliases.py
"""
import sqlite3, re

ALIASES = {
 'Matas Buzelis':['Bazales','Bazala','Bazale','Buzelis','Matas Bala','Bazalis','Bisellis','Bales','Bisales','Bzalis','Buzzales'],
 'Collin Murray-Boyles':['Murray Boils','Colin Murray Boils','Murray Boyles','Murray-Boyles','CMB','Mari Boils','Colin Mari boils','Mari boils'],  # CMB is MY shorthand, 0 FTS hits by design
 'Giannis Antetokounmpo':['Jiannis','Giannis','Antetokounmpo','Yani Ant Kmpo','Yani Ant'],
 'Victor Wembanyama':['Wembanyama','Wemby','Wemi','Victoryama','Yama','Weby'],
 'Nikola Jokic':['Jokic','Jokich','Joker'],
 'Luka Doncic':['Doncic','Donic','Donuch','Luca'],
 'Shai Gilgeous-Alexander':['Gilgeous','Sheay','Shay'],
 'Jakob Poeltl':['Poeltl','Purle','Purdle','Yaka Purle','Yaka Purdle'],
 'Zach Edey':['Edey','Edy','Zack Edy','Zakit','Zack Edi','Zakid','Zakiti'],
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
 'Scottie Barnes':['Scottie Barnes','Scott Barnes','Barzie'],
 'Deandre Ayton':['Ayton','Aton','Eighton','DeAndre Aton'],
 'Jaren Jackson Jr.':['Jiren Jackson','Jaren Jackson'],
 'Cedric Coward':['Coward','the chicken','Cedric Carol'],
 'Kon Knueppel':['Knueppel','Kon Knueppel','Conquer Nipple'],  # captioner mangles him badly
 'Keyonte George':['Keyonte George','Kee George','Keshan George'],
 'Noa Essengue':['Essengue'],
 'Caleb Wilson':['Caleb Wilson'],
 'Leonard Miller':['Leonard Miller'],
 'Brandon Miller':['Brandon Miller'],
 'Jalen Williams':['Jaylen Williams','Jalen Williams','the Bronco'],
 'Jalen Suggs':['Jaylen Suggs','Jalen Suggs'],
 'Ivica Zubac':['Zubats','Zubac'],
 'Tyrese Maxey':['Maxey','Maxi','Tyres Maxi'],
 'Franz Wagner':['Fran Vagna','Franz Wagner','Vagna','Vagnner','Frzagna'],
 'Desmond Bane':['Desbane','Dez Bane','Desmond Bane'],
 'Anthony Edwards':['Anthony Edwards','Anthony Ed Woods'],  # NOT 'Ant ' — matches 'anti', 'want'
 'Karl-Anthony Towns':['Karl-Anthony Towns','Carlton Towns','KAT','Towns'],
 'Josh Giddey':['Giddey','Josh Giddey','Giddy','Joshy Giddy','Josh Giddy'],
 'Anthony Davis':['Anthony Davis','Anthony Tony Davis'],  # NOT 'AD' — collides with waiver 'add'/'ad'
 'Amen Thompson':['Amen Thompson','a men Thompson','Aymen','a man Thompson'],  # 'Amen' alone matches the word "amen"
 'Tari Eason':['Tari E','Trey Een','Tari Eason'],
 'Fred VanVleet':['Van Vleet','Vanble','Van Vele','VanVleet','Fleet'],
 'Jabari Smith Jr.':['Jabari Smith','Jabar Smith'],
 'Darius Garland':['Garland','Gallo Garland','Daryus Garland','Darius Gard'],
 'Donovan Clingan':['Clingan','Klingan','Don Klingan','Donnie Klingan','Donovan Klingan'],
 'Deni Avdija':['Avdija','Abdia','Abda','Abia','Denny Abda'],
 'Jalen Brunson':['Brunson','Jaylen Brunson','Bronson','Bunson'],
 'LaMelo Ball':['LaMelo','Melo Ball'],
 'Mikal Bridges':['Mikal Bridges','Mikuel Bridges','Muel Bridges'],
 'Ryan Rollins':['Ryan Rollins','Rollins'],
 'Darryn Peterson':['Darryn Peterson','Darren Peterson','Kmart Thong'],
 'Paul Reed':['Paul Reed','Reed'],
 'Paul George':['Paul George'],
 'Jeremiah Fears':['Fears','Jeremiah Fears','Jeremiah'],
 'Dejounte Murray':['Dejonte','Dejante','Dejonte Murray','Dejante Murray','Dejonte Mari'],  # real name -> 0 hits
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
