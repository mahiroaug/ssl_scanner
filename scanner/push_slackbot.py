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
    msg_u60 = make_message([row for row in rows if row["Remaining_Days"] is not None and row["Remaining_Days"] <= 60])
    msg_o61 = make_message([row for row in rows if row["Remaining_Days"] is not None and 60 < row["Remaining_Days"]])
    
    header = "定期スキャン結果 ({})".format(now)
    post_message(header)
    post_message(msg_u60)
    post_message(msg_o61)


def make_message(source_list: list) -> str:
    format_str = "• {},{},`[{:3}days]`,`{:30}`,{:30},{},{}\n"
    msg = format_str.format("FROM-date","EXPIRY-date","---","Domain","common-name","issuer","スキャン日時")

    for row in source_list:
        msg += format_str.format(row["Valid_From"].replace("Z",""), \
                                    row["Valid_To"].replace("Z",""), \
                                    row["Remaining_Days"], \
                                    row["Domain"], \
                                    row["Subject"], \
                                    row["Issuer"], \
                                    row["Last_Check"].replace("Z",""))
    return(msg)


def post_message(msg: str):
    print(msg)
    try:
        blocks_list = [{"type": "section", "text": {"type": "mrkdwn", "text": msg}}]
        response = SLACK_CLIENT.chat_postMessage(channel=SLACK_CHANNEL,blocks=blocks_list,as_user=True)
        print("slackResponse: ", response)
    except SlackApiError as e:
        print("Error posting message: {}".format(e))

        
if __name__ == '__main__':
    push_slackbot()
