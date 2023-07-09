from argparse import ArgumentParser
import json
import pandas as pd
from pathlib import Path

def parse_json(arg):
    return json.loads(Path(arg).read_text())

def rtm_backup_to_csv():
    parser = ArgumentParser()
    parser.add_argument("backup", type=Path)
    
    args = parser.parse_args()

    copy_to = Path(__file__).parent / args.backup.name
    copy_to.write_bytes(args.backup.read_bytes())

    rtm_backup = parse_json(args.backup)
    tasks = pd.DataFrame(rtm_backup["tasks"])
    lists = pd.DataFrame(rtm_backup["lists"])
    joined = tasks.merge(lists, how="left", left_on="list_id", right_on="id", suffixes=("", "_list"))

    # Full dadta
    out_file = args.backup.name.replace(".json", "_tasks.csv")
    joined.to_csv(out_file, index=False)

    # Triage format
    out_file = args.backup.name.replace(".json", "_triage.csv")
    triage = joined[joined["date_completed"].isnull()]
    triage = triage[~triage["repeat_every"]]
    triage = triage[["name", "name_list", "date_due"]]
    triage["date_due"] = pd.to_datetime(triage["date_due"], unit="ms").dt.date
    triage.to_csv(out_file, index=False)


if __name__ == "__main__":
    rtm_backup_to_csv()
