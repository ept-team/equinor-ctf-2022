// Decompiled with JetBrains decompiler
// Type: ConsolePew.level2
// Assembly: ConsolePew, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// MVID: BC4DED27-C1A6-4AC3-816D-2AA45E5CF440
// Assembly location: ConsolePew.dll inside C:\Users\heina\Downloads\ConsolePew2.exe)

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading;


#nullable enable
namespace ConsolePew
{
    internal class level2
    {
        private string flag = "j+Zdll1AHhxi496ET1Nw8CjfxIoVcaVCORWgKfWiH0KaBT7zrAMQK3ysXAuxurKLHuvRne6gxht6o8+0G6XdoA==";
        private Player player;
        private int bossHP = 100000;

        public level2(Player p) => this.player = p;

        public bool Start()
        {
            this.player.GetWeaponsInventory();
            string chosenWeapon = this.player.GetEquippedWeapon().GetWeaponName();
            Console.WriteLine("You currently wield your " + this.player.GetEquippedWeapon().GetWeaponName());
            while (true)
            {
                Console.WriteLine("Do you wish to change weapon? YES/NO");
                string str = Console.ReadLine();
                if (!(str == "YES"))
                {
                    if (!(str == "NO"))
                        Console.WriteLine("YES or NO");
                    else
                        goto label_8;
                }
                else
                    break;
            }
            List<Weapon> weaponsInventory = this.player.GetWeaponsInventory();
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("Choose (write) a weapon from your inventory: " + string.Join(",", Enumerable.Select<Weapon, string>((IEnumerable<Weapon>) weaponsInventory, (Func<Weapon, string>) (weapon => weapon.GetWeaponName()))));
            Console.ForegroundColor = ConsoleColor.Red;
            chosenWeapon = Console.ReadLine();
            while (!Enumerable.Any<Weapon>((IEnumerable<Weapon>) weaponsInventory, (Func<Weapon, bool>) (weapon => weapon.GetWeaponName() == chosenWeapon)))
            {
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("You dont seem to have any " + chosenWeapon + " in your inventory.");
                Console.WriteLine("Choose again");
                Console.ForegroundColor = ConsoleColor.Red;
                chosenWeapon = Console.ReadLine();
            }
            this.player.EquipWeeapon(Enumerable.First<Weapon>(Enumerable.Where<Weapon>(Enumerable.Cast<Weapon>((IEnumerable) weaponsInventory), (Func<Weapon, bool>) (w => w.GetWeaponName() == chosenWeapon))));
label_8:
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("Wielding your " + this.player.GetEquippedWeapon()?.ToString() + ", its time to fight");
            while (this.player.GetPlayerHP() > 0 && this.bossHP > 0)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("You have " + this.player.GetPlayerHP().ToString() + " HP");
                Console.WriteLine("The Final Boss has " + this.bossHP.ToString() + " HP");
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("write your choice of action from: " + string.Join(",", this.player.GetActions()));
                Console.ForegroundColor = ConsoleColor.Red;
                string code = Console.ReadLine();
                int num1 = new Random().Next(1, 20);
                if (code == null)
                    code = "unknown";
                if (code == "attack")
                {
                    Thread.Sleep(1000);
                    int num2 = this.player.GetEquippedWeapon().Attack();
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine("You attacked for " + num2.ToString() + " damage!");
                    this.bossHP -= num2;
                    Console.WriteLine("The boss attacked you for " + num1.ToString() + " damage!");
                    this.player.SetPlayerHP(this.player.GetPlayerHP() - num1);
                }
                else if (code == "dodge")
                {
                    Thread.Sleep(1000);
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine("You dodged an attack!!");
                    Console.WriteLine("The would have dealt " + num1.ToString() + " damage!");
                }
                else if (code == "run")
                {
                    Thread.Sleep(2000);
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine("You tried run......");
                    Console.WriteLine("The boss caught you");
                    this.player.SetPlayerHP(0);
                }
                else if (this.player.GetEquippedWeapon().GetWeaponName() == "arcanite reaper")
                {
                    string str = this.CheckSuperSecretCode(code);
                    if (str != "")
                    {
                        Thread.Sleep(3000);
                        Console.ForegroundColor = ConsoleColor.DarkGreen;
                        Console.Write("you have won, here is your loot: ");
                        Console.ForegroundColor = ConsoleColor.DarkMagenta;
                        Console.WriteLine(str);
                        return true;
                    }
                    Thread.Sleep(1000);
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine("You did nothing......");
                    Console.WriteLine("The boss attacked you for " + num1.ToString() + " damage!");
                    this.player.SetPlayerHP(this.player.GetPlayerHP() - num1);
                }
                else
                {
                    Thread.Sleep(1000);
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine("You did nothing......");
                    Console.WriteLine("The boss attacked you for " + num1.ToString() + " damage!");
                    this.player.SetPlayerHP(this.player.GetPlayerHP() - num1);
                }
            }
            if (this.bossHP == 0)
            {
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("You have completed level 2");
                return true;
            }
            Console.ForegroundColor = ConsoleColor.DarkRed;
            return false;
        }

        private string CheckSuperSecretCode(string code)
        {
            EncryptUtils encryptUtils = new EncryptUtils();
            string str = "boomLigHningBoltLigntingBoltLightnigBolt";
            if (!this.isValidWeaponCode(code))
                return "";
            string encKey = str + code;
            return encryptUtils.Decrypt(this.flag, encKey);
        }

        private bool isValidWeaponCode(string s)
        {
            char[] charArray = s.ToCharArray();
            int length = s.Length;
            for (int index1 = 0; index1 < length; ++index1)
            {
                char[] chArray = charArray;
                int index2 = index1;
                if (index1 % 3 == 0)
                    chArray[index2] ^= 'E';
                else if (index1 % 3 == 1)
                    chArray[index2] ^= 'P';
                else
                    chArray[index2] ^= 'T';
            }
            return Enumerable.SequenceEqual<char>((IEnumerable<char>) charArray, (IEnumerable<char>) new char[26]
            {
                '$',
                '"',
                '7',
                '$',
                '\u001E',
                '=',
                '1',
                '5',
                '\u0006',
                ' ',
                '1',
                '$',
                ' ',
                '"',
                '\u001C',
                '*',
                '\u001F',
                ';',
                '\n',
                '`',
                '\u001B',
                '*',
                '\u001F',
                'd',
                '\n',
                'q'
            });
        }
    }
}
