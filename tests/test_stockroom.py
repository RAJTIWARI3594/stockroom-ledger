import unittest,tempfile
from stockroom import connect,move,stock,history
class Tests(unittest.TestCase):
 def setUp(self):self.c=connect(':memory:');self.addCleanup(self.c.close)
 def receive(self):move(self.c,'receive','BOOK',10,'R1',target='MAIN')
 def test_receive(self):self.receive();self.assertEqual(stock(self.c)[0]['quantity'],10)
 def test_issue(self):self.receive();move(self.c,'issue','BOOK',3,'I1',source='MAIN');self.assertEqual(stock(self.c)[0]['quantity'],7)
 def test_transfer(self):
  self.receive();move(self.c,'transfer','BOOK',4,'T1',source='MAIN',target='COUNTER');self.assertEqual(sum(r['quantity'] for r in stock(self.c)),10);self.assertEqual(len(history(self.c)),2)
 def test_shortage_rollback(self):
  self.receive()
  with self.assertRaises(ValueError):move(self.c,'transfer','BOOK',11,'T1',source='MAIN',target='B')
  self.assertEqual(stock(self.c)[0]['quantity'],10);self.assertEqual(len(history(self.c)),1)
 def test_duplicate(self):
  self.receive()
  with self.assertRaises(ValueError):move(self.c,'receive','BOOK',10,'R1',target='MAIN')
  self.assertEqual(stock(self.c)[0]['quantity'],10)
 def test_zero(self):
  with self.assertRaises(ValueError):move(self.c,'receive','BOOK',0,'R',target='MAIN')
 def test_bool(self):
  with self.assertRaises(ValueError):move(self.c,'receive','BOOK',True,'R',target='MAIN')
 def test_injection(self):
  with self.assertRaises(ValueError):move(self.c,'receive',"X'; DROP TABLE stock",1,'R',target='MAIN')
 def test_same_location(self):
  with self.assertRaises(ValueError):move(self.c,'transfer','B',1,'R',source='A',target='A')
 def test_persistence(self):
  with tempfile.TemporaryDirectory() as d:
   c=connect(d+'/d.db');move(c,'receive','B',8,'R',target='A');c.close();c=connect(d+'/d.db');self.assertEqual(stock(c)[0]['quantity'],8);c.close()
 def test_empty(self):self.assertEqual(stock(self.c),[]);self.assertEqual(history(self.c),[])
 def test_unknown(self):
  with self.assertRaises(ValueError):move(self.c,'bad','B',1,'R')
if __name__=='__main__':unittest.main()
