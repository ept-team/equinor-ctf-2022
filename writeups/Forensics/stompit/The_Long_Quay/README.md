Description
-----------
Timestomping is a common anti-forensic technique that attackers and malware authors use to hide their tracks. 
When a file was actually created or modified are things they would rather you don't know. 
Our incident responders suspect an attacker has tampered with one of the employees' payment data. 
The responders have extracted the $MFT along with the files from the relevant directory.

Can you find the file?

Wat do
------
You're given two files; mft.zip and files.zip

mft.zip contained $MFT which is a Master File Table from a NTFS volume where each file is represented by a record, and files.zip contained 9994 .txt-files which ALL had a unique flag in them.

Depending on your tool and OS of choice, you may or may not need to convert the MFT to a more convenient format.
I used https://github.com/dkovar/analyzeMFT (which can be installed with `sudo pip install analyzeMFT`) to convert the records to csv with 

```bash
sudo analyzeMFT.py -f '$MFT' -o mftanalyzed.csv
```

Now, the MFT contained alot more records (322868) than the 9994 files from files.zip, so it made sense to filter these out based on the path they were in, with;

```bash
grep '\/Techarisma Corporation\/HR_masterdata\/' mftanalyzed.csv > records.csv
```

I didn't really need the header as I already knew where the relevant timestamp would be, but there's definitely more elegant ways to do this.

While inspecting these records I noticed they all seemingly had the same timestamp: `2022-10-03 22:49:35.<nanoseconds>`.
Generally speaking, its rather difficult to do very granular timestomping, so it made sense to look for any records missing nanoseconds:

```bash
grep -P '\"2022\-10\-03\s\d{2}\:\d{2}\:\d{2}\"' records.csv
```

which matched the columns `"Std Info Creation date","Std Info Modification date","Std Info Access date","Std Info Entry date"` and gave me the the following record:

`
"170029","Good","Active","File","1","207","2","/Techarisma Corporation/HR_masterdata/3621169.txt","2022-10-03 22:49:46","2022-10-03 22:49:46","2022-10-03 22:49:46","2022-10-03 22:49:46","2022-10-03 22:49:46.105391","2022-10-03 22:49:46.105391","2022-10-03 22:49:46.105391","2022-10-03 22:49:46.105391","48806af0-5646-ed11-a75e-000c29b74253","80000000-5801-0000-0000-180000000100","3f010000-1800-0000-2323-232320546563","68617269-736d-6120-436f-72706f726174","","","","","","","","","","","","","","","","True","False","True","True","False","False","False","False","False","False","False","False","False","False","False","","N","N","N"
`

 which in turn contained the flag
  
 `EPT{b709edeabe2d1859f145216ec0a9fe26304d6681}` 
