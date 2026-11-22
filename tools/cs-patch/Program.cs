using System;
using System.Collections.Generic;
using System.Linq;
using dnlib.DotNet;
using dnlib.DotNet.Emit;

class Program
{
    // exact ldstr value -> BearPatch method name
    static readonly Dictionary<string, string> Map = new()
    {
        ["http://farmzone.joymeng.com:8080"] = "Farmzone",
        ["farmesb1.joymeng.com:60000"] = "Esb",
        ["http://api.joyapi.com"] = "Api",
        ["http://hijoyres.joymeng.com/"] = "Res",
        ["http://hijoyusers.joymeng.com:8100/bigbear/getPacksList?app_id="] = "PacksList",
        ["http://netvoice.joymeng.com/bearfarm/uploads/"] = "Uploads",
        ["http://netvoice.joymeng.com/bearfarm/sendfile.php"] = "SendFile",
        ["http://netuser.joymeng.com/user/"] = "NetUser",
    };

    static int Main(string[] args)
    {
        var managedDir = args[0];
        var bearPath = args[1];
        var outPath = args[2];

        var target = ModuleDefMD.Load(System.IO.Path.Combine(managedDir, "Assembly-CSharp.dll"));
        var bear = ModuleDefMD.Load(bearPath);

        // move BearPatch type into the target module
        var bearType = bear.Types.FirstOrDefault(t => t.Name == "BearPatch");
        if (bearType == null)
        {
            Console.WriteLine("BearPatch type not found");
            return 1;
        }
        bear.Types.Remove(bearType);
        target.Types.Add(bearType);

        var methods = bearType.Methods.ToDictionary(m => m.Name.String, m => m);

        int patched = 0;
        foreach (var type in target.Types)
        {
            foreach (var method in type.Methods)
            {
                if (!method.HasBody)
                    continue;
                var instrs = method.Body.Instructions;
                for (int i = 0; i < instrs.Count; i++)
                {
                    var ins = instrs[i];
                    if (ins.OpCode != OpCodes.Ldstr)
                        continue;
                    if (ins.Operand is string s && Map.TryGetValue(s, out var mname))
                    {
                        if (methods.TryGetValue(mname, out var targetMethod))
                        {
                            ins.OpCode = OpCodes.Call;
                            ins.Operand = targetMethod;
                            patched++;
                        }
                    }
                }
            }
        }
        Console.WriteLine($"patched {patched} ldstr sites");
        if (patched == 0)
        {
            Console.WriteLine("WARNING: nothing patched!");
            return 2;
        }
        PatchTradePanelCache(target);
        target.Write(outPath);
        Console.WriteLine($"written {outPath}");
        return 0;
    }

    /// <summary>
    /// TradeBuyPanel_New.PerformFetchStorey..ctor restores stale seller lists from
    /// the player blob (GlobalSellers) and short-circuits the fetch on first open.
    /// Neutralize `_list = ...Sellers` so the panel always fetches fresh data.
    /// </summary>
    static void PatchTradePanelCache(ModuleDefMD target)
    {
        foreach (var type in target.Types)
        {
            foreach (var nested in type.NestedTypes)
            {
                if (nested.Name != "PerformFetchStorey")
                    continue;
                var ctor = nested.Methods.FirstOrDefault(m => m.Name == ".ctor" && m.HasBody);
                var listField = nested.Fields.FirstOrDefault(f => f.Name == "_list");
                if (ctor == null || listField == null)
                    continue;
                var instrs = ctor.Body.Instructions;
                for (int i = 0; i < instrs.Count; i++)
                {
                    if (instrs[i].OpCode != OpCodes.Stfld || instrs[i].Operand != listField)
                        continue;
                    // stack layout at stfld: [... this, value]
                    // walk back over the value-producing instructions (calls/loads)
                    int j = i - 1;
                    while (j >= 0 && (instrs[j].OpCode == OpCodes.Call
                                      || instrs[j].OpCode == OpCodes.Callvirt
                                      || instrs[j].OpCode == OpCodes.Ldsfld
                                      || instrs[j].OpCode == OpCodes.Ldfld))
                    {
                        j--;
                    }
                    // j now points at the instruction that pushed `this` (e.g. ldloc.0)
                    // nop everything between j+1..i-1 and place a single ldnull there
                    for (int k = j + 1; k <= i - 1; k++)
                    {
                        instrs[k].OpCode = OpCodes.Nop;
                        instrs[k].Operand = null;
                    }
                    instrs[i - 1].OpCode = OpCodes.Ldnull;
                    instrs[i - 1].Operand = null;
                    Console.WriteLine("PerformFetchStorey..ctor: cache assignment neutralized");
                    return;
                }
            }
        }
        Console.WriteLine("WARNING: PerformFetchStorey patch site not found!");
    }
}
