#!/usr/bin/env python3.9
import asyncio
import mytelegram
from mytelegram import MyTelegram
from myguessit import MyGuessit
from database import Database


class MyChannel:
    mime_type_list = [
        "video/x-matroska",  # .mkv .mk3d .mka .mks
        "video/mpeg",  # .mpg, .mpeg, .mp2, .mp3
        "video/x-mpeg",  #
        "video/mp4",  # .mp4, .m4a, .m4p, .m4b, .m4r .m4v
    ]

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
        media_raw = []
        async for message in self.telegram.takeout.iter_messages(self.telegram.channel.channel_id,
                                                                 limit=None, reverse=True, wait_time=1):
            # Si accerta che sia un messaggio
            if message:
                # Eslcude gli sticker
                if not message.sticker:
                    # Si accerta che esista un documento di media
                    if message.media:
                        if hasattr(message.media, 'document'):
                            if message.media.document.mime_type in self.mime_type_list:
                                # esclude messaggi senza file name(pubblcità)
                                if not message.file.name:
                                    continue
                                # Memorizza per ogni documento media filename e ID del messaggio
                                file_name = message.file.name
                                # print(file_name, message.id)
                                self.media.ids = message.id
                        else:
                            # Se media è già stato istanziato abbiamo raggiunto qui la prossima locandina
                            # Se filemedia non è empty ( filmedia accettato in base alla list mimetype_list)
                            # lo salva nella lista media_list. Al termine passa ad un'altra locandina.
                            if self.media:
                                if self.media.ids:
                                    media_raw.append(self.media)
                            # Ottiene il testo della Locandina
                            poster = message.message
                            # Filtra il testo quindi lo passa a guessit
                            guess = MyGuessit(poster)
                            self.media = mytelegram.MyMedia()
                            self.media.title = str(guess)
                            self.media.posterid = message.id
                            print(f"*{guess} {message.id}")

        media_list = [media for media in media_raw if media.ids]
        return media_list


async def main():
    anime = MyChannel()
    await anime.connect()
    database = Database("CartoonAnime.db")
    await database.connect()
    await database.create_table("cartoonanime")
    media_list = await anime.struttura()

    for media in media_list:
        print(media.title, media.posterid, media.ids)
        category = "Multi" if len(media.ids) > 1 else "Single"
        await database.insert_video("cartoonanime", media.title, media.posterid, category, media.ids)
    await database.db.commit()

    for media in media_list:
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
