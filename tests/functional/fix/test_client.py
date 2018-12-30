#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Functional tests for `copra.fixt.Client` class.
"""

import asyncio
from decimal import Decimal
import os.path
import random
import sys

from asynctest import TestCase

from copra.fix.client import Client, SANDBOX_URL

if not os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    print("\n** .env file not found. **\n")
    sys.exit()

from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PASSPHRASE = os.getenv('PASSPHRASE')

class TestFix(TestCase):
    """Tests for copra.fix.Client"""
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    async def test_connect_close(self):
        client = Client(self.loop, KEY, SECRET, PASSPHRASE, url=SANDBOX_URL)
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())
        
        await client.connect()
        
        self.assertTrue(client.connected.is_set())
        self.assertFalse(client.disconnected.is_set())
        self.assertTrue(client.logged_in.is_set())
        self.assertFalse(client.logged_out.is_set())
        
        await asyncio.sleep(0)
        
        self.assertTrue(client.keep_alive_task)
        
        await client.close()
        
        self.assertFalse(client.connected.is_set())
        self.assertTrue(client.disconnected.is_set())
        self.assertFalse(client.logged_in.is_set())
        self.assertTrue(client.logged_out.is_set())        
        
        await asyncio.sleep(0)
        
        self.assertIsNone(client.keep_alive_task)
        
    
    async def test_limit_order(self):
        
        client = Client(self.loop, KEY, SECRET, PASSPHRASE, url=SANDBOX_URL)
        await client.connect()
        
        # Assumes cancel works
        for side, base_price in (('buy', 1), ('sell', 10000)):
            
            # default time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            
            order = await client.limit_order(side, 'BTC-USD', size, price)
            print(order, '\n')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, side)
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal(str(size)))
            self.assertEqual(order.price, Decimal(str(price)))
            self.assertEqual(order.time_in_force, 'GTC')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            
            await client.cancel(order.id)
            
            self.assertTrue(order.done.is_set())
            
            # explicit time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            order = await client.limit_order(side, 'BTC-USD', size, price,
                                                            time_in_force='GTC')
            print(order, '\n')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, side)
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal(str(size)))
            self.assertEqual(order.price, Decimal(str(price)))
            self.assertEqual(order.time_in_force, 'GTC')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            
            await client.cancel(order.id)
            
            self.assertTrue(order.done.is_set())
            
            # IOC time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            order = await client.limit_order(side, 'BTC-USD', size, price,
                                                            time_in_force='IOC')
            print(order, '\n')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, side)
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal(str(size)))
            self.assertEqual(order.price, Decimal(str(price)))
            self.assertEqual(order.time_in_force, 'IOC')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            
            await asyncio.sleep(1)

            if not order.done.is_set():
                await client.cancel(order.id)
            
            self.assertTrue(order.done.is_set())
                       
            # FOK time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            order = await client.limit_order(side, 'BTC-USD', size, price,
                                                            time_in_force='FOK')
            print(order, '\n')
            self.assertTrue(order.id)
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, side)
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal(str(size)))
            self.assertEqual(order.price, Decimal(str(price)))
            self.assertEqual(order.time_in_force, 'FOK')
            self.assertTrue(order.received.is_set())

            await asyncio.sleep(1)

            if not order.done.is_set():
                await client.cancel(order.id)
            
            self.assertTrue(order.done.is_set())
            
            # PO time_in_force
            price = base_price + (random.randint(1, 9) / 10)
            size = random.randint(1, 10) / 1000
            order = await client.limit_order(side, 'BTC-USD', size, price,
                                                            time_in_force='PO')
            print(order, '\n')
            self.assertTrue(order.id)
            self.assertEqual(order.status, 'new')
            self.assertEqual(order.type, 'limit')
            self.assertEqual(order.side, side)
            self.assertEqual(order.product_id, 'BTC-USD')
            self.assertEqual(order.size, Decimal(str(size)))
            self.assertEqual(order.price, Decimal(str(price)))
            self.assertEqual(order.time_in_force, 'PO')
            self.assertTrue(order.received.is_set())
            self.assertFalse(order.done.is_set())
            
            await client.cancel(order.id)
            
            self.assertTrue(order.done.is_set())
            
        # stop loss
        order = await client.limit_order('sell', 'BTC-USD', .001, 2, stop_price=2.5)
        print(order)
        self.assertTrue(order.id)
        self.assertEqual(order.status, 'stopped')
        self.assertEqual(order.type, 'stop limit')
        self.assertEqual(order.side, 'sell')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.001'))
        self.assertEqual(order.price, Decimal('2'))
        self.assertEqual(order.stop_price, Decimal('2.5'))
        self.assertEqual(order.time_in_force, 'GTC')
        self.assertTrue(order.received.is_set())
        self.assertFalse(order.done.is_set())           
        
        await client.cancel(order.id)
            
        self.assertTrue(order.done.is_set())
        
        # stop entry
        order = await client.limit_order('buy', 'BTC-USD', .001, 9000, stop_price=8550)
        print(order)
        self.assertTrue(order.id)
        self.assertEqual(order.status, 'stopped')
        self.assertEqual(order.type, 'stop limit')
        self.assertEqual(order.side, 'buy')
        self.assertEqual(order.product_id, 'BTC-USD')
        self.assertEqual(order.size, Decimal('.001'))
        self.assertEqual(order.price, Decimal('9000'))
        self.assertEqual(order.stop_price, Decimal('8550'))
        self.assertEqual(order.time_in_force, 'GTC')
        self.assertTrue(order.received.is_set())
        self.assertFalse(order.done.is_set())           
        
        await client.cancel(order.id)
            
        self.assertTrue(order.done.is_set())
        
        await client.close()
        

        
        # #stop entry
        # order = await self.auth_client.limit_order('buy', 'BTC-USD', 9000, .001,
        #                                           stop='entry', stop_price=9550)
        
        # try:
        #     await self.auth_client.cancel(order['id'])
        # except APIRequestError:
        #     pass
        
        # keys = {'created_at', 'executed_value', 'fill_fees', 'filled_size', 
        #         'id', 'post_only', 'price', 'product_id', 'settled', 'side', 
        #         'size', 'status', 'stp', 'time_in_force', 'type', 'stop',
        #         'stop_price'}
                
        # self.assertEqual(order.keys(), keys)
        # self.assertEqual(float(order['price']), 9000)
        # self.assertEqual(float(order['size']), .001)
        # self.assertEqual(order['product_id'], 'BTC-USD')
        # self.assertEqual(order['side'], 'buy')
        # self.assertEqual(order['stp'], 'dc')
        # self.assertEqual(order['type'], 'limit')
        # self.assertEqual(order['time_in_force'], 'GTC')
        # self.assertEqual(order['stop'], 'entry')
        # self.assertEqual(float(order['stop_price']), 9550)
                
