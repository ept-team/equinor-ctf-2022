# the npm package
Author: starsiv

Flag: `EPT{ae009a13fb6b2c52f3a730a02c9bb827}`
## Description
```
Category: web

Install those npm packages they said, It will be helpful they said!

Download `chall.tar.gz`, build and run locally before visiting `http://localhost:3000` 
```
$ tar xzf chall.tar.gz && cd chall
$ docker build -t thepackage:latest .
$ docker run -p 3000:3000 --rm -it thepackage:latest
```
```

## Provided challenge files
* [chall.tar.gz](chall.tar.gz)
