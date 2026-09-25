// Research helper for P05, NOT the future converter or a .top writer.
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

class PocketTopoProjectionFixtures
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
            using (StreamWriter data = new StreamWriter(Path.Combine(dir, "native-coordinates.tsv"), false, new UTF8Encoding(false)))
            {
                data.WriteLine("source_index\tfrom\tto\tnum\tx\ty\th\td\tdx\tdy\tdh\tdd\tstart_num\tstart_x\tstart_y\tstart_h\tstart_d");
                for (int index = 0; index < check.Shots.Count; ++index)
                {
                    object shot = check.Shots[index];
                    data.Write(index);
                    foreach (string field in new string[] { "from", "to", "num", "x", "y", "h", "d", "dx", "dy", "dh", "dd" })
                        data.Write("\t" + Get(shot, field));
                    object start = Get(shot, "start");
                    foreach (string field in new string[] { "num", "x", "y", "h", "d" })
                        data.Write("\t" + (start == null ? "" : Get(start, field).ToString()));
                    data.WriteLine();
                }
            }
            Console.WriteLine("Native DataSet.Read + Survey.WriteText + DXFWriter.WriteDXF: OK " + name);
        }
    }

    static void Loop(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, 0, false, "P05 unadjusted nonclosing loop");
        m.Shot("0", "1", 10000, 0, 0, 0, 0, false, "north");
        m.Shot("1", "2", 6000, 90, 0, 0, 0, false, "east");
        m.Shot("2", "0", 11000, 210, 0, 0, 0, false, "nonclosing loop to known root");
        m.Shot("2", "3", 3000, 180, 30, 0, 0, true, "branch after loop");
        m.Save(root, "loop");
    }
    static void Branch(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, 0, false, "P05 branches and reverse attachment");
        m.Shot("0", "1", 10000, 0, 0, 0, 0, false, "north");
        m.Shot("2", "1", 4000, 270, 0, 0, 0, true, "reverse attachment, flipped");
        m.Shot("1", "3", 6000, 180, 0, 0, 0, false, "second branch");
        m.Shot("2", "4", 2000, 90, 30, 0, 0, false, "continues flipped parent, own Flip false");
        m.Shot("3", "5", 3000, 270, -30, 0, 0, true, "third direction, own Flip true");
        m.Shot("1", "", 2000, 45, 30, 0, 0, false, "branch splay");
        m.Shot("2", "", 2000, 180, -30, 0, 0, false, "reversed branch splay");
        m.Save(root, "branch");
    }
    static void Sections(string root)
    {
        Model m = new Model();
        m.Trip(632401344000000000L, 5, false, "P05 XSection and declination");
        m.Shot("0", "1", 10000, 0, 0, 0, 0, false, "trunk incoming");
        m.Shot("1", "2", 8000, 90, 0, 0, 0, false, "trunk outgoing");
        m.Shot("1", "", 2000, 0, 0, 0, 0, false, "splay north");
        m.Shot("1", "", 3000, 90, 0, 0, 0, false, "splay east");
        m.Shot("1", "", 4000, 180, 0, 0, 0, false, "splay south");
        m.Shot("1", "", 5000, 270, 0, 0, 0, false, "splay west");
        m.Shot("1", "", 6000, 45, 30, 0, 0, false, "splay northeast up");
        m.Shot("1", "", 7000, 225, -30, 0, 0, false, "splay southwest down");
        m.Shot("1", "", 1000, 0, 90, 0, 0, false, "splay vertical up");
        int[] directions = { -1, 0, 8192, 16384, 32768 };
        for (int i = 0; i < directions.Length; ++i)
        {
            m.Section(m.Plan, new Point(-15000 + i * 10000, 15000), "1", directions[i]);
            m.Section(m.Side, new Point(-15000 + i * 10000, 15000), "1", directions[i]);
        }
        m.Save(root, "xsection");
    }
    [STAThread]
    static int Main(string[] args)
    {
        try
        {
            if (args.Length != 2) throw new ArgumentException("PocketTopoProjectionFixtures.exe PocketTopo.exe new-output-directory");
            System.Threading.Thread.CurrentThread.CurrentCulture = CultureInfo.InvariantCulture;
            App = Assembly.LoadFrom(Path.GetFullPath(args[0]));
            Set(T("Config"), "metric", true);
            Set(T("Config"), "angle", 360);
            Console.WriteLine("Assembly: " + App.FullName);
            Console.WriteLine("Source: " + App.Location);
            string root = Path.GetFullPath(args[1]);
            Directory.CreateDirectory(root);
            using (StreamWriter palette = new StreamWriter(Path.Combine(root, "palette.tsv"), false, new UTF8Encoding(false)))
            {
                palette.WriteLine("name\tred\tgreen\tblue\talpha");
                foreach (string name in new string[] { "black", "gray", "brown", "blue", "red", "green", "orange" })
                {
                    Color color = ((Pen)Get(T("MainForm"), name)).Color;
                    palette.WriteLine(name + "\t" + color.R + "\t" + color.G + "\t" + color.B + "\t" + color.A);
                }
            }
            Loop(root);
            Branch(root);
            Sections(root);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.ToString());
            return 1;
        }
    }
}
