# -*- coding: utf-8 -*-
"""Maßstabsgetreue PNG-Vorschau des modernen CV-Layouts (A4 @150dpi)."""
from PIL import Image, ImageDraw, ImageFont

DPI = 150
CM = DPI / 2.54
W, H = int(21.0*CM), int(29.7*CM)
ML = int(1.3*CM); MR = W-int(1.3*CM)
USABLE = MR-ML
SIDE_W = int(6.0*CM)
SX0, SX1 = ML, ML+SIDE_W
MX0 = SX1+int(0.0*CM)

NAVY=(22,42,67); STEEL=(44,95,138); INK=(34,38,43); GREY=(107,114,128)
WHITE=(255,255,255); LIGHT=(232,236,241); SIDE=(238,242,246)
GOLD=(154,122,46); GOLDBG=(251,241,216); LINE=(201,210,220)
ACC=(143,180,217)

F="/usr/share/fonts/truetype/liberation/"
def font(sz,b=False,i=False):
    n="LiberationSans-"
    n+= ("BoldItalic" if b and i else "Bold" if b else "Italic" if i else "Regular")
    return ImageFont.truetype(F+n+".ttf", int(sz))

img=Image.new("RGB",(W,H),WHITE)
d=ImageDraw.Draw(img)

def text(x,y,s,fnt,fill=INK,spacing=0,caps=False):
    if caps: s=s.upper()
    if spacing:
        cx=x
        for ch in s:
            d.text((cx,y),ch,font=fnt,fill=fill); cx+=d.textlength(ch,font=fnt)+spacing
        return cx
    d.text((x,y),s,font=fnt,fill=fill); return x+d.textlength(s,font=fnt)

def chip(x,y,s,fnt,fg,bg,pad=6):
    w=d.textlength(s,font=fnt)
    d.rounded_rectangle([x,y-2,x+w+pad*2,y+fnt.size+4],radius=4,fill=bg)
    d.text((x+pad,y),s,font=fnt,fill=fg); return x+w+pad*2

def gold(x,y,s,fnt):
    w=d.textlength("〈"+s+"〉",font=fnt)
    d.rectangle([x,y-1,x+w,y+fnt.size+2],fill=GOLDBG)
    d.text((x,y),"〈"+s+"〉",font=fnt,fill=GOLD); return x+w

# ---------- HEADER BAND ----------
HB=int(2.55*CM)
d.rectangle([ML,0,MR,HB],fill=NAVY)
text(ML+int(0.5*CM),int(0.45*CM),"BURAK ",font(34,b=True),WHITE,spacing=3)
xx=ML+int(0.5*CM)+d.textlength("BURAK ",font=font(34,b=True))+ (3*len("BURAK "))
text(xx,int(0.45*CM),"ÜÇÖZ",font(34,b=True),ACC,spacing=3)
text(ML+int(0.5*CM),int(1.42*CM),"TECHNISCHER VERTRIEB IM AUSSENDIENST",font(13),LIGHT,spacing=3)
text(ML+int(0.5*CM),int(1.92*CM),"Gebietsverkauf · Neukundenakquise · Key-Account",font(11),(159,178,199),spacing=2)

# ---------- SIDEBAR BG ----------
by0=HB+int(0.25*CM)
d.rectangle([SX0,by0,SX1,H-int(1.1*CM)],fill=SIDE)

def s_title(y,s):
    text(SX0+int(0.42*CM),y,s,font(12,b=True),NAVY,spacing=3,caps=True)
    yy=y+int(0.52*CM); d.line([SX0+int(0.42*CM),yy,SX1-int(0.42*CM),yy],fill=LINE,width=2)
    return yy+int(0.18*CM)

def s_field(y,label,val,is_gold=True):
    text(SX0+int(0.42*CM),y,label.upper(),font(9,b=True),STEEL,spacing=1)
    y+=int(0.38*CM)
    if is_gold: gold(SX0+int(0.42*CM),y,val,font(10,i=True))
    else: text(SX0+int(0.42*CM),y,val,font(10),INK)
    return y+int(0.5*CM)

sx=SX0+int(0.42*CM); sw=SIDE_W-int(0.84*CM)
# Foto
fy=by0+int(0.3*CM)
d.rectangle([sx,fy,sx+sw,fy+int(2.4*CM)],outline=(183,194,206),width=2)
text(sx+sw/2-18,fy+int(1.0*CM),"Foto",font(11,i=True),GREY)
text(sx+sw/2-44,fy+int(2.55*CM),"optional · CH-üblich",font(8,i=True),GREY)

