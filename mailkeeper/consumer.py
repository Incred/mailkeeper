import json
import asyncio
import aio_pika
from pytz import UTC
from datetime import datetime

import config
from handlers import MainHandler
from db import DB, Email


class Consumer:
    db = None
    connections = []

    async def store_message(self, data):
        email = Email(
            created=datetime.now(UTC),
            sender=data['from_email'],
            recipient=data['email'],
            body=data.get('html') or data.get('text'),
            raw_content=data['raw_content'],
            subject=data['subject'],
            inbound=data['event'] == 'inbound',
            bounced=data['event'] == 'bounced',
        )
        async with self.db.session() as session:
            session.add(email)

    async def process_message(self, message: aio_pika.IncomingMessage):
        # Inbound message handler which uses message.process context manager
        # with requeue=True flag, it means in case of exception the message
        # will be requeued
        async with message.process(requeue=True):
            msg = json.loads(message.body)
            handler = MainHandler(msg['sender'], msg['recipient'], msg['msg'])
            await handler.process()
            # TODO validate message
            if handler.data is not None:
                await self.store_message(handler.data)


    async def main(self, loop):
        connection = await aio_pika.connect_robust(
            host=config.RABBITMQ_HOST, loop=loop
        )
        self.db = DB(config.A_DB_URL)
        self.db.connect()
        channel = await connection.channel()
        # Maximum message count which will be processing at the same time.
        await channel.set_qos(prefetch_count=50)
        queue = await channel.declare_queue(config.QUEUE_NAME, durable=True)
        await queue.consume(self.process_message)
        self.connections.append(connection)

    async def close_connections(self):
        for connection in self.connections:
            await connection.close()


if __name__ == "__main__":
    consumer = Consumer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consumer.main(loop))
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(consumer.close_connections())
        loop.close()
