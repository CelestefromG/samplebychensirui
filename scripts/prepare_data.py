import openpyxl,json,collections,datetime,hashlib,pathlib,sys
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('Skincare_Product_Reviews_Dataset-rGDXr9.xlsx')
w=openpyxl.load_workbook(path,read_only=True,data_only=True)
rows=list(w.active.values);headers=rows.pop(0); groups={}; invalid=0
for i,row in enumerate(rows,2):
 product,category,rating,date,text,decision=row
 text=str(text or '').strip(); product=str(product or '').strip(); key=(product,text)
 ds=date.isoformat()[:10] if isinstance(date,datetime.datetime) else str(date or '')
 if not isinstance(date,datetime.datetime) or not 2000<=date.year<=2026: invalid+=1
 if key not in groups: groups[key]={'id':'R'+str(len(groups)+1).zfill(4),'product':product,'category':category,'text':text,'ratings':[],'dates':[],'annotations':[],'sourceRows':[]}
 g=groups[key];g['ratings'].append(rating);g['dates'].append(ds);g['sourceRows'].append(i)
 for aspect,sentiment in json.loads(decision).items():
  a={'aspect':aspect,'sentiment':sentiment}
  if a not in g['annotations']:g['annotations'].append(a)
records=list(groups.values())
for g in records:
 g['ratings']=list(dict.fromkeys(g['ratings']));g['dates']=list(dict.fromkeys(g['dates']))
meta={'file':path.name,'sheet':w.active.title,'rawRows':len(rows),'groupedReviews':len(records),'invalidDateRows':invalid,'products':len(set(g['product'] for g in records)),'annotationCount':sum(len(g['annotations']) for g in records),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':'https://data.mendeley.com/datasets/6vmrcypy7c/2','doi':'10.17632/6vmrcypy7c.2','license':'CC BY 4.0','authors':'Mangsura Kabir Oni; Khandoker Nosiba Arifin; Iffat Ara Sanzida; Sayma Akter Rupa; Md Musfique Anwar','note':'按产品名与去除首尾空白的原文合并；相同方面与情绪去重。合并组不是可验证的独立消费者。原始日期与评分保留，多值不强行统一。'}
(pathlib.Path(__file__).resolve().parents[1]/'docs/data.json').write_text(json.dumps({'meta':meta,'reviews':records},ensure_ascii=False),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False))
for a in ['texture','sensitivity','effectiveness','quality','suitability','satisfaction','others']:
 vals=[g for g in records if any(x['aspect']==a and x['sentiment']=='negative' for x in g['annotations'])]
 print(a,[(g['id'],g['text'][:160]) for g in vals[:2]])
