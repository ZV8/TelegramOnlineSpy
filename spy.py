from datetime import datetime, timedelta
from sys import argv, exit
from telethon import TelegramClient, events, connection
from telethon.tl.types import UserStatusRecently, UserStatusEmpty, UserStatusOnline, UserStatusOffline, PeerUser, PeerChat, PeerChannel
from time import mktime, sleep
import telethon.sync
from threading import Thread
import collections.abc

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
API_HASH = 'xxxxxx'  # Получите на https://my.telegram.org/apps
API_ID = '12345'      # Получите на https://my.telegram.org/apps
BOT_TOKEN = "xxxxxx"  # Ваш токен бота
USER_NAME = "xxxxxx"  # Ваше имя пользователя в Telegram

client = TelegramClient('data_thief', API_ID, API_HASH)

client.connect()
client.start()
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

data = {}

help_messages = ['/start - start online monitoring ',
         '/stop - stop online monitoring ',
         '/help - show help ',
         '/add - add user to monitoring list "/add +79991234567 UserName"',
         '/list - show added users',
         '/clear - clear user list',
         '/remove - remove user from list with position in list (to show use /list command)"/remove 1"',
         '/setdelay - set delay between user check in seconds',
         '/logs - display command log',
         '/clearlogs - clear the command log file',
         '/cleardata - reset configuration',
         '/disconnect - disconnect bot',
         '/getall - status']


print('running')
class Contact:
    online = None
    last_offline = None
    last_online = None
    id = ''
    name = ''

    def __init__(self, id, name):
        self.id = id
        self.name = name
    def __str__(self):
        return f'{self.name}: {self.id}'

@bot.on(events.NewMessage(pattern='^/logs$'))
async def logs(event):
    """Send a message when the command /start is issued."""
    str = ''
    with open('spy_log.txt', 'r') as file:
        str = file.read()
    await event.respond(str)

@bot.on(events.NewMessage(pattern='/clearlogs$'))
async def clearLogs(event):
    """Send a message when the command /start is issued."""
    open('spy_log.txt', 'w').close()
    await event.respond('logs has been deleted')

@bot.on(events.NewMessage(pattern='^/clear$'))
async def clear(event):
    """Send a message when the command /start is issued."""
    message = event.message
    id = message.chat_id
    data[id] = {}
    await event.respond('User list has been cleared')

@bot.on(events.NewMessage(pattern='^/help$'))
async def help(event):
    await event.respond('\n'.join(help_messages))

@bot.on(events.NewMessage())
async def log(event):
    """Send a message when the command /start is issued."""
    message = event.message
    id = message.chat_id
    str = f'{datetime.now().strftime(DATETIME_FORMAT)}: [{id}]: {message.message}'
    printToFile(str)
    #await bot.send_message(entity=entity,message=str)
    #await event.respond('cleared')

@bot.on(events.NewMessage(pattern='^/stop$'))
async def stop(event):
    """Send a message when the command /start is issued."""
    message = event.message
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]
    user_data['is_running'] = False
    await event.respond('Monitoring has been stopped')

@bot.on(events.NewMessage(pattern='^/cleardata$'))
async def clearData(event):
    data.clear()
    await event.respond('Data has been cleared')

