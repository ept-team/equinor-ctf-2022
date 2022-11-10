## Challenge: Beginner/Notes - Revisited
### Description
The hacker claims we have planted this note on his phone. Can you find out the actual date and time when it was last modified?

The flag format is: EPT{31.12.2099_23:59}

P.S: This is not an artificial challenge - this timestamp is indeed added by the notes application and can be recreated easily on your phone.

![](notes_r01.png)

### Solution

Using the same tool as in the challenge `notes` ([29a.ch/photo-forensics](29a.ch/photo-forensics) and Luminance Gradient) we can see the date and time in plaint text:
![](notes_r02.png)

### Flag
`EPT{30.05.2001_06:45}`