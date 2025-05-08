import json
import pathlib

INPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Input' # Input JSON Discord logs folder
OUTPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Output' # Output formatted Discord messages folder

class Message:
    author_ids_and_names = {} # dict to save names for mentions and reply references
    message_ids_and_line_numbers = {} # dict to save message ids and what line numbers they appear on for reply references

    def __init__(self, line_num, message):
        self.line_num = line_num
        self.message_id = message.get('id', 0) # gets id of the message
        self.author_id = message.get('author', {}).get('id') # gets the author id of the message
        self.author = message.get('author', {}).get('global_name') or message.get('author', {}).get('username') # gets either the author's "global_name" (possibly nickname?) and if that doesn't exist, gets their discord username
        self.content = message.get('content', "") # gets content/text of their message
        self.timestamp = message.get('timestamp', "")[:10] + " " + message.get('timestamp', "")[11:19] # truncated time stamp
        self.mentioned_id = None
        if message.get('mentions'):
            self.mentioned_id = message['mentions'][0].get('id') # gets if they either @'d anyone, also shows up if they replied to someone
        self.referenced_message_id = None
        if message.get('referenced_message'): # gets if they replied to another message
            self.referenced_message_id = message['referenced_message'].get('id') # gets the id of the replied to message so we can find the line number of that message
            self.referenced_message = message['referenced_message']
        Message.author_ids_and_names[self.author_id] = self.author # adds author name to dict
        Message.message_ids_and_line_numbers[self.message_id] = self.line_num # adds message ids to dict

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
        return " ".join(new_words) # returns modified content message

    def __str__(self):
        message_line = f"{self.line_num}. `{self.timestamp}`  {self.author}: \"" # prefix for every message
        reply_info = ""
        if self.referenced_message_id:
            reply = getattr(self, 'referenced_message', None) # gets the referenced message from the object
            if reply and reply.get('author'): # just makes sure they exist
                reply_name = reply['author'].get('global_name') or reply['author'].get('username')
                reply_line_num = Message.message_ids_and_line_numbers.get(str(reply.get('id')), 0)
                reply_info = f"Replying to @{reply_name} from line `{reply_line_num}` - " # adds if they are replying to someone to the output string
        return message_line + reply_info + self.replace_id_with_name() # returns final output message


def main():
    for file in INPUT_PATH.iterdir(): # iterates over every file in the input path
        if file.is_file():

            messages = []

            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f) # loads json file
                for channel, message_list in data.items():
                    line_num = 1
                    messages.append(f"## {channel}:\n") # displays channel name
                    for i in range(len(data[channel]) - 1, -1, -1): # the json is saved in reverse chronological order, so we iterate backwards
                        messages.append(Message(line_num, data[channel][i]))
                        line_num += 1
                    messages.append("") # line spacing between channel names

            with open(OUTPUT_PATH / f"{file.name}Output.md", 'w', encoding='utf-8') as f:
                f.write(f"# {file.name}\n") # adds the input file name to the top
                for message in messages:
                    f.write(str(message) + "\n")

if __name__ == '__main__':
    main()

