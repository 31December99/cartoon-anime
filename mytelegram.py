#!/usr/bin/env python3.9
import asyncio
import os

from telethon import TelegramClient, errors, types
from decouple import config
from telethon.errors import SessionPasswordNeededError
from datetime import datetime

API_ID = config('YOUR_API_ID')
API_HASH = config('YOUR_API_HASH')
PHONE = config('YOUR_PHONE_NUMBER')
SESSION = config('SESSION_NAME')
INVITE_LINK = config('INVITE_LINK')


class MyMedia:

    def __init__(self):
        self.__title = None
        self.__msgid = None
        self.__filemedia = []

    @property
    def title(self):
        return self.__title

    @property
    def filemedia(self):
        return self.__filemedia

    @title.setter
    def title(self, value):
        self.__title = value

    @filemedia.setter
    def filemedia(self, value):
        self.__filemedia.append(value)

    def saved(self) -> bool:
        return True if (self.__title and
                        self.__msgid and
                        self.__filemedia) else False

    def __str__(self):
        print(self.__title, self.__msgid, self.__filemedia)


class MyTelegram:
    """
    Classe per creare una connessione verso telegram

    """
    def __init__(self):
        self.__takeout = None
        self.__channel = None
        self.__client = None

    async def connect(self):
        """
        Istanzia una nuova connessione con telegram
        """
        self.__client = TelegramClient(session=SESSION, api_id=API_ID, api_hash=API_HASH, retry_delay=10,
                                       flood_sleep_threshold=240)
        await self.__client.connect()

    async def disconnect(self):
        """
        Si disconnette.
        """
        if self.__client:
            await self.__client.disconnect()

    async def send_message(self, to_username, message):
        """
        :param to_username: Username dell'utente
        :param message:  testo del messaggio
        :return: True = inviato
        """
        if self.__client:
            try:
                await self.__client.send_message(to_username, message)
                return True
            except Exception as e:
                print(f"Errore nell'invio del messaggio: {e}")
        return False

    async def get_chat_id(self, username):
        """
        :param username: Username dell'utente
        :return:  ritorna l'ID dell'username
        """
        if self.__client:
            try:
                entity = await self.__client.get_entity(username)
                if isinstance(entity, types.User):
                    return entity.id
            except Exception as e:
                print(f"Errore nell'ottenere l'ID della chat: {e}")
        return None

    async def delete_file(self, filename):
        os.remove(filename)

    async def login(self):
        """
        Fa il login come userbot.
        Richiede autorizzazione se assente.
        Ottiene l'ID del canale Anime Cartoon.
        Avverte se manca l'autorizzazione.
        """
        await self.connect()
        if not await self.__client.is_user_authorized():
            print("Richiesta di autorizzazione...")
            await self.__client.send_code_request(PHONE)
            try:
                await self.__client.sign_in(phone=PHONE, code=int(input('Enter code: ')))
            except SessionPasswordNeededError:
                password = input("Inserisci la password del tuo account Telegram: ")
                await self.__client.sign_in(password=password)
        try:
            async with self.__client.takeout(finalize=False) as conn:
                self.__channel = await conn.get_input_entity(INVITE_LINK)
                self.__takeout = conn
                print(f"Connesso...")
        except errors.TakeoutInitDelayError:
            print("step1 > Confermare autorizzazione in canale telegram service notifications (+42777)")
            print("step2 > Riavviare solo dopo aver confermato.")
        except errors.InviteHashExpiredError as err:
            print("Indirizzo del canale non valido !", err)

    async def worker(self, queue):
        while True:
            queue_item = await queue.get()
            msgbody, percorso, title = queue_item[:3]  # Estrai il messaggio e il percorso + nome del file
            current_time = datetime.now().strftime('%H:%M')
            if msgbody is not None:
                try:
                    print(f"[{current_time}] Download -> [{title}]")
                    await self.takeout.download_media(msgbody, percorso)
                except errors.FileReferenceExpiredError:
                    print(f"[{current_time}] §Expired§ => {title} ")
                    await self.delete_file(title)
                except errors.TimeoutError:
                    print(f"[{current_time}] §Incompleto§ => {title} ")
                    await self.delete_file(title)
                else:
                    print(f"[{current_time}] Completato ! {title} ")
                finally:
                    # Chiudi e decrementa la coda di 1 con task_done()
                    queue.task_done()
            else:
                current_time = datetime.now().strftime('%H:%M')
                print(f"[{current_time}] Questo video non esiste più ! {percorso}")
                queue.task_done()

    async def downloader(self, media_list: MyMedia):
        # Se filemedia è vuoto ( non in lista mimetypes)
        if not media_list.filemedia:
            print("-> escluso dalla lista di mimetype_list")
            return
        # Prepara i workers
        queue = asyncio.Queue(1)
        workers = [asyncio.create_task(self.worker(queue)) for _ in range(3)]
        for filemedia, ids in media_list.filemedia:
            async for messg in self.takeout.iter_messages(self.channel.channel_id, wait_time=1, ids=ids):
                await queue.put((messg, ".", filemedia))
        await queue.join()
        # Cancello i workers
        for workers_attivi in workers:
            workers_attivi.cancel()
        # Pausa
        await asyncio.sleep(3)

    @property
    def takeout(self):
        return self.__takeout

    @property
    def channel(self):
        return self.__channel
