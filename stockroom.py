import argparse,csv,json,re,sqlite3,sys
from datetime import datetime,timezone
TOKEN=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')
def token(x):
 if not isinstance(x,str) or not TOKEN.fullmatch(x):raise ValueError('Use 1–64 letters/digits/._-')
 return x

def connect(path):
 c=sqlite3.connect(path,timeout=10);c.execute('PRAGMA foreign_keys=ON');c.executescript("""CREATE TABLE IF NOT EXISTS stock(sku TEXT,location TEXT,quantity INTEGER NOT NULL CHECK(quantity>=0),PRIMARY KEY(sku,location));CREATE TABLE IF NOT EXISTS movement(id INTEGER PRIMARY KEY,ref TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,sku TEXT NOT NULL,source TEXT,target TEXT,quantity INTEGER NOT NULL CHECK(quantity>0),at TEXT NOT NULL);""");return c

def move(c,kind,sku,qty,ref,source=None,target=None):
 token(sku);token(ref)
 if type(qty)!=int or not 1<=qty<=1000000:raise ValueError('Quantity 1–1000000 required')
 if kind not in ('receive','issue','transfer'):raise ValueError('Unknown operation')
 if kind=='receive' and source is not None or kind=='issue' and target is not None:raise ValueError('Unexpected source or target')
 if kind in ('issue','transfer'):token(source)
 if kind in ('receive','transfer'):token(target)
 if kind=='transfer' and source==target:raise ValueError('Locations must differ')
 try:
  c.execute('BEGIN IMMEDIATE')
  if c.execute('SELECT 1 FROM movement WHERE ref=?',(ref,)).fetchone():raise ValueError('Reference already used')
  if source:
   cur=c.execute('UPDATE stock SET quantity=quantity-? WHERE sku=? AND location=? AND quantity>=?',(qty,sku,source,qty))
   if cur.rowcount!=1:raise ValueError('Insufficient stock')
  if target:c.execute('INSERT INTO stock VALUES(?,?,?) ON CONFLICT(sku,location) DO UPDATE SET quantity=quantity+excluded.quantity',(sku,target,qty))
  c.execute('INSERT INTO movement(ref,kind,sku,source,target,quantity,at) VALUES(?,?,?,?,?,?,?)',(ref,kind,sku,source,target,qty,datetime.now(timezone.utc).isoformat()));c.commit()
 except Exception:c.rollback();raise

def stock(c):return [dict(zip(('sku','location','quantity'),r)) for r in c.execute('SELECT sku,location,quantity FROM stock ORDER BY sku,location')]
def history(c):
 cur=c.execute('SELECT ref,kind,sku,source,target,quantity,at FROM movement ORDER BY id');return [dict(zip([d[0] for d in cur.description],r)) for r in cur]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--db',required=True);sp=ap.add_subparsers(dest='action',required=True)
 for kind in ('receive','issue','transfer'):
  p=sp.add_parser(kind);p.add_argument('sku');p.add_argument('location')
  if kind=='transfer':p.add_argument('target')
  p.add_argument('quantity',type=int);p.add_argument('--ref',required=True)
 for kind in ('stock','history'):sp.add_parser(kind)
 sp.add_parser('export').add_argument('output');a=ap.parse_args()
 try:
  with connect(a.db) as c:
   if a.action in ('receive','issue','transfer'):
    move(c,a.action,a.sku,a.quantity,a.ref,source=a.location if a.action!='receive' else None,target=a.target if a.action=='transfer' else a.location if a.action=='receive' else None);print('Movement committed')
   elif a.action=='export':
    with open(a.output,'x',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=['sku','location','quantity']);w.writeheader();w.writerows(stock(c))
    print('Exported stock')
   else:print(json.dumps(stock(c) if a.action=='stock' else history(c),indent=2))
 except (ValueError,OSError,sqlite3.Error) as e:print(f'Error: {e}',file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
