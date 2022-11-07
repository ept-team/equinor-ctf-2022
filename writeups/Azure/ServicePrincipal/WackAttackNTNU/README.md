# A solution to ServicePrincipal

Huge hint: The task is named "ServicePrincipal" and is in the azure category.

We were given azure service principal credentials. Log into the account with the credentials.

```ps1
az login --service-principal --username appID --password PASSWORD --tenant tenantID
```

We are not given any other clue to what we are searching for, so I decided to log the recent activities with:

```ps1
Get-AzLog
```

The only activity is with Azure key vault named "flag1vault2CF06847". I tried to get the vault secrets and found there was a secret named flag. We get the flag secret with

```ps1
Get-AzKeyVaultSecret -VaultName "flag1vault2CF06847" -Name "flag" -AsPlainText
```

Nice, we got the flag! 🚩