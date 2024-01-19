import tkinter as tk
import time
import json
from openai import OpenAI
from threading import Thread
from uuid import uuid4
import tiktoken


""" 
tkinter UI for a ChatGPT app that uses the GPT API
Made so that GPT-4 can be used and payed for per each message rather than buying the ChatGPT Plus for 20€ per month.


functions:
- Save and load conversations
    - Different conversations are stored in a json file and can be loaded to continue the conversation from the UI

- Active conversation can be deleted from UI
- New conversation can be started from UI

- adds previous messages from conversation to GPT prompt. The previous message length is limited by the following variables in GPT class:
    self.max_messages = 5 # max number of messages that can be added to prompt
    self.max_history_tokens = 1000 # max number of tokens that previous messages can have
    
    which ever limit is reached first will be the limit for the prompt.
"""

API_KEY = "..."

class UI:
    def __init__(self, root):  
        self.root = root
        self.MAX_HISTORY = 30
        self.root.title("GPT-4 Chat")
        
        self.bg_color = "#333333"
        self.text_color = "#FFFFFF"
        self.button_color = "#555555"
        self.entry_bg_color = "#555555"

        self.root.configure(bg=self.bg_color)

        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(pady=20, fill=tk.BOTH, expand=True)  # Allow main_frame to expand and fill space

        # Chat history area
        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y)  # Align to the left side
        self.chat_history = tk.Text(self.main_frame, wrap='word', bg=self.bg_color, fg=self.text_color)
        self.chat_history.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)  # Expand in both X and Y directions
        self.chat_history.config(state='disabled')


        # User input box
        self.entry_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.entry_frame.pack(pady=5, fill=tk.X, expand=False)  # Expand only in X direction
        self.user_input = tk.Text(self.entry_frame, bg=self.entry_bg_color, fg=self.text_color, insertbackground=self.text_color, height=10)
        self.user_input.pack(expand=True, fill=tk.BOTH, padx=20, pady=5, side=tk.LEFT)  # Expand and fill space in all directions


        # Bind the Enter key to a function that inserts a newline
        self.user_input.bind('<Return>', self.insert_newline)
        
        # delete button 
        self.delete_button = tk.Button(self.entry_frame, text="Delete conversation", command=self.delete_message, bg=self.button_color, fg=self.text_color)
        self.delete_button.pack(side=tk.RIGHT, padx=10)
        
        # Send button
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg=self.button_color, fg=self.text_color)
        self.send_button.pack(side=tk.RIGHT, padx=10)
        

    def create_button(self, text, command):
        button = tk.Button(self.button_frame, text=text, bg=self.button_color, fg=self.text_color, command=command)
        button.pack(side=tk.TOP, fill=tk.X)

    def insert_newline(self, event):
        self.user_input.insert(tk.INSERT, '\n')
    
    def delete_message(self):
        if self.delete_message_callback:
            self.delete_message_callback()
    
    def create_new_conversation_button(self):
        self.new_convo_button = tk.Button(self.button_frame, text="New Conversation", bg=self.button_color, fg=self.text_color, command=self.new_conversation)
        self.new_convo_button.pack(side=tk.TOP, fill=tk.X)

    def new_conversation(self):
        if self.new_conversation_callback:
            self.new_conversation_callback()
    
    def send_message(self):
        message = self.user_input.get("1.0", tk.END).strip()
        if message:
            message = f"\n{message}"
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, "You: " + message + "\n")
            # Placeholder for where you would generate a response
            self.chat_history.insert(tk.END, "\n\nChatGPT: \nThis is where the response would go.\n")
            self.chat_history.yview(tk.END)  # Auto-scroll to the bottom
            self.chat_history.config(state='disabled')
            self.user_input.delete(0, tk.END)

    def create_button(self, text, command):
        button = tk.Button(self.button_frame, text=text, bg=self.button_color, fg=self.text_color, command=command)
        button.pack(side=tk.TOP, fill=tk.X)
        return button  # Return the created button

# manage chat history
class ChatHistory:
    def __init__(self, file_path="chat_history.json") -> None:
        self.file_path = file_path
        self.conversations = {}
        
    def load(self):
        with open(self.file_path, 'r') as file:
            self.conversations = json.load(file)

    def save(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.conversations, file, indent=4)

    def add_message(self, conversation_id, sent, response):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {"messages": []}

        message = {
            "timestamp": time.time(),
            "sent": sent,
            "response": response
        }
        self.conversations[conversation_id]["messages"].append(message)
        self.save()

    def get_messages(self, conversation_id):
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["messages"]
        return []

    def new_conversation(self, conversation_id):
        self.conversations[conversation_id] = {"messages": []}
        self.save()


