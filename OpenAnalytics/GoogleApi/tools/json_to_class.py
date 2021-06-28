from pathlib import Path
import io
import json

out_file = r"/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/GoogleApi/tools/out.txt"
json_file = r"/home/hirvin/Documents/Dev/OpenAnalytics/OpenAnalytics/GoogleApi/tools/person.json"

DEF_PARAM_BASE = "{}=None,"
DEF_SELF_PARAM = "self.{} = {}"

def json_to_class(json_file=json_file, out_file=out_file):
    json_path = Path(json_file)
    if json_path.exists():
        with open(json_path) as read_file:
            in_json = json.load(read_file)
    param_io = io.StringIO('(')
    self_io = io.StringIO('')
    for e in in_json.keys():
        param_io.write(DEF_PARAM_BASE.format(e))
        self_io.write(DEF_SELF_PARAM.format(e, e) + "\n")
    param_io.write(')')

    out_path = Path(out_file)
    with open(out_path, "w") as out:
        out.write(param_io.getvalue())
        out.write("\n\n")
        out.write(self_io.getvalue())

    print(param_io.getvalue())
    print(self_io.getvalue())

if __name__ == "__main__":
    json_to_class()