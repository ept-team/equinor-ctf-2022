# Misc/Lets Play Harder

We connected to a tcp server which presented itself and wanted to play a game where you identify symbols, and when you said "Yes" I am ready the server sent you PNG files encoded with base64 and you had 3 seconds to respond. And in total it would send 400 of them.


The first image it sent was what my code started with
![](./1.png)


An image with 512x512 pixels, with 4 areas. Meaning each area is 256x256 pixels.

I made the code measure the colour in the middle point (128x128) and then I calculated the number of "none" black pixels at row 80 (top), 128 (middle) and 176 (bottom) to identify the shape.
* All values equal = RECTANGLE
* Top value smaller than medium and medium smaller than bottom = TRIANGLE

Then it was a little more tricky with HEXAGON and CIRCLE. Both was showing top and bottom with identical values, and middle with a bigger value. The only way to differentiate them was to calculate the percentage of change from the middle value. The HEXAGON would have a much more reduced value.

* Pixel count reduced by 25% (or more) = HEXAGON
* Remaining must be = CIRCLE


That run well for a while, until we got different colurs into the mix

![](./2.png)

And the questions changed, it would now ask for shape AND colour.

Modified the code to map colour to names and added flexibility to parsing so it would understand the two different question types. And now it worked.. 400 Q&A's and we had our flag.

I now tried the code on the other game Misc/LetsPlayAgame and it worked without change. One code, two flags.

I am sure the code could be written somewhat more elegant, but time was of the essence

```
using System.Drawing.Imaging;
using System.Drawing;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Net.NetworkInformation;

internal class Program
{
    private static global::System.Int32 Main(string[] args)
    {
        using TcpClient tcpClient = new TcpClient();
        tcpClient.Connect("io.ept.gg", 30049);

        NetworkStream netStream = tcpClient.GetStream();
        netStream.ReadTimeout = 250;

        byte[] sendBuffer;
        bool waiting_for_image = false;
        int imagecnt = 0;
        string lookingFor = "";
        string lookingColour = "";

        // Receive some data from the peer.
        byte[] receiveBuffer = new byte[1024];
        string alldata = "";
        string cmd = "";
        int bytesReceived;

        while (true)
        {

            bytesReceived = -1;
            if (netStream.DataAvailable)
                bytesReceived = netStream.Read(receiveBuffer, 0, receiveBuffer.Length);


            if (bytesReceived > 0)
            {
                string data = Encoding.ASCII.GetString(receiveBuffer.AsSpan(0, bytesReceived));

                if (!waiting_for_image)
                    Console.WriteLine(data);

                alldata = alldata + data;
                int idxCr = alldata.IndexOf("\n");

                while (idxCr > 0)
                {
                    if (idxCr >= 0)
                    {
                        cmd = alldata.Substring(0, idxCr);
                        cmd.Trim();

                        alldata = alldata.Substring(idxCr + 1);

                        processCmd(cmd);
                    }
                    idxCr = alldata.IndexOf("\n");
                }
                Thread.Sleep(200);
            }
        }



        void processCmd(string cmd)
        {


            if (cmd.Contains("Are you ready?"))
            {
                Console.WriteLine($"CMD:{cmd}");

                sendBuffer = Encoding.UTF8.GetBytes("YES\r\n");
                netStream.Write(sendBuffer);
            }
            else if (cmd.Contains("Where is"))
            {
                Console.WriteLine(cmd);
                waiting_for_image = true;

                lookingFor = "";
                lookingColour = "";

                int idxP = cmd.IndexOf("(");

                if (idxP > 0)
                {
                    cmd = cmd.Substring(0, idxP).Trim();
                    var tokens = cmd.Split(" ");
                    if (tokens.Length == 4)
                    {
                        lookingFor = tokens[3];
                    }
                    else if (tokens.Length == 5)
                    {
                        lookingColour = tokens[3];
                        lookingFor = tokens[4];
                    }
                }

                lookingFor = lookingFor.ToUpper();
                lookingColour = lookingColour.ToUpper();

                Console.WriteLine($"Looking for: {lookingColour} {lookingFor}");

            }
            else if (waiting_for_image)
            {
                imagecnt++;
                string where = "";
                byte[] pngBytes = Convert.FromBase64String(cmd);

                string filePath = $"LAST.PNG";
                File.WriteAllBytes(filePath, pngBytes);

                Console.WriteLine($"Got Image {imagecnt}!!");

                using (Image image = Image.FromStream(new MemoryStream(pngBytes)))
                {

                    using (Bitmap bmp = new Bitmap(image))
                    {

                        // Image is 512*512. So each square is 256*256

                        // Classify by x,y
                        string nw = classify(bmp, 0, 0);
                        string ne = classify(bmp, 256, 0);
                        string sw = classify(bmp, 0, 256);
                        string se = classify(bmp, 256, 256);

                        Console.WriteLine($"nw={nw} ne={ne} sw={sw} se={se}");

                        if (isMatch(nw)) where = "nw";
                        if (isMatch(ne)) where = "ne";
                        if (isMatch(sw)) where = "sw";
                        if (isMatch(se)) where = "se";
                    }
                }

                Console.WriteLine($"Found {lookingFor} at {where}");

                sendBuffer = Encoding.UTF8.GetBytes($"{where}\n");
                netStream.Write(sendBuffer);

                waiting_for_image = false;
            }
            else
                Console.WriteLine(cmd);
        }

        bool isMatch(string classified)
        {
            classified = classified.ToUpper();

            var tokens = classified.Split("-");

            if (lookingColour.Length > 0)
            {
                if (!tokens[0].Contains(lookingColour)) return false;
            }

            if (lookingFor.Length > 0)
            {
                if (!tokens[1].Contains(lookingFor)) return false;
            }

            return true;
        }

        string classify(Bitmap img, int x, int y)
        {
            Color c = img.GetPixel(x + 128, y + 128);
            string color = "";

            switch (c.Name.ToUpper())
            {
                case "FF000000":
                    color = "black";
                    break;
                case "FFFF0000":
                    color = "red";
                    break;
                case "FF008000":
                    color = "green";
                    break;

                case "FF800080":
                    color = "purple";
                    break;

                case "FF0000FF":
                    color = "blue";
                    break;
                case "FFFFFFFF":
                    color = "white";
                    break;
                case "FFFFFF00":
                    color = "yellow";
                    break;

                case "FFA52A2A":
                    color = "brown"; // Dark red
                    break;

                default:
                    color = "unknown#" + c.Name;
                    break;
            }


            int ytop = CountColour(img, c, x, y + 80);
            int ymid = CountColour(img, c, x, y + 128);
            int ybottom = CountColour(img, c, x, y + 176);

            double delta = ((double)ybottom / (double)ymid) * 100;

            Console.WriteLine($"top={ytop} mid={ymid} bottom={ybottom} delta={delta}");

            if ((ytop == ymid) && (ymid == ybottom))
                return $"{color}-RECTANGLE";


            if ((ytop < ymid) && (ymid < ybottom))
                return $"{color}-TRIANGLE";

            if ((ytop < ymid) && (ybottom < ymid) && (delta < 75))
                return $"{color}-HEXAGON";


            return $"{color}-CIRCLE";
        }


        int CountColour(Bitmap img, Color c, int x, int y)
        {
            int cnt = 0;

            for (int i = 0; i < 253; i++)
            {
                if (img.GetPixel(x + i, y).Name == c.Name)
                    cnt++;
            }

            return cnt;
        }

    }
}
```