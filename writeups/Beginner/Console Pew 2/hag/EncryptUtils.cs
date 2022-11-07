// Decompiled with JetBrains decompiler
// Type: ConsolePew.EncryptUtils
// Assembly: ConsolePew, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null
// MVID: BC4DED27-C1A6-4AC3-816D-2AA45E5CF440
// Assembly location: ConsolePew.dll inside C:\Users\heina\Downloads\ConsolePew2.exe)

using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;


#nullable enable
namespace ConsolePew
{
    internal class EncryptUtils
    {
        public string Encrypt(string cleartext, string encKey)
        {
            string password = encKey;
            byte[] bytes = Encoding.Unicode.GetBytes(cleartext);
            using (Aes aes = Aes.Create())
            {
                Rfc2898DeriveBytes rfc2898DeriveBytes = new Rfc2898DeriveBytes(password, new byte[13]
                {
                    (byte) 73,
                    (byte) 118,
                    (byte) 97,
                    (byte) 110,
                    (byte) 32,
                    (byte) 77,
                    (byte) 101,
                    (byte) 100,
                    (byte) 118,
                    (byte) 101,
                    (byte) 100,
                    (byte) 101,
                    (byte) 118
                });
                aes.Key = rfc2898DeriveBytes.GetBytes(32);
                aes.IV = rfc2898DeriveBytes.GetBytes(16);
                using (MemoryStream memoryStream = new MemoryStream())
                {
                    using (CryptoStream cryptoStream = new CryptoStream((Stream) memoryStream, aes.CreateEncryptor(), CryptoStreamMode.Write))
                    {
                        ((Stream) cryptoStream).Write(bytes, 0, bytes.Length);
                        ((Stream) cryptoStream).Close();
                    }
                    cleartext = Convert.ToBase64String(memoryStream.ToArray());
                }
            }
            return cleartext;
        }

        public string Decrypt(string cipherText, string encKey)
        {
            string password = encKey;
            cipherText = cipherText.Replace(" ", "+");
            byte[] numArray = Convert.FromBase64String(cipherText);
            using (Aes aes = Aes.Create())
            {
                Rfc2898DeriveBytes rfc2898DeriveBytes = new Rfc2898DeriveBytes(password, new byte[13]
                {
                    (byte) 73,
                    (byte) 118,
                    (byte) 97,
                    (byte) 110,
                    (byte) 32,
                    (byte) 77,
                    (byte) 101,
                    (byte) 100,
                    (byte) 118,
                    (byte) 101,
                    (byte) 100,
                    (byte) 101,
                    (byte) 118
                });
                aes.Key = rfc2898DeriveBytes.GetBytes(32);
                aes.IV = rfc2898DeriveBytes.GetBytes(16);
                using (MemoryStream memoryStream = new MemoryStream())
                {
                    using (CryptoStream cryptoStream = new CryptoStream((Stream) memoryStream, aes.CreateDecryptor(), CryptoStreamMode.Write))
                    {
                        ((Stream) cryptoStream).Write(numArray, 0, numArray.Length);
                        ((Stream) cryptoStream).Close();
                    }
                    cipherText = Encoding.Unicode.GetString(memoryStream.ToArray());
                }
            }
            return cipherText;
        }
    }
}