y=fy+int(3.1*CM)
y=s_title(y,"Kontakt")
y=s_field(y,"Adresse","Strasse, PLZ Ort")
y=s_field(y,"Telefon","+41 ...")
y=s_field(y,"E-Mail","b.s.uecoez@gmail.com",is_gold=False)
y=s_field(y,"LinkedIn","linkedin.com/in/...")
y+=int(0.15*CM)
y=s_title(y,"Persönliches")
y=s_field(y,"Geburtsdatum","TT.MM.JJJJ")
y=s_field(y,"Nationalität","...")
y=s_field(y,"Bewilligung","...")
y+=int(0.15*CM)
y=s_title(y,"Sprachen")
for n,l in [("Deutsch","Muttersprache"),("Französisch","B2"),("Englisch","B2/C1"),("Türkisch","Niveau")]:
    text(sx,y,n,font(10,b=True),INK); gold(sx+int(2.6*CM),y,l,font(9,i=True)); y+=int(0.46*CM)
y+=int(0.15*CM)
y=s_title(y,"Kompetenzen")
for sk in ["Neukundenakquise","Gebiets- & Budgetverantw.","Technische Beratung","Verhandlung & Abschluss","CRM / MS Office"]:
    text(sx,y,"▪",font(10),STEEL); text(sx+int(0.4*CM),y,sk,font(10),INK); y+=int(0.44*CM)

# ---------- MAIN COLUMN ----------
mx=MX0+int(0.5*CM); mw=MR-mx-int(0.2*CM)
def m_title(y,s):
    text(mx,y,s,font(14,b=True),NAVY,spacing=2,caps=True)
    yy=y+int(0.62*CM); d.line([mx,yy,MR-int(0.2*CM),yy],fill=NAVY,width=3)
    return yy+int(0.22*CM)

def wrap(s,fnt,maxw):
    words=s.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

my=by0+int(0.3*CM)
my=m_title(my,"Kurzprofil")
prof=("Technischer Vertriebsprofi mit Schwerpunkt Aussendienst und Gebietsverkauf "
      "erklärungsbedürftiger Produkte. Eigenverantwortung für ein Gebietsbudget von rund "
      "CHF 2,5 Mio. Stärken in Neukundenakquise, technischer Beratung und langfristiger "
      "Kundenbindung. Führungserfahrung als Reife eingebracht – Fokus klar auf Gebiets- "
      "und Kundenverantwortung.")
for ln in wrap(prof,font(10),mw):
    text(mx,my,ln,font(10),INK); my+=int(0.42*CM)

my+=int(0.1*CM)
my=m_title(my,"Berufserfahrung")

def job(y,role,comp,period,bullets,anchor=False):
    text(mx,y,role,font(11,b=True),INK)
    pw=d.textlength(period,font=font(9,i=True))
    gold(MR-int(0.2*CM)-pw-14,y+2,period.replace("〈","").replace("〉",""),font(9,i=True))
    y+=int(0.5*CM)
    text(mx,y,comp,font(10,b=True),STEEL)
    cw=d.textlength(comp,font=font(10,b=True))
    text(mx+cw+8,y,"· Ort",font(9),GREY)
    if anchor: chip(mx+cw+int(1.4*CM),y,"Ankerstation",font(8,b=True),WHITE,STEEL)
    y+=int(0.5*CM)
    for b,is_g in bullets:
        text(mx,y,"▪",font(9),STEEL)
        lines=wrap(b,font(10),mw-int(0.4*CM))
        for i,ln in enumerate(lines):
            if is_g and i==0: gold(mx+int(0.4*CM),y,ln,font(10,i=True))
            else: text(mx+int(0.4*CM),y,ln,font(10),INK)
            y+=int(0.4*CM)
    return y+int(0.18*CM)

my=job(my,"Gebietsverkaufsleiter / Area Sales Manager","Cortexia SA","MM.JJJJ – heute",
   [("Entwicklung des Verkaufsgebiets, Budget rund CHF 2,5 Mio.",False),
    ("gewonnen: Anzahl Neukunden / Volumen",True),
    ("Technische Beratung – Erstansprache bis Abschluss.",False)],anchor=True)
my=job(my,"Aussendienst / Technischer Verkauf","Camille Bauer Metrawatt AG","MM.JJJJ – MM.JJJJ",
   [("Betreuung eines Verkaufsgebiets im technischen B2B-Umfeld.",False),
    ("Neukundengewinnung: echte Zahl einsetzen",True)])
my=job(my,"Funktion / Titel","MRK · Manz · Anadolu · Pflitsch","MM.JJJJ – MM.JJJJ",
   [("je Station: Kernaufgabe + ein messbares Ergebnis",True)])
my=job(my,"Funktion / Titel","Kabuu","MM.JJJJ – MM.JJJJ",
   [("Langjähriges Engagement – Beleg für Beständigkeit.",False)])

my+=int(0.05*CM)
my=m_title(my,"Ausbildung")
gold(mx,my,"Abschluss / Titel · Fachrichtung · Hochschule",font(10,i=True))
gold(MR-int(0.2*CM)-d.textlength("〈JJJJ–JJJJ〉",font=font(9,i=True)),my,"JJJJ–JJJJ",font(9,i=True))

img.save("docs/cv_preview.png")
print("saved docs/cv_preview.png", img.size)
