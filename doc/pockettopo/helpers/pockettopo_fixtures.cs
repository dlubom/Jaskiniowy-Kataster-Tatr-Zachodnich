// Research helper for P01, NOT the future converter or a .top writer.
// Loads an installed PocketTopo 1.372 assembly, creates its own native model
// objects, then calls its DataSet.Write/Read and native TXT/DXF exporters.
// No MainForm is instantiated; no window is shown and no GUI process is touched.
// All serialization belongs to PocketTopo.exe. The fixture inputs below are
// intentionally explicit and independent of the Python byte inspector.
using System;
using System.Collections;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using System.Drawing;

class PocketTopoFixtures
{
    static Assembly App;
    const BindingFlags Flags = BindingFlags.Public | BindingFlags.NonPublic |
        BindingFlags.Instance | BindingFlags.Static;

    static Type T(string name) { return App.GetType("PocketTopo." + name, true); }
    static object New(string name, params object[] args)
    {
        return Activator.CreateInstance(T(name), Flags, null, args, CultureInfo.InvariantCulture);
    }
    static object Call(object obj, string method, params object[] args)
    {
        Type type = obj as Type;
        if (type == null) type = obj.GetType();
        return type.InvokeMember(method, Flags | BindingFlags.InvokeMethod,
            null, obj is Type ? null : obj, args, CultureInfo.InvariantCulture);
    }
    static FieldInfo Field(Type type, string name)
    {
        while (type != null)
        {
            FieldInfo result = type.GetField(name, Flags);
            if (result != null) return result;
            type = type.BaseType;
        }
        throw new MissingFieldException(name);
    }
    static void Set(object obj, string name, object value)
    {
        Type type = obj as Type;
        Field(type ?? obj.GetType(), name).SetValue(obj is Type ? null : obj, value);
    }
    static object Get(object obj, string name)
    {
        Type type = obj as Type;
        return Field(type ?? obj.GetType(), name).GetValue(obj is Type ? null : obj);
    }
    static object Id(string text) { return New("ID", text); }
    static object Angle(double degrees) { return New("Angle", degrees, 360); }
    static void IgnoreEvent(object sender, EventArgs args) { }

