# -*- coding: utf-8 -*-
import sys
import random
import telepot
from telepot.delegate import per_chat_id, create_open
import urllib2
from urllib2 import urlopen
from HTMLParser import HTMLParser
from yahoo_finance import Currency
from enchant import Dict
from random import choice 
from pprint import pprint
from random import randint

help_string = """
My name is UTKB - Universal Time Killer Bot!
You can always rely on me in case of time killing emergency!
You don't know what to read? - /reader will provide you with a fragment of book long enough to decide whether you want to read a full version.
Want to send a message to your English-speaking friend, but you are not sure in spelling? Use /check word to find out whether you are right or not.
Had a bad day? /sendkotik will make you smile!
Nobody sends you telegram stickers? I can do it! Just choose /sendsticker.
Want to read a webpage, but Roskmnadzor blocked it and you can't open it? Use /webanon url to receive a html file whith this page.
Want to spoil your mood type /currency USDRUB.
But never foreget that every cloud has a silver lining... Ask /compliment why.
"""


# Needed to deal with a website with fiction books.
class MyHTMLParser(HTMLParser):
    # These ones live in the very bottom of a typical page. We do not this tech info.
    junk_strings = [u'Это литературный проект', u'Как это работает?', u'NoCover дает', 
                u'Надеемся, что наш проект сумеет', u'Если у вас есть вопросы',
                u'admin@nocover.ru']

    def __init__(self):
        HTMLParser.__init__(self)
        self.printing = False
        
        result_ = ''
        self.result = result_.encode('utf-8') 

    # Parsing paragraphs
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.printing = True

    def handle_endtag(self, tag):
        self.tag = tag

        if tag == 'p':
            self.printing = False

    def handle_data(self, data):
        if self.printing == True:
            text = data.strip()

            if self.tag == 'p':
                text = text + '\n\n'

            for strain in self.junk_strings:
                if text.count(strain):
                    return
            self.data_out = text.encode('utf-8')



class Player(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Player, self).__init__(seed_tuple, timeout)

    def open(self, initial_msg, seed):
        self.sender.sendMessage('Hello! Starting our session.\n')
        self.sender.sendMessage(help_string)
        return True

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        user_id = msg['chat']['id']

        if content_type != 'text':
            if content_type == 'sticker': 
                self.sender.sendMessage('Wow! Nice sticker! Where did you get these?')
            else:
                self.sender.sendMessage('Meh, I only can parse text and stickers. Sorry.')
            return

        if msg['text'] == "/help": 
            self.sender.sendMessage(help_string)
            return

        elif '/check' in msg['text']:
            if len(msg['text'].split(' ')) < 2:
                self.sender.sendMessage("But WHAT would you want to check?")
                return 

            # Checks spelling 
            # Taking argument
            word = msg['text'].split(' ')[1].strip()
            dictionary = Dict("en_US")
            if dictionary.check(word):
                self.sender.sendMessage("Your spelling seems to be good!")
            else:
                self.sender.sendMessage("Well, this not correct. Did you mean something from below? ")                
                suggestions = str(" ".join(dictionary.suggest(word)))
                self.sender.sendMessage(suggestions)
            return


        elif '/sendsticker' in msg['text']:
            # File ids of some stickers
            file_ids = ['BQADBAADfgoAAv76ywAB14IfQL_VswYC', 
             'BQADBAADaAoAAv76ywAB37Qnda-rjJgC',
             'BQADBAADZAoAAv76ywABB-ORoHUpiI8C',
             'BQADAgADcwoAAkKvaQABJ9DdkZXZA9wC',
             'BQADAgADaQoAAkKvaQABrL9OF84Hk7kC',
             'BQADAgADfQoAAkKvaQABgH-KI2wmXFAC',
             'BQADBAADagADXSupAcBZICwpXF7JAg']

            # Sending to user.
            file_id = random.choice(file_ids)
            response = bot.sendSticker(user_id, file_id)
            return 

        elif '/sendkotik' in msg['text']:
            # It is very obvious what it does.
            cats_total = 14
            cat_id = randint(1, cats_total)            
            cat_path = 'kot' + str(cat_id) + '.jpg'
            
            # Sending to user.
            f = open(cat_path, 'rb')  
            response = bot.sendPhoto(user_id, f)
            return 

        elif '/webanon' in msg['text']:
            # Taking command argument
            if len(msg['text'].split(' ')) < 2:
                self.sender.sendMessage("But WHAT would you want to anonymize?")
                return 

            url = msg['text'].split(' ')[1].strip()

            # Adding some protocol 
            if 'http://' not in url:
                url = 'http://' + url
            
            # Anonymizing
            url = 'http://anonymouse.org/cgi-bin/anon-www.cgi/' + url
            self.sender.sendMessage("Downloading url anonymously for you.")
            response = urllib2.urlopen(url)
            html = response.read()
            with open('anonymized_document.html', 'w') as fout:
                fout.write(html)
            
            # Sending to user.
            f = open('anonymized_document.html', 'rb') 
            response = bot.sendDocument(user_id, f)
            return

        elif msg['text'] == "/compliment":
            # First of all, who are we addressing to?
            first_name = msg['from']['first_name']

            reinforcement = random.choice(["absolutely", "very", "really", "fairly", "extraordinally", "notably"])
            compliment = random.choice(["gorgeous", "marvellous", "interesting", "amazing", "fine", "excellent", 
                                        "gifted"])
            full_compliment = "Dear " + first_name + "! You are " + reinforcement + " " + compliment + "!\n";
            self.sender.sendMessage(full_compliment)

        elif msg['text'] == "/reader":
            # This website contains lots of book fragments
            connection = urlopen('http://nocover.ru/')
            data = connection.read()
            html = data.decode('utf-8', 'ignore')
            connection.close()
            parser = MyHTMLParser()
            parser.feed(html)  
            self.sender.sendMessage(parser.data_out)
            return

        elif '/currency' in msg['text']: 
            # E.g., USDRUB or PLNEUR

            if len(msg['text'].split(' ')) < 2:
                self.sender.sendMessage("What pair of currencies are we talking about?")
                return 

            currency_pair = Currency(msg['text'].split(' ')[1].strip())
            rate = currency_pair.get_rate()

            self.sender.sendMessage("Current rate for this currency pair is: " + str(rate))
            return 
        else:
            self.sender.sendMessage('What did you mean? Please type /help for instructions.')
            return

    def on_close(self, exception):
        if isinstance(exception, telepot.helper.WaitTooLong):
            self.sender.sendMessage('Going to get some rest. Goodbye!')


TOKEN = '176131681:AAGGLNBZ6MJSjEdnjQ1ARe0Tu3ZIw1wxWSQ'

bot = telepot.DelegatorBot(TOKEN, [(per_chat_id(), create_open(Player, timeout=2000000000)),])
bot.notifyOnMessage(run_forever=True)