#!/usr/bin/env python3.9
import asyncio
import mytelegram
from mytelegram import MyTelegram
from myguessit import MyGuessit


class MyChannel:
    def __init__(self):
        """
         Estrae ogni singolo file dividendolo dalla locandine
        """
        self.telegram = MyTelegram()
        self.media = None

    async def connect(self):
        """
        :return: Telegram login e collegamento al canale
        """
        await self.telegram.login()
        print(f"-> [INVITE LINK] {mytelegram.INVITE_LINK}")
        print(f"-> [CHANNEL ID]  {self.telegram.channel.channel_id}")
        print(f"-> [CONNECT OBJ] {self.telegram.takeout}")

    async def struttura(self) -> list:
        """
        :return: ritorna un elenco di oggetti MyMedia pronti per il download
        """
        media_list = []
        async for message in self.telegram.takeout.iter_messages(self.telegram.channel.channel_id,
                                                                 limit=None, reverse=True, wait_time=1):
            # Si accerta che sia un messaggio
            if message:
                # Eslcude gli sticker
                if not message.sticker:
                    # Si accerta che esista un documento di media
                    if message.media:
                        if hasattr(message.media, 'document'):
                            # esclude messaggi senza file name(pubblcità)
                            if not message.file.name:
                                continue
                            # Memorizza per ogni documento media filename e ID del messaggio
                            file_name = message.file.name
                            print(file_name, message.id)
                            self.media.filemedia = message.file.name, message.id
                        else:
                            # Se media è già stato istanziato abbiamo raggiunto qui ora la prossima locandina
                            # lo salva quindi nella lista media_list. Al termine passa ad un'altra locandina.
                            if self.media:
                                media_list.append(self.media)
                            # Ottiene il testo della Locandina
                            poster = message.message
                            # Filtra il più possibile il testo poi lo passa a guessit e ottiene un titolo
                            guess = MyGuessit(poster)
                            self.media = mytelegram.MyMedia()
                            print(f"*{guess}")
                            self.media.title = guess
        return media_list


async def main():
    anime = MyChannel()
    await anime.connect()
    media_list = await anime.struttura()
    for media in media_list:
        print(media.title)
        await anime.telegram.downloader(media)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        task_main = loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pass
