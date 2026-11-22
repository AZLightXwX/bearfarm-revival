using System.IO;
using UnityEngine;

public static class BearPatch
{
	private static string _srv;

	private static string Srv()
	{
		if (_srv != null)
		{
			return _srv;
		}
		try
		{
			string path = Application.persistentDataPath + "/../shared_prefs/bearfarm.xml";
			if (File.Exists(path))
			{
				string xml = File.ReadAllText(path);
				int k = xml.IndexOf("<string name=\"server\">");
				if (k >= 0)
				{
					int gt = xml.IndexOf(">", k);
					int start = gt + 1;
					int end = xml.IndexOf("</string>", start);
					if (end > start)
					{
						string s = xml.Substring(start, end - start);
						if (s.Length > 0)
						{
							_srv = s;
							return _srv;
						}
					}
				}
			}
		}
		catch
		{
		}
		return "192.168.2.20";
	}

	public static string Farmzone()
	{
		return "http://" + Srv() + ":8080";
	}

	public static string Esb()
	{
		return Srv() + ":60000";
	}

	public static string Api()
	{
		return "http://" + Srv();
	}

	public static string Res()
	{
		return "http://" + Srv() + "/";
	}

	public static string PacksList()
	{
		return "http://" + Srv() + ":8100/bigbear/getPacksList?app_id=";
	}

	public static string Uploads()
	{
		return "http://" + Srv() + "/bearfarm/uploads/";
	}

	public static string SendFile()
	{
		return "http://" + Srv() + "/bearfarm/sendfile.php";
	}

	public static string NetUser()
	{
		return "http://" + Srv() + "/user/";
	}
}