# main class for the app
class GPT:
    def __init__(self):
        self.conversation_buttons = {}
        # Load all old chats
        self.chat_history = ChatHistory()
        self.chat_history.load()
        
        # Initialize the UI
        self.root = tk.Tk()
        self.ui = UI(self.root)
        self.ui.send_button.config(command=self.message)  # Link send_message method
        
        # Initialize a variable to store the current conversation ID
        self.current_conversation_id = str(uuid4())
        
        # Link the new conversation callback from the UI
        self.ui.create_new_conversation_button()
        self.ui.new_conversation_callback = self.start_new_conversation
        # Load chat buttons
        self.load_chat_buttons()
        self.ui.delete_message_callback = self.delete_message
        
        self.gpt_client = OpenAI(
            api_key = API_KEY
        )
        # Limits for history that will be passed to GPT        
        self.max_messages = 5
        self.max_history_tokens = 1000
        self.encoder = tiktoken.encoding_for_model("gpt-4")


    def message(self):
        Thread(target=self.send_message).start()
        
    def prompt_gpt(self, prompt, model="gpt-4"):
        
        chat_completion = self.gpt_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model = model
        )
        return chat_completion.choices[0].message.content

    def delete_message(self):
        if self.current_conversation_id not in self.chat_history.conversations:
            return
        self.ui.chat_history.config(state=tk.NORMAL)
        self.ui.chat_history.delete(1.0, tk.END)
        self.ui.chat_history.config(state='disabled')
        
        # print(self.current_conversation_id)
        # print(self.conversation_buttons)
        # destroy button from UI
        self.conversation_buttons[self.current_conversation_id].destroy()

        # delete from json file
        self.chat_history.conversations.pop(self.current_conversation_id)
        self.chat_history.save()
    
    def start_new_conversation(self):
        # dont create a new conversation if the current one is empty
        if self.chat_history.get_messages(self.current_conversation_id):
            name = self.chat_history.conversations[self.current_conversation_id]["messages"][0]["sent"][:20]
            self.ui.create_button(name, lambda cid=self.current_conversation_id: self.load_chat(cid))
        
        self.current_conversation_id = str(uuid4())
        # Update the UI
        self.ui.chat_history.config(state=tk.NORMAL)
        self.ui.chat_history.delete(1.0, tk.END)
        self.ui.chat_history.config(state='disabled')

        self.ui.user_input.delete(1.0, tk.END)
        
    
    def load_chat_buttons(self):
        for conversation_id in self.chat_history.conversations:
            name = self.chat_history.conversations[conversation_id]["messages"][0]["sent"][:20]
            button = self.ui.create_button(name, lambda cid=conversation_id: self.load_chat(cid))
            
            self.conversation_buttons[conversation_id] = button 
        
    def load_chat(self, conversation_id):
        messages = self.chat_history.get_messages(conversation_id)
        self.ui.chat_history.config(state=tk.NORMAL)
        self.ui.chat_history.delete(1.0, tk.END)
        
        for message in messages:
            self.ui.chat_history.insert(tk.END, f"{message['sent']}\n{message['response']}\n\n")
        self.ui.chat_history.yview(tk.END)
        self.ui.chat_history.config(state='disabled')
        self.current_conversation_id = conversation_id
    
    def send_message(self):
        # Get message from UI
        message = self.ui.user_input.get("1.0", tk.END).strip()

        if message:
            # add previous messages to prompt.
            previous_messages = self.chat_history.get_messages(self.current_conversation_id)
            
            history = ""
            
            for i, m in enumerate(reversed(previous_messages)):
                string = f"\nUser: \n{m['sent']}\n\nAI response: \n{m['response']}\n"
                if len(self.encoder.encode(history + string)) > self.max_history_tokens or i >= self.max_messages - 1:
                    break
                
                history += string

            final_message = f"{history}User:\n{message}"
            # print(final_message)
            
            response = self.prompt_gpt(final_message)
            
            self.ui.chat_history.config(state=tk.NORMAL)
            self.ui.chat_history.insert(tk.END, "You: " + message + "\n\n" + "ChatGPT: " + response + "\n\n")
            self.ui.chat_history.yview(tk.END)
            self.ui.chat_history.config(state='disabled')
            self.ui.user_input.delete(1.0, tk.END)
            
            self.chat_history.add_message(self.current_conversation_id, message, response)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    chat_app = GPT()
    chat_app.run()
