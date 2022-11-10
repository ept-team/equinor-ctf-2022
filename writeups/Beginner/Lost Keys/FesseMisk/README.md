## Challenge: Beginner/Lost Keys
### Description
Category: Forensics\Web

I lost my keys to the vault, but since I always have my full packet capture collector going maybe you can retrieve them somehow? I have some tasty flags stored there.

Site: vault7.io.ept.gg

![](lostkeys1.png)

PS: Note that there is a pcap provided for this challenge..


### Solution
Use the program wireshark and open the vault.pcap file. Following the tcp stream of the http data we find a vaultsession cookie. Having this we can inspect the website and insert the new vaultsession cookie where the old one was.

![](lostkeys3.png)
![](lostkeys2.png)

```
Cookie:
vaultsession: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMzM3IiwibmFtZSI6ImFkbWluaXN0cmF0b3IiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNjYyODM2OTE5LCJleHAiOjE4NjI4NDA1MTl9.UUjgd23gMWqseDU39Jhay2mjbtwRdcWE7KbqDbmTK9A
```
After inserting the new cookie, refresh the website and the flag will appear

### Flag
`EPT{n00m_n00m_c00kies}`

