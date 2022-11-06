Upon opening the provided .eml there's a file attached: `resume.pdf`.

From here there are several approaches that can be used, but depending on the filetype I almost always start with binwalk to se if there's something more hidden;

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
