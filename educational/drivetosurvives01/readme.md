# Drive To Survive S01 - Introduction to Windows Kernel Driver Exploitation

### Don't let the title put you off. Kernel driver exploitation might sound intimidating and extremely complex. (Which it is, but please continue reading) 
<br />

---

## Intro 

The purpose of this challenge is to give you an introduction to windows kernel driver exploitation and to give you an insight the world of driver-based vulnerabilities.

Even though this topic is indeed very complex and require in-depth knowledge of Windows internals for advanced use cases there are also some ways to simplificate this to get you started on the subject.

If you have no prior experience with reverse engineering it will take a bit more effort to follow, but in general reverse engineering a windows driver is not different from reversing any other windows binary.

If this is the first time you are reversing a Windows Driver, please spend 10 minutes on reading the following great article [Methodology for Static Reverse Engineering of Windows Kernel Drivers](https://posts.specterops.io/methodology-for-static-reverse-engineering-of-windows-kernel-drivers-3115b2efed83) written by [@matterpreter](https://twitter.com/matterpreter) 

You don't have to understand everything, but it introduces some important concepts and terminologies needed to solve this challenge.

## Lights out and away we go

OK, you have scrolled through and above article and everything is crystal clear? Probably not, but that is fine. I will try to further simplify some of the concepts to understand the workflow:

- We can regard a Windows Driver an API with kernel privileges that can be called by any user (not really, but for the sake of this challenge lets regard it as such) 
- The symlink name can be regarded as the location of the API
- IOCTLs can be regarded the API endpoints

This means that for us to find an interesting driver that could possibly have a vulnerability to exploit we need to:

1. Search the file system for non-default drivers with [DriverQuery](https://github.com/matterpreter/OffensiveCSharp/tree/master/DriverQuery) (already present on the vulnerable machine).
2. Retrieve the driver(s) to your reversing environment (or use the vulnerable machine which comes with Ghidra pre-installed)
3. Verify that the driver has *IoCreateDevice* and *IoCreateSymbolicLink* in the import table. (Even if it uses *IoCreateDeviceSecure* it could potentially be vulnerable as developer needs to apply a proper DACL on the device object to restrict who can interact with the object.) and find it's name.
4. Locate IOCTLs with vulnerable code and determine what input they require.
5. Create or find a user mode client to interact with the driver to send a request to the vulnerable code.

By doing these steps we have identified the API name (IoCreateSymbolicLink name), we have identified the endpoint (IOCTL address) and we have identified what input data we are required to send to the endpoint to trigger the vulnerability.

## TIPS
- Have the above mentioned article opened and use it as a reference guide as you proceed
- Remember to apply the ntddk_64.gdt in Ghidra to extend symbol support in Ghidra
- Find the correct entry function -> find the MajorFunction[0xe] (IRP_MJ_DEVICE_CONTROL) handler function -> Locate and understand vulnerable code -> Use a user mode client to call the driver with the identified IOCTL address and required input data. -> Profit!
- To ease the debugging you can also install the vulnerable driver on your local machine and use [DebugView](https://learn.microsoft.com/en-us/sysinternals/downloads/debugview) as it requires administrative privileges to capture the kernel. To install the driver on your machine you first have to enable Windows Test Mode since the driver is unsigned (not verified by microsoft). Run cmd as admin and execute `bcdedit /set testsigning on`. Restart your machine and then register the driver with `sc create vulndrv binpath= 'path to sys file' type= kernel && sc start vulndrv`. The driver will not harm your system, but remember to turn off testsigning and delete the driver afterwards. 
- We have supplied you with a very simple .net user mode client on the vulnerable machine but its functionality might have to be extended to fully profit. You can find many pre-compiled clients with required functionality online but for learning purposes it is a good exercise to extend the provided application for you to play a bit with the Win32 API and understand how the DeviceIoControl function communicates with a device driver.




