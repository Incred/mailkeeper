import json
import asyncio
import aio_pika
import argparse
import sys

import config

parser = argparse.ArgumentParser(description='Process bounced emails.')
parser.add_argument('--recipient', dest='recipient')
parser.add_argument('--sender', dest='sender')

args = parser.parse_args()


async def main(loop):
    connection = await aio_pika.connect_robust(
        host=config.RABBITMQ_HOST, loop=loop
    )

    async with connection:
        routing_key = config.QUEUE_NAME
        channel = await connection.channel()

        msg_dict = {
            'sender': args.sender,
            'recipient': args.recipient,
            'msg': sys.stdin.read()
        }

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(msg_dict).encode()
            ),
            routing_key=routing_key,
        )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
