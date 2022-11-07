<Query Kind="Statements">
  <Namespace>System.Security.Cryptography</Namespace>
</Query>

const string flag = "j+Zdll1AHhxi496ET1Nw8CjfxIoVcaVCORWgKfWiH0KaBT7zrAMQK3ysXAuxurKLHuvRne6gxht6o8+0G6XdoA==";

var code = new char[26]
{
	'$', '"', '7', '$', '\u001E', '=', '1', '5', '\u0006', ' ', '1', '$', ' ', '"', '\u001C', '*', '\u001F', ';', '\n', '`', '\u001B', '*', '\u001F', 'd', '\n', 'q'
};

var xorkey = new char[3] {'E', 'P', 'T'};

int cnt = 0;
while (cnt < code.Length)
{
	for (int i = 0; i < xorkey.Length; i++)
	{
		if (code.Length > cnt)
		{
			code[cnt] = (char)(code[cnt] ^ xorkey[i]);
		}
		cnt++;
	}
}

//Convert.ToBase64String(code.Select(x => (byte)x).ToArray()).Dump();

var SuperSecretCode = new String(code);
SuperSecretCode.Dump();

CheckSuperSecretCode(SuperSecretCode).Dump();



static string CheckSuperSecretCode(string code)
{
	EncryptUtils encryptUtils = new EncryptUtils();
	string str = "boomLigHningBoltLigntingBoltLightnigBolt";
	if (!isValidWeaponCode(code))
		return "";
	string encKey = str + code;
	return encryptUtils.Decrypt(flag, encKey);
}

static bool isValidWeaponCode(string s)
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
	return Enumerable.SequenceEqual<char>((IEnumerable<char>)charArray, (IEnumerable<char>)new char[26]
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

public class EncryptUtils
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
				using (CryptoStream cryptoStream = new CryptoStream((Stream)memoryStream, aes.CreateEncryptor(), CryptoStreamMode.Write))
				{
					((Stream)cryptoStream).Write(bytes, 0, bytes.Length);
					((Stream)cryptoStream).Close();
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
				using (CryptoStream cryptoStream = new CryptoStream((Stream)memoryStream, aes.CreateDecryptor(), CryptoStreamMode.Write))
				{
					((Stream)cryptoStream).Write(numArray, 0, numArray.Length);
					((Stream)cryptoStream).Close();
				}
				cipherText = Encoding.Unicode.GetString(memoryStream.ToArray());
			}
		}
		return cipherText;
	}
}