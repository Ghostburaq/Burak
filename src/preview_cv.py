# -*- coding: utf-8 -*-
"""Maßstabsgetreue PNG-Vorschau des CV (A4 @150dpi) - echte Daten."""
from PIL import Image, ImageDraw, ImageFont

DPI = 150; CM = DPI / 2.54
W, H = int(21.0*CM), int(29.7*CM)
ML = int(1.3*CM); MR = W-int(1.3*CM)
SIDE_W = int(6.0*CM); SX0, SX1 = ML, ML+SIDE_W; MX0 = SX1

NAVY=(22,42,67); STEEL=(44,95,138); INK=(34,38,43); GREY=(107,114,128)
WHITE=(255,255,255); LIGHT=(232,236,241); SIDE=(238,242,246)
GOLD=(154,122,46); GOLDBG=(251,241,216); LINE=(201,210,220); ACC=(143,180,217)

F="/usr/share/fonts/truetype/liberation/"
def font(sz,b=False,i=False):
    n="LiberationSans-"+("BoldItalic" if b and i else "Bold" if b else "Italic" if i else "Regular")
    return ImageFont.truetype(F+n+".ttf", int(sz))

img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)

def text(x,y,s,fnt,fill=INK,spacing=0,caps=False):
    if caps: s=s.upper()
    if spacing:
        cx=x
        for ch in s:
            d.text((cx,y),ch,font=fnt,fill=fill); cx+=d.textlength(ch,font=fnt)+spacing
        return cx
    d.text((x,y),s,font=fnt,fill=fill); return x+d.textlength(s,font=fnt)

def chip(x,y,s,fnt,fg,bg,pad=6):
    w=d.textlength(s,font=fnt); d.rounded_rectangle([x,y-2,x+w+pad*2,y+fnt.size+4],radius=4,fill=bg)
    d.text((x+pad,y),s,font=fnt,fill=fg); return x+w+pad*2

def gold(x,y,s,fnt):
    w=d.textlength("〈"+s+"〉",font=fnt); d.rectangle([x,y-1,x+w,y+fnt.size+2],fill=GOLDBG)
    d.text((x,y),"〈"+s+"〉",font=fnt,fill=GOLD); return x+w

# HEADER
HB=int(2.55*CM); d.rectangle([ML,0,MR,HB],fill=NAVY)
text(ML+int(0.5*CM),int(0.45*CM),"BURAK ",font(34,b=True),WHITE,spacing=3)
xx=ML+int(0.5*CM)+d.textlength("BURAK ",font=font(34,b=True))+(3*len("BURAK "))
text(xx,int(0.45*CM),"ÜÇÖZ",font(34,b=True),ACC,spacing=3)
text(ML+int(0.5*CM),int(1.42*CM),"SALES ENGINEER · TECHNISCHER VERTRIEB",font(13),LIGHT,spacing=2)
text(ML+int(0.5*CM),int(1.92*CM),"Investitionsgüter · Neukundenakquise · Gebietsverantwortung",font(10.5),(159,178,199),spacing=1)

by0=HB+int(0.25*CM)
d.rectangle([SX0,by0,SX1,H-int(1.1*CM)],fill=SIDE)
sx=SX0+int(0.42*CM); sw=SIDE_W-int(0.84*CM)

def s_title(y,s):
    text(sx,y,s,font(12,b=True),NAVY,spacing=2,caps=True)
    yy=y+int(0.52*CM); d.line([sx,yy,SX1-int(0.42*CM),yy],fill=LINE,width=2); return yy+int(0.18*CM)
def s_field(y,label,val,is_gold=False):
    text(sx,y,label.upper(),font(9,b=True),STEEL,spacing=1); y+=int(0.38*CM)
    if is_gold: gold(sx,y,val,font(10,i=True))
    else: text(sx,y,val,font(10),INK)
    return y+int(0.5*CM)

# Foto
fy=by0+int(0.3*CM)
d.rectangle([sx,fy,sx+sw,fy+int(2.3*CM)],outline=(183,194,206),width=2)
text(sx+sw/2-18,fy+int(0.95*CM),"Foto",font(11,i=True),GREY)
text(sx+sw/2-44,fy+int(2.45*CM),"optional · CH-üblich",font(8,i=True),GREY)
y=fy+int(3.0*CM)
y=s_title(y,"Kontakt")
y=s_field(y,"Adresse","Im Abt 9a, 8240 Thayngen")
y=s_field(y,"Telefon","+41 76 202 01 70")
y=s_field(y,"E-Mail","b.s.uecoez@gmail.com")
y=s_field(y,"LinkedIn","Profil-URL ergänzen",is_gold=True)
y+=int(0.1*CM); y=s_title(y,"Persönliches")
y=s_field(y,"Geburtsdatum","29.03.1986")
y=s_field(y,"Nationalität","deutsch")
y=s_field(y,"Aufenthalt CH","Ausweis C / B",is_gold=True)
y=s_field(y,"Führerausweis","Kat. B")
y+=int(0.1*CM); y=s_title(y,"Sprachen")
for n,l in [("Deutsch","Muttersprache"),("Englisch","verhandlungssicher"),("Französisch","gute Kenntnisse"),("Türkisch","fliessend"),("Schweizerdeutsch","gutes Verständnis")]:
    text(sx,y,n,font(9.5,b=True),INK); y+=int(0.36*CM)
    text(sx,y,l,font(8.5),GREY); y+=int(0.4*CM)