    class Model
    {
        public BindingSource Shots = new BindingSource(new ArrayList(), null);
        public BindingSource References = new BindingSource(new ArrayList(), null);
        public object Survey, Map, Plan, Side, Data;
        public Model()
        {
            Call(T("Trip"), "Reset");
            Survey = New("Survey", Shots, References, new EventHandler(IgnoreEvent));
            // MainForm normally supplies this native cross-section dependency.
            Set(T("XSection"), "survey", Survey);
            Map = New("Mapping", new Control());
            Plan = New("Drawing", New("Mapping", new Control()), false);
            Side = New("Drawing", New("Mapping", new Control()), true);
            Call(Plan, "add_UndoChanged", new EventHandler(IgnoreEvent));
            Call(Side, "add_UndoChanged", new EventHandler(IgnoreEvent));
            Data = New("DataSet", Survey, Map, Plan, Side);
        }
        public void Trip(long ticks, double declination, bool automatic, string comment)
        {
            object trip = New("Trip");
            Set(trip, "date", new DateTime(ticks));
            Set(trip, "comment", comment);
            Set(trip, "declCorr", Angle(declination));
            Set(trip, "automatic", automatic);
            Call(T("Trip"), "AddTrip", trip);
        }
        public void Shot(string from, string to, int distance, double azimuth,
            double inclination, byte roll, short trip, bool flipped, string comment)
        {
            object shot = New("Station", Id(from), Id(to), distance,
                Angle(azimuth), Angle(inclination), roll, trip);
            if (flipped) Set(shot, "flags", Enum.ToObject(Field(T("Station"), "flags").FieldType, 1));
            Set(shot, "comment", comment);
            Shots.Add(shot);
        }
        public void Reference(string id, long east, long north, int altitude, string comment)
        {
            object location = New("MetricLocation");
            Set(location, "e", east);
            Set(location, "n", north);
            Set(location, "alt", altitude);
            object reference = New("Reference", Id(id), location);
            Set(reference, "comment", comment);
            References.Add(reference);
        }
        public void Polygon(object drawing, string color, Point[] points)
        {
            object polygon = New("Polygon");
            Set(polygon, "points", points);
            Set(polygon, "pen", Get(T("MainForm"), color));
            Append(drawing, polygon);
        }
        public void Section(object drawing, Point center, string station, int direction)
        {
            object section = New("XSection");
            Set(section, "center", center);
            Set(section, "num", Id(station));
            Set(section, "direction", direction);
            Append(drawing, section);
        }
        void Append(object drawing, object element)
        {
            // Preserve the explicit input order without using the GUI undo stack.
            Set(element, "list", drawing);
            object last = Get(drawing, "elems");
            if (last == null) Set(drawing, "elems", element);
            else
            {
                while (Get(last, "next") != null) last = Get(last, "next");
                Set(last, "next", element);
            }
        }
        public void Save(string root, string name)
        {
            string dir = Path.Combine(root, name);
            Directory.CreateDirectory(dir);
            string top = Path.Combine(dir, name + ".top");
            if (File.Exists(top)) throw new IOException("Refusing to overwrite " + top);
            Call(Data, "Write", top);
            Console.WriteLine("Native DataSet.Write: " + top);
            // Reopen through the real reader before producing comparison exports.
            Model check = new Model();
            bool valid = (bool)Call(check.Data, "Read", top, false);
            if (!valid) throw new InvalidDataException("Native DataSet.Read rejected " + top);
            using (StreamWriter text = new StreamWriter(Path.Combine(dir, "native.txt"), false, new UTF8Encoding(false)))
                Call(check.Survey, "WriteText", text);
            Type options = T("DXFWriter").GetNestedType("Options", Flags);
            object planOptions = Enum.Parse(options, "ENS, ENX, SEPS, SEPX");
            object sideOptions = Enum.Parse(options, "SIDE, ENS, ENX, SEPS, SEPX");
            Call(T("DXFWriter"), "WriteDXF", Path.Combine(dir, "native-plan.dxf"), check.Survey, check.Plan, 500, planOptions);
            Call(T("DXFWriter"), "WriteDXF", Path.Combine(dir, "native-side.dxf"), check.Survey, check.Side, 500, sideOptions);
            // PocketTopo's DXF exporter catches its exceptions internally.
            // A returned call alone is not evidence of a complete output.
            foreach (string file in new string[] { "native-plan.dxf", "native-side.dxf" })
                if (!File.ReadAllText(Path.Combine(dir, file)).TrimEnd().EndsWith("EOF"))
                    throw new InvalidDataException("Incomplete native DXF: " + file);
            Console.WriteLine("Native DataSet.Read + Survey.WriteText + DXFWriter.WriteDXF: OK " + name);
        }
    }

