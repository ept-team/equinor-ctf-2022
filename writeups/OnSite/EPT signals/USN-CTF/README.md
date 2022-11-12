# 🔥 EPT Signals 🔥 Writeup


```
There is an EPT signal in the room. What is it trying to tell you?

flag = flag.replace("(", "{").replace(")", "}").replace("-", "_").upper()
```

This onsite challenge consisted of the EPT-logo blinking in morse-code.

To solve this we filmed the entire sequence of morse-code which lasted roughly 2 minutes and 40 seconds. To be able to better differentatiate between on and off, we converted the video from color to grayscale. This was done using ffmpeg:
```
ffmpeg -i input_video.mov -vf format=gray output_video.mov
```

By googling we found a GitHub repository which contained a script that could extract morse-code from videos. [video-morse-decoder](https://github.com/AndrewWasHere/video-morse-decoder)

After running the script we got this string
```
THISCHALLENGEISONFIRE?THEFLAGISCOMINGREALLYSOONNOW?AREYOUREADY?EPT?WELL?DONE?MORSE?IS?C00L??THATISIT?ENJOYTHERESTOFTHE
```

We saw that the flag part of the string was this:
```
EPT?WELL?DONE?MORSE?IS?C00L?
```

In the task description we were given a Python-command which would format the flag correctly. The script we used could not understand every sign, but the Python-command would switch dashes to underlines. This gave us the flag:

```
EPT{WELL_DONE_MORSE_IS_C00L}
```