y+=int(0.05*CM); y=s_title(y,"Kompetenzen")
for sk in ["Techn. Vertrieb Investitionsg.","Neukundenakquise (Hunter)","Beratungsverkauf","Angebots- & Projektabwicklung","Verhandlung & Abschluss","CRM · MS Office"]:
    text(sx,y,"▪",font(9.5),STEEL); text(sx+int(0.4*CM),y,sk,font(9),INK); y+=int(0.42*CM)
y+=int(0.05*CM); y=s_title(y,"Zusatzqualifikationen")
for q in ["EMV-Fachkraft","Elektrofachkraft","BetrSichV","DGUV"]:
    text(sx,y,"▪",font(9.5),STEEL); text(sx+int(0.4*CM),y,q,font(9),INK); y+=int(0.4*CM)

# MAIN
mx=MX0+int(0.5*CM); mw=MR-mx-int(0.2*CM)
def m_title(y,s):
    text(mx,y,s,font(14,b=True),NAVY,spacing=2,caps=True)
    yy=y+int(0.62*CM); d.line([mx,yy,MR-int(0.2*CM),yy],fill=NAVY,width=3); return yy+int(0.22*CM)
def wrap(s,fnt,maxw):
    words=s.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

my=by0+int(0.3*CM); my=m_title(my,"Kurzprofil")
prof=("Erfahrener Sales Engineer mit über 10 Jahren B2B-Erfahrung im technischen Vertrieb "
      "erklärungsbedürftiger Investitionsgüter. Fundierte technische Basis (Elektrotechnik B.Eng., "
      "EMV, Mess- & Analysesysteme) kombiniert mit ausgeprägter Hunter-Mentalität in der aktiven "
      "Neukundenakquise. Stärken im consultativen Verkauf, in der Projektabwicklung bis zur "
      "Inbetriebnahme und im Aufbau langfristiger Kundenbeziehungen.")
for ln in wrap(prof,font(10),mw):
    text(mx,my,ln,font(10),INK); my+=int(0.42*CM)
my+=int(0.1*CM); my=m_title(my,"Berufserfahrung")

def job(y,role,comp,loc,bullets,badge=None):
    text(mx,y,role,font(11,b=True),INK)
    gold(MR-int(0.2*CM)-d.textlength("〈MM.JJJJ – MM.JJJJ〉",font=font(9,i=True)),y+2,"MM.JJJJ – MM.JJJJ",font(9,i=True))
    y+=int(0.5*CM)
    text(mx,y,comp,font(10,b=True),STEEL); cw=d.textlength(comp,font=font(10,b=True))
    text(mx+cw+8,y,"· "+loc,font(9),GREY)
    if badge: chip(mx+cw+d.textlength("· "+loc,font=font(9))+int(0.7*CM),y,badge,font(8,b=True),WHITE,STEEL)
    y+=int(0.5*CM)
    for b,is_g in bullets:
        text(mx,y,"▪",font(9),STEEL)
        for i,ln in enumerate(wrap(b,font(10),mw-int(0.4*CM))):
            if is_g and i==0: gold(mx+int(0.4*CM),y,ln,font(10,i=True))
            else: text(mx+int(0.4*CM),y,ln,font(10),INK)
            y+=int(0.4*CM)
    return y+int(0.16*CM)

my=job(my,"Sales Engineer · Technischer Vertrieb","Camille Bauer Metrawatt AG","Wohlen AG",
   [("Vertrieb von Mess-/Analysesystemen (Sineax, Messwandler) im B2B.",False),
    ("Betreuung von Kunden über mehrere Kantone.",False),
    ("Aktive Neukundenakquise und Ausbau bestehender Kunden.",False),
    ("Konkretes Ergebnis / Neukundenzahl einsetzen",True)],badge="Aktuellste Position")
my=job(my,"Gebietsverkaufsleiter / Area Sales Manager","Cortexia SA","Westschweiz",
   [("Entwicklung des Verkaufsgebiets, Budget rund CHF 2,5 Mio.",False),
    ("Neukundenakquise und technische Beratung bis Abschluss.",False),
    ("Ergebnis / Projekt aus der Cortexia-Zeit ergänzen",True)])
my=job(my,"Funktion / Titel ergänzen","MRK · Manz · Pflitsch","Ort",
   [("je Station: Kernaufgabe + ein messbares Ergebnis",True)])
my=job(my,"Selbständige Ingenieur- & Vertriebstätigkeit","Kabuu Engineering","Hagen (DE)",
   [("Selbständige Tätigkeit im Engineering-/Vertriebsumfeld.",False)])

my+=int(0.05*CM); my=m_title(my,"Ausbildung")
text(mx,my,"Bachelor of Engineering (B.Eng.) – Elektrotechnik",font(10,b=True),INK)
gold(MR-int(0.2*CM)-d.textlength("〈JJJJ – JJJJ〉",font=font(9,i=True)),my,"JJJJ – JJJJ",font(9,i=True))
my+=int(0.5*CM); text(mx,my,"Hochschule Bochum, Deutschland",font(9.5),GREY)
my+=int(0.7*CM); my=m_title(my,"Weiterbildung & Zertifikate")
text(mx,my,"EMV-Fachkraft · Elektrofachkraft · BetrSichV · DGUV",font(9.5),INK)

img.save("docs/cv_preview.png"); print("saved", img.size)