@bot.on(events.NewMessage(pattern='^/start$'))
async def start(event):
    message = event.message
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]
    
    # Проверяем, существует ли ключ is_running
    if 'is_running' in user_data and user_data['is_running']:
        await event.respond('Spy is already started')
        return

    if 'contacts' not in user_data:
        user_data['contacts'] = []

    contacts = user_data['contacts']

    if(len(contacts) < 1):
        await event.respond('No contacts added')
        return
    await event.respond('Monitoring has been started')

    counter = 0
    user_data['is_running'] = True

    while True:
        # Получаем актуальные данные пользователя
        user_data = data[id]
        
        # Проверяем, существует ли ключ is_running
        if 'is_running' not in user_data or not user_data['is_running'] or len(contacts) < 1:
            break;
        print(f'running {id}: {counter}')
        counter+=1
        for contact in contacts:
            print(contact)
            try:
                account = await client.get_entity(contact.id)

                if isinstance(account.status, UserStatusOnline):
                    if contact.online != True:
                        contact.online = True
                        contact.last_offline = datetime.now()
                        was_offline='unknown offline time'
                        if contact.last_online is not None:
                            # Преобразуем в timezone-naive объекты перед вычитанием
                            last_offline = contact.last_offline.replace(tzinfo=None)
                            last_online = contact.last_online
                            if hasattr(last_online, 'tzinfo') and last_online.tzinfo is not None:
                                last_online = last_online.replace(tzinfo=None)
                            was_offline = get_interval(last_offline - last_online)
                        await event.respond(f'{was_offline}: {contact.name} went online.')
                elif isinstance(account.status, UserStatusOffline):
                    if contact.online == True:
                        contact.online = False
                        last_time_online = utc2localtime(account.status.was_online)
                        if (last_time_online is None):
                            last_time_online = datetime.now()
                        contact.last_online = last_time_online

                        was_online='unknown online time'
                        if contact.last_offline is not None:
                            # Преобразуем в timezone-naive объекты перед вычитанием
                            last_online = contact.last_online
                            if hasattr(last_online, 'tzinfo') and last_online.tzinfo is not None:
                                last_online = last_online.replace(tzinfo=None)
                            last_offline = contact.last_offline
                            if hasattr(last_offline, 'tzinfo') and last_offline.tzinfo is not None:
                                last_offline = last_offline.replace(tzinfo=None)
                            was_online = get_interval(last_online - last_offline)

                        await event.respond(f'{was_online} {contact.name} went offline.')
                    contact.last_offline = None
                else:
                    if contact.online == True:
                        contact.online = False
                        contact.last_online = datetime.now()

                        was_online='unknown online time'
                        if contact.last_offline is not None:
                            # Преобразуем в timezone-naive объекты перед вычитанием
                            last_online = contact.last_online
                            if hasattr(last_online, 'tzinfo') and last_online.tzinfo is not None:
                                last_online = last_online.replace(tzinfo=None)
                            last_offline = contact.last_offline
                            if hasattr(last_offline, 'tzinfo') and last_offline.tzinfo is not None:
                                last_offline = last_offline.replace(tzinfo=None)
                            was_online = get_interval(last_online - last_offline)

                        await event.respond(f'{was_online}: {contact.name} went offline.')
                        contact.last_offline = None
            except Exception as e:
                print(f"Error getting status for {contact.name}: {e}")
                await event.respond(f"Error getting status for {contact.name}: {e}")
        delay = 5
        if('delay' in user_data):
            delay = user_data['delay']
        sleep(delay)
    user_data['is_running'] = False
    await event.respond(f'Spy gonna zzzzzz...')

@bot.on(events.NewMessage(pattern='^/add'))
async def add(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    phone = person_info[1]
    name = person_info[2]
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']
    contact = Contact(phone, name)
    contacts.append(contact)
    await event.respond(f'{name}: {phone} has been added')


@bot.on(events.NewMessage(pattern='^/remove'))
async def remove(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    index = int(person_info[1])
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']

    if(len(contacts) > index):
        del contacts[index]
        await event.respond(f'User №{index} has been deleted')
    else:
        await event.respond('Incorrect index')

@bot.on(events.NewMessage(pattern='^/setdelay'))
async def setDelay(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    index = int(person_info[1])
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    print(index)
    if(index >= 0):
        user_data['delay'] = index
        await event.respond(f'Delay has been updated to {index}')
    else:
        await event.respond('Incorrect delay')

@bot.on(events.NewMessage(pattern='^/disconnect$'))
async def disconnect(event):
    await event.respond('Bot gonna disconnect')
    await bot.disconnect()

@bot.on(events.NewMessage(pattern='/list'))
async def list(event):
    message = event.message
    id = message.chat_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']
    response = 'List is empty'
    if(len(contacts)):
        response = 'User list: \n'+'\n'.join([str(x) for x in contacts])
    await event.respond(response)

@bot.on(events.NewMessage(pattern='/getall'))
async def getAll(event):
    response = ''
    for key, value in data.items():
        response += f'{key}:\n'
        for j, i in value.items():
            if (isinstance(i, collections.abc.Sequence)):
                response += f'{j}: ' + '\n'.join([str(x) for x in i]) + '\n'
            else:
                response += f'{j}: {i}\n'
        response += '\n'
    await event.respond(response)

def main():
    """Start the bot."""
    bot.run_until_disconnected()


def utc2localtime(utc):
    if utc is None:
        return None
    # Преобразуем UTC в локальное время
    from datetime import timezone
    # Получаем локальное время с учетом часового пояса
    local_time = utc.replace(tzinfo=timezone.utc).astimezone()
    # Возвращаем naive datetime объект
    return local_time.replace(tzinfo=None)

def printToFile(str):
    file_name = 'spy_log.txt'
    with open(file_name,'a') as f:
        print(str)
        f.write(str + '\n')

def get_interval(date):
    """
    Преобразует timedelta объект в строку формата 'Xh:Ym:Zs'
    """
    if not isinstance(date, timedelta):
        return "unknown time"
        
    d = divmod(date.total_seconds(), 86400)  # days
    h = divmod(d[1], 3600)  # hours
    m = divmod(h[1], 60)  # minutes
    s = m[1]  # seconds

    return '%dh:%dm:%ds' % (h[0], m[0], s)

if __name__ == '__main__':
    main()
