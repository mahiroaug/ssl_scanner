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
    if not msg:
        post_message("[緊急]15日以内にタイムリミットな人たちでーす({})\n".format(now) + msg)
    
    msg = make_message([row for row in rows if row["Remaining_Days"] is not None and 15 < row["Remaining_Days"] <= 30])
    if not msg:
        post_message("[注意]30日以内にタイムリミットな人たちでーす({})\n".format(now) + msg)
    
    msg = make_message([row for row in rows if row["Remaining_Days"] is not None and 30 < row["Remaining_Days"] <= 45])
    if not msg:
        post_message("45日切ったよ。そろそろ更新準備した方がいいカモ({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 45 < row["Remaining_Days"] <= 120])
    if not msg:
        post_message("まだまだ余裕。({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 120 < row["Remaining_Days"] <= 400])
    if not msg:
        post_message("高みの見物({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and 400 < row["Remaining_Days"]])
    if not msg:
        post_message("大富豪ですか？({})\n".format(now) + msg)
    
    msg = make_message_short([row for row in rows if row["Remaining_Days"] is not None and row["Remaining_Days"] < 0])
    if not msg:
        post_message("タイムパトロールに通報しました({})\n".format(now) + msg)
    
    msg = make_message_null([row for row in rows if row["Remaining_Days"] is None])
    if not msg:
        post_message("データが取得できないよ？domainの生存確認をしてみて({})\n".format(now) + msg)



def make_message(source_list: list) -> str:
    format_str = "• {}~{} [{:3}days] {:28}|{:28}|{}|{}\n"
    #msg = format_str.format("FROM-date","EXPIRY-date","---","Domain","common-name","issuer","スキャン日時")    
    msg = "\`\`\` "

    for row in source_list:
        msg += format_str.format(row["Valid_From"].replace("Z","").replace("-",""), \
                                    row["Valid_To"].replace("Z","").replace("-",""), \
                                    row["Remaining_Days"], \
                                    row["Domain"], \
                                    row["Subject"], \
                                    row["Issuer"], \
                                    row["Last_Check"].replace("Z","").replace("-",""))
    msg += " `\`\`"
    return(msg)

def make_message_short(source_list: list) -> str:
    format_str = "• {}~{},`[{:3}days]`,`{:30}`\n"
    #msg = format_str.format("FROM-date","EXPIRY-date","---","Domain")
    msg = ""
    
    for row in source_list:
        msg += format_str.format(row["Valid_From"].replace("Z","").replace("-",""), \
                                    row["Valid_To"].replace("Z","").replace("-",""), \
                                    row["Remaining_Days"], \
                                    row["Domain"])
    return(msg)

def make_message_null(source_list: list) -> str:
    format_str = "• `{:30}`\n"
    msg = ""
    
    for row in source_list:
        msg += format_str.format(row["Domain"])
    return(msg)



def post_message(msg: str):
    print(msg)
    try:
        blocks_list = [{"type": "section", "text": {"type": "mrkdwn", "text": msg}}]
        response = SLACK_CLIENT.chat_postMessage(channel=SLACK_CHANNEL,blocks=blocks_list,as_user=True)
        print("slackResponse: ", response)
    except Exception as e:
        print("Error posting message: {}".format(e))

        
if __name__ == '__main__':
    push_slackbot()
