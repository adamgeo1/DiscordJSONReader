import json
import pathlib

INPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Input' # Input JSON Discord logs folder
OUTPUT_PATH = pathlib.Path(__file__).parent.absolute() / 'Output' # Output formatted Discord messages folder

class Message:
    author_ids_and_names = {}
    message_ids_and_line_numbers = {}

    def __init__(self, line_num, message):
        self.line_num = line_num
        self.message_id = message.get('id', 0)
        self.author_id = message.get('author', {}).get('id')
        self.author = message.get('author', {}).get('global_name') or message.get('author', {}).get('username')
        self.content = message.get('content', "")
        self.timestamp = message.get('timestamp', "")[:10] + " " + message.get('timestamp', "")[11:19]
        self.mentioned_id = None
        if message.get('mentions'):
            self.mentioned_id = message['mentions'][0].get('id')
        self.referenced_message_id = None
        if message.get('referenced_message'):
            self.referenced_message_id = message['referenced_message'].get('id')
            self.referenced_message = message['referenced_message']
        Message.author_ids_and_names[self.author_id] = self.author
        Message.message_ids_and_line_numbers[self.message_id] = self.line_num

    def replace_id_with_name(self):
        words = self.content.split()
        new_words = []
        for word in words:
            if word.startswith("<@") and word.endswith(">"):
                user_id = word[2:-1]
                name = Message.author_ids_and_names.get(user_id, f"@{user_id}")
                new_words.append(f"@{name}")
            else:
                new_words.append(word)
        return " ".join(new_words)

    def __str__(self):
        message_line = f"{self.line_num}. `{self.timestamp}`  {self.author}: \""
        reply_info = ""
        if self.referenced_message_id:
            reply = getattr(self, 'referenced_message', None)
            if reply and reply.get('author'):
                reply_name = reply['author'].get('global_name') or reply['author'].get('username')
                reply_line_num = Message.message_ids_and_line_numbers.get(str(reply.get('id')), 0)
                reply_info = f"Replying to @{reply_name} from line `{reply_line_num}` - "
        return message_line + reply_info + self.replace_id_with_name()


def main():
    for file in INPUT_PATH.iterdir():
        if file.is_file():

            messages = []

            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for channel, message_list in data.items():
                    line_num = 1
                    messages.append(f"## {channel}:\n")
                    for i in range(len(data[channel]) - 1, -1, -1):
                        messages.append(Message(line_num, data[channel][i]))
                        line_num += 1
                    messages.append("") # line spacing between channel names

            with open(OUTPUT_PATH / f"{file.name}Output.md", 'w', encoding='utf-8') as f:
                f.write(f"# {file.name}\n")
                for message in messages:
                    f.write(str(message) + "\n")

if __name__ == '__main__':
    main()

