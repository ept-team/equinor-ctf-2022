# ServicePrincipal

## Challenge

![](img/2022-11-07-18-03-36.png)

```
Tenant:         6837db8b-72d9-4346-bbb4-c2536150adf5
Application ID: 638ba534-d2ee-475a-adf7-089190310ec0
Secret:         ab28Q~u1z~KktYhXgfAn4OwTFtYv.NsojE4GlcO~
```

## Solution

In this task we were given a Tenant, an Application ID and a Secret.

We've also got the credentials for a normal user, given to us by the OnDemand portal. Those creds are not neccecary to solve this task, but can be nice to explore what's going on.

Note, naming convention in Azure is a can of worms. The terms used in the Azure Portal is different than the ones used in PowerShell. A "Service Principal" in PowerShell terminology is called "Enterprise Application" in the Azure portal. Service Principals (Enterprise Applications) are instances of an Application (App Registration).

If we log into https://portal.azure.com with the normal user, and search for the ApplicationID we find an App Registration called "flagreader".

![](img/2022-11-09-21-44-56.png)

Looking under the "Certificates & Secrets" menu we can see the secrets available for this application. The first one, which is expired when writing this writeup, is the one from the CTF.

![](img/2022-11-09-21-50-55.png)

Ok, now that we've briefly looked at what the Application (i.e. Service Principal) and secret looks like, let's go looking for the flag.

When working with Azure there are three main methods to interact with Azure. Here are examples using all three to find the flag.

### Using az cli

```sh
$ az login --service-principal -u 638ba534-d2ee-475a-adf7-089190310ec0 -p ab28Q~u1z~KktYhXgfAn4OwTFtYv.NsojE4GlcO~ --tenant 6837db8b-72d9-4346-bbb4-c2536150adf5

$ az resource list

$ az keyvault secret list --vault-name flag1vault2CF06847

$ az keyvault secret show --vault-name flag1vault2CF06847 --name flag
```

### Using Az Powershell Module

```powershell
$passwd = ConvertTo-SecureString "ab28Q~u1z~KktYhXgfAn4OwTFtYv.NsojE4GlcO~" -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential("638ba534-d2ee-475a-adf7-089190310ec0", $passwd)
Connect-AzAccount -ServicePrincipal -Credential $creds -Tenant 6837db8b-72d9-4346-bbb4-c2536150adf5

# List all resources
Get-AzResource

# List keyvaults
Get-AzKeyVault

# List secrets in keyvault
Get-AzKeyVaultSecret -VaultName flag1vault2CF06847

# Get value from secret
Get-AzKeyVaultSecret -VaultName flag1vault2CF06847 -Name flag -AsPlainText
```

### Using REST API

With the REST API it is a little more code than the previous two examples, but gives better insight into what is actually happening.

```python
#!/usr/bin/env python3

import requests

tenant = "6837db8b-72d9-4346-bbb4-c2536150adf5"
applicationId = "638ba534-d2ee-475a-adf7-089190310ec0"
secret = "jTh8Q~cMB37gMC1kJJfayE~TVAvf5GoIGGYkAa7N"

# 1. Authenticate
TOKEN_URL = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
body = {
    "client_id": applicationId,
    "grant_type": "client_credentials",
    "client_secret": secret,
    "scope": "https://management.azure.com/.default"
}
response = requests.post(TOKEN_URL, data=body)
print(response.content)
token = response.json()['access_token']

# 2. List subscriptions
SUBSCRIPTIONS_URL = "https://management.azure.com/subscriptions?api-version=2014-04-01"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(SUBSCRIPTIONS_URL, headers=headers)
print(response.content)

# 3. List all resources
subscription_id = response.json()['value'][0]['id']
RESOURCES_URL = f"https://management.azure.com{subscription_id}/resources?api-version=2014-04-01"
response = requests.get(RESOURCES_URL, headers=headers)
print(response.content)

# 4. List keyvault secrets
keyvault_id = response.json()['value'][0]['id']
KEYVAULT_URL = f"https://management.azure.com{keyvault_id}/secrets?api-version=2022-07-01"
response = requests.get(KEYVAULT_URL, headers=headers)
print("----------")
print(response.content)
secret_uri = response.json()['value'][0]['properties']['secretUri']

# 5. Get access token for vault.azure.net
body = {
    "client_id": applicationId,
    "grant_type": "client_credentials",
    "client_secret": secret,
    "scope": "https://vault.azure.net/.default"
}
response = requests.post(TOKEN_URL, data=body)
print(response.content)
token = response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# 6. Get secret
response = requests.get(secret_uri + "?api-version=7.3", headers=headers)
print(response.content)
flag = response.json()['value']

print(flag)
```