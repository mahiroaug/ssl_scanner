import os
from command import get_table,convert_to_output
from datetime import date
from slack_sdk import WebClient

SLACK_CLIENT = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
SLACK_CHANNEL = os.environ["SLACK_CHANNEL_ID"]


def push_slackbot(now: date=date.today()):
    table = get_table()
    order_by_keys = {'id': ['ID'],
                    'expire': ['Valid_To'],
                    'scan': ['Last_Check'],
                    }
    rows = [convert_to_output(row,now) for row in table.find(order_by=order_by_keys['expire'])]
    
    
    msg = make_message([row for row in rows if row["Remaining_Days"] is not None and 0 <= row["Remaining_Days"] <= 15])
    if msg:
        post_message("[緊急]15日以内にタイムリミットな人たちでーす({})\n".format(now) + msg)
    
    msg = make_message([row for row in rows if row["Remaining_Days"] is not None and 15 < row["Remaining_Days"] <= 30])
    if msg:
        post_message("[注意]30日以内にタイムリミットな人たちでーす({})\n".format(now) + msg)
    
    msg = make_message([row for row in rows if row["Remaining_Days"] is not None and 30 < row["Remaining_Days"] <= 45])
    if msg:
        post_message("45日切ったよ。そろそろ更新準備した方がいいカモ({})\n".format(now) + msg)
    
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 45 < row["Remaining_Days"] <= 120])
    if msg:
        post_message("まだまだ余裕。({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 120 < row["Remaining_Days"] <= 400])
    if msg:
        post_message("高みの見物({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 400 < row["Remaining_Days"]])
    if msg:
        post_message("大富豪ですか？({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and row["Remaining_Days"] < 0])
    if msg:
        post_message("タイムパトロールに通報しました({})\n".format(now) + msg)
    
    
    msg = make_message_null([row for row in rows if row["Remaining_Days"] is None])
    if msg:
        post_message("データが取得できないよ？domainの生存確認をしてみて({})\n".format(now) + msg)



def make_message(source_list: list) -> str:
    format_str = "• `[{:2}days]{}~{}` `{:28}` |{:28}|{}|{}\n"
    #msg = format_str.format("FROM-date","EXPIRY-date","---","Domain","common-name","issuer","スキャン日時")    
    msg = ""
    for row in source_list:
        msg += format_str.format(row["Remaining_Days"], \
                                    row["Valid_From"].replace("Z","").replace("-",""), \
                                    row["Valid_To"].replace("Z","").replace("-",""), \
                                    row["Domain"], \
                                    row["Subject"], \
                                    row["Issuer"], \
                                    row["Last_Check"].replace("Z","").replace("-",""))
    return(msg)

def make_message_short(source_list: list) -> str:
    format_str = "• `[{:2}days]{}~{}` `{:28}` \n"
    msg = ""
    for row in source_list:
        msg += format_str.format(row["Remaining_Days"], \
                                    row["Valid_From"].replace("Z","").replace("-",""), \
                                    row["Valid_To"].replace("Z","").replace("-",""), \
                                    row["Domain"])
    return(msg)

def make_message_null(source_list: list) -> str:
    format_str = "• `{:30}`\n"
    msg = ""
    for row in source_list:
        msg += format_str.format(row["Domain"])
    return(msg)



def post_message(msg: str):
    chunk_size=2900
    start=0
    while start < len(msg):        
        if (start + chunk_size) < len(msg):
            end = msg.rfind("\n", start, start+ chunk_size)
            if end > start:
                chunk_size = end - start + 1
        chunk = msg[start:start+chunk_size]
        print("len=" + str(len(msg)) + ", start=" + str(start) + ", chunk_size=" + str(chunk_size))
        print(chunk)
        start = start + chunk_size
        
        try:
            blocks_list = [{"type": "section", "text": {"type": "mrkdwn", "text": chunk}}]
            response = SLACK_CLIENT.chat_postMessage(channel=SLACK_CHANNEL,blocks=blocks_list,as_user=True)
            print("slackResponse: ", response)
        except Exception as e:
            print("Error posting message: {}".format(e))


if __name__ == '__main__':
    push_slackbot()
