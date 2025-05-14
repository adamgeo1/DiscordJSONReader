import json
import pathlib
from datetime import datetime, time
import math
from operator import index

INPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Input' # Input JSON Discord logs folder
OUTPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Output' # Output formatted Discord messages folder

def format_timestamp(string):
    return string[:10] + " " + string[11:19]


class Message:
    author_names_and_number_of_messages = {}
    author_names_and_number_of_messages_sent_between_eight_and_five = {}
    author_names_and_total_words = {}

    author_ids_and_names = {} # dict to save names for mentions and reply references
    message_ids_and_line_numbers = {} # dict to save message ids and what line numbers they appear on for reply references

    def __init__(self, line_num, message, channel):
        self.line_num = line_num
        self.message_id = message.get('id', 0) # gets id of the message
        self.author_id = message.get('author', {}).get('id') # gets the author id of the message
        self.author = message.get('author', {}).get('global_name') or message.get('author', {}).get('username') # gets either the author's "global_name" (possibly nickname?) and if that doesn't exist, gets their discord username
        self.content = message.get('content', "") # gets content/text of their message
        self.timestamp = format_timestamp(message.get('timestamp', "")) # truncated time stamp
        self.mentioned_id = None
        if message.get('mentions'):
            self.mentioned_id = message['mentions'][0].get('id') # gets if they either @'d anyone, also shows up if they replied to someone
        self.referenced_message_id = None
        self.referenced_message = None
        if message.get('referenced_message'): # gets if they replied to another message
            self.referenced_message_id = message['referenced_message'].get('id') # gets the id of the replied to message so we can find the line number of that message
            self.referenced_message = message['referenced_message']
        self.attachments = None
        if message.get('attachments'):
            self.attachments = message['attachments'][0].get('content_type', 'null')
        Message.author_ids_and_names[self.author_id] = self.author # adds author name to dict
        Message.message_ids_and_line_numbers[self.message_id] = self.line_num # adds message ids to dict

        if channel != "introductions" and channel != "general":
            Message.author_names_and_number_of_messages[self.author] = Message.author_names_and_number_of_messages.get(self.author, 0) + 1
            dt = datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S")
            if time(8, 0, 0) <= dt.time() <= time(17, 0, 0):
                Message.author_names_and_number_of_messages_sent_between_eight_and_five[self.author] = Message.author_names_and_number_of_messages_sent_between_eight_and_five.get(self.author, 0) + 1
            Message.author_names_and_total_words[self.author] = Message.author_names_and_total_words.get(self.author, 0) + len(self.content.split())

    def replace_id_with_name(self): # replaces "<@12345678>" id in message with said person's username
        words = self.content.split()
        new_words = []
        for word in words:
            if word.startswith("<@") and word.endswith(">"):
                user_id = word[2:-1]
                name = Message.author_ids_and_names.get(user_id, f"@{user_id}")
                new_words.append(f"@{name}")
            else:
                new_words.append(word)
        return " ".join(new_words) + "\"" # returns modified content message (the end " was lost somewhere along the way)

    def get_time_difference(self, message): # function to find how long it took for someone to reply to another person
        try:
            dt1 = datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S")
            dt2 = datetime.strptime(format_timestamp(message['timestamp']), "%Y-%m-%d %H:%M:%S")
            return dt1 - dt2
        except:
            return None

    def __str__(self):
        message_line = f"{self.line_num}. `{self.timestamp}`  {self.author}: \"" # prefix for every message
        reply_info = ""
        if self.referenced_message_id:
            if self.referenced_message and self.referenced_message.get('author'): # just makes sure they exist
                reply_name = self.referenced_message['author'].get('global_name') or self.referenced_message['author'].get('username')
                reply_line_num = Message.message_ids_and_line_numbers.get(str(self.referenced_message.get('id')), 0)
                reply_info = f"Replying to @{reply_name} from line `{reply_line_num}` - " # adds if they are replying to someone to the output string
        if self.attachments:
            message_line += f"(Attachments: {self.attachments}) "
        return message_line + reply_info + self.replace_id_with_name() # returns final output message


def calculate_time_stats(messages):
    author_reply_deltas = {}  # stores all time differences

    for message in messages:
        if isinstance(message, Message) and message.referenced_message:
            delta = message.get_time_difference(message.referenced_message)
            if delta:
                seconds = delta.total_seconds()
                author_reply_deltas.setdefault(message.author, []).append(seconds)

    author_stats = {}
    for author, times in author_reply_deltas.items():
        avg = sum(times) / len(times)
        standard_deviation = math.sqrt(sum((x - avg) ** 2 for x in times) / len(times))
        author_stats[author] = (avg, standard_deviation, len(times))

    return author_stats


def main():

    for file in INPUT_PATH.iterdir(): # iterates over every file in the input path
        if file.is_file():

            messages = []

            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f) # loads json file
                for channel, message_list in data.items():
                    line_num = 1
                    messages.append(f"### **{channel}**\n") # displays channel name
                    for i in range(len(data[channel]) - 1, -1, -1): # the json is saved in reverse chronological order, so we iterate backwards
                        messages.append(Message(line_num, data[channel][i], channel))
                        line_num += 1
                    messages.append("") # line spacing between channel names

            with open(OUTPUT_PATH / f"{file.name}Output.md", 'w', encoding='utf-8') as f:
                f.write(f"## **Output**\n")
                for message in messages:
                    f.write(str(message) + "\n")

            author_time_stats = calculate_time_stats(messages)

            with open(OUTPUT_PATH / f"{file.name}Statistics.txt", 'w', encoding='utf-8') as f:
                f.write(f"{file.name}\n")  # adds the input file name to the top
                f.write(f"\nTotal number of words per person:\n")
                for author in Message.author_names_and_total_words:
                    f.write(f"\t- {author}: {Message.author_names_and_total_words[author]}\n")
                f.write(f"\nNumber of messages per person:\n")
                for author in Message.author_names_and_number_of_messages:
                    Message.author_names_and_number_of_messages[author] > 1 and f.write(f"\t- {author}: {Message.author_names_and_number_of_messages[author]}\n")
                f.write(f"\nNumber of messages sent between 8 AM and 5 PM per person:\n")
                for author in Message.author_names_and_number_of_messages_sent_between_eight_and_five:
                    f.write(f"\t- {author}: {Message.author_names_and_number_of_messages_sent_between_eight_and_five[author]}\n")
                f.write(f"\nTime response statistics per person:\n") # line breaks
                for author, (avg, standard_deviation, num_responses) in author_time_stats.items():
                    f.write(f"\t- {author}:\n")
                    f.write(f"\t\t- Total responses: {num_responses}\n")
                    f.write(f"\t\t- Average response time: {avg:.2f} seconds\n")
                    f.write(f"\t\t- Standard deviation: {standard_deviation:.2f} seconds\n")

            # resetting all dicts for the next file
            Message.author_ids_and_names = {}
            Message.author_names_and_total_words = {}
            Message.author_names_and_number_of_messages = {}
            Message.author_names_and_number_of_messages_sent_between_eight_and_five = {}
            Message.message_ids_and_line_numbers = {}


if __name__ == '__main__':
    main()