    static void Cardinal(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, 0, false, "P01 synthetic cardinal and repeat readings");
        m.Shot("0", "1", 10000, 0, 0, 0, 0, false, "north");
        m.Shot("1", "2", 2000, 90, 0, 64, 0, false, "east");
        m.Shot("2", "3", 3000, 180, 0, 128, 0, false, "south");
        m.Shot("3", "4", 4000, 270, 0, 192, 0, false, "west");
        m.Shot("4", "5", 5000, 358, 10, 255, 0, false, "confirmed repeat A1");
        m.Shot("4", "5", 5000, 2, 10, 0, 0, false, "confirmed repeat A2");
        m.Shot("5", "4", 5000, 180, -10, 0, 0, false, "confirmed repeat A3 backwards");
        m.Shot("5", "6", 1000, 0, 90, 0, 0, false, "vertical up");
        m.Shot("6", "7", 1000, 0, -90, 0, 0, false, "vertical down");
        m.Shot("7", "", 1234, 45, -20, 0, 0, false, "splay");
        m.Shot("7", "8", 0, 0, 0, 0, 0, false, "zero link");
        m.Save(root, "api-cardinal");
    }

    static void TripsAndIds(string root)
    {
        Model m = new Model();
        m.Trip(630822816000000007L, 5, false, "Synthetic reset-looking date, not field evidence");
        m.Trip(639259776000000009L, -3.5, false, "Unicode trip: Zażółć gęślą jaźń");
        m.Trip(639260640000000001L, 0, true, "Auto declination sentinel; no CRS asserted");
        m.Shot("0", "0.0", 1000, 0, 0, 0, 0, false, "plain zero to major.minor zero");
        m.Shot("0.0", "12.65535", 2000, 90, 10, 0, 1, true, "Zażółć gęślą jaźń — " + new string('ą', 70));
        m.Shot("12.65535", "", 3000, 180, -10, 0, 2, false, "automatic trip splay");
        m.Shot("12.65535", "13.0", 4000, 270, 0, 0, -1, false, "unassigned trip");
        m.Save(root, "api-trips-ids");
    }

    static void References(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, -2, false, "Synthetic coordinates in unspecified CRS");
        m.Shot("0", "1", 1000, 90, 0, 0, 0, false, null);
        m.Reference("0", -4000000001L, -5000000002L, -1250, "ujemne E/N/Z; żadnego przypisania CRS");
        // Keep both references at the same source station: the binary oracle
        // concerns signed values, not a geographically meaningful survey fix.
        m.Reference("0", 6000000003L, 7000000004L, 1500250, "positive int64 E/N beyond int32");
        m.Save(root, "api-references");
    }

    static void Drawings(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, 0, false, "P01 synthetic drawing vertices");
        m.Shot("0", "1", 10000, 0, 0, 0, 0, false, null);
        m.Shot("1", "2", 10000, 90, 0, 0, 0, true, "flipped extended segment");
        string[] colors = { "black", "gray", "brown", "blue", "red", "green", "orange" };
        for (int i = 0; i < colors.Length; ++i)
        {
            int x = -6000 + i * 2000;
            m.Polygon(m.Plan, colors[i], new Point[] {
                new Point(x, -2000), new Point(x + 500, -1000), new Point(x + 1500, -1500) });
            m.Polygon(m.Side, colors[i], new Point[] {
                new Point(x, 2000), new Point(x + 500, 1000), new Point(x + 1500, 1500) });
        }
        m.Polygon(m.Plan, "black", new Point[] { new Point(-7500, 3500) });
        m.Polygon(m.Side, "orange", new Point[] { new Point(7500, -3500) });
        m.Section(m.Plan, new Point(-5000, -6000), "1", -1);
        m.Section(m.Plan, new Point(5000, -6000), "2", 16384);
        m.Section(m.Side, new Point(-5000, 6000), "1", -1);
        m.Section(m.Side, new Point(5000, 6000), "2", 16384);
        Set(m.Map, "x0", -1234); Set(m.Map, "y0", 5678);
        Set(Get(m.Plan, "mapping"), "x0", -100); Set(Get(m.Plan, "mapping"), "y0", 200);
        Set(Get(m.Side, "mapping"), "x0", 300); Set(Get(m.Side, "mapping"), "y0", -400);
        m.Save(root, "api-drawings");
    }

    [STAThread]
    static int Main(string[] args)
    {
        try
        {
            bool readOnly = args.Length == 3 && args[0] == "--read";
            bool rewrite = args.Length == 4 && args[0] == "--rewrite";
            if (args.Length != 2 && !readOnly && !rewrite)
                throw new ArgumentException("PocketTopoFixtures.exe PocketTopo.exe output-directory OR --read PocketTopo.exe input.top OR --rewrite PocketTopo.exe input.top output.top");
            System.Threading.Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
            App = Assembly.LoadFrom(Path.GetFullPath(args[(readOnly || rewrite) ? 1 : 0]));
            // Set process-local native defaults only. Public Config setters
            // write the user's registry, so deliberately do not call them.
            Set(T("Config"), "metric", true);
            Set(T("Config"), "angle", 360);
            Console.WriteLine("Assembly: " + App.FullName);
            Console.WriteLine("Source: " + App.Location);
            if (readOnly || rewrite)
            {
                Model probe = new Model();
                bool accepted = (bool)Call(probe.Data, "Read", Path.GetFullPath(args[2]), false);
                Console.WriteLine("Native DataSet.Read accepted: " + accepted);
                if (!accepted) return 2;
                if (rewrite)
                {
                    string output = Path.GetFullPath(args[3]);
                    if (File.Exists(output)) throw new IOException("Refusing to overwrite " + output);
                    Call(probe.Data, "Write", output);
                    Console.WriteLine("Native DataSet.Write: " + output);
                }
                return 0;
            }
            string root = Path.GetFullPath(args[1]);
            Directory.CreateDirectory(root);
            Cardinal(root);
            TripsAndIds(root);
            References(root);
            Drawings(root);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.ToString());
            return 1;
        }
    }
}
