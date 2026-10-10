"""Explainable, conservative English clause-level lexicon baseline, no model API."""
import re,json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
# topic: label, creative parent, group, mention, positive cues, negative cues
RULES={
'redness':('泛红与红疹','sensitivity','肌肤反应',r'redness|red rash|rash|skin (?:became|turned|got) red',r'(?:reduc|calm|sooth|reliev|no |without |not caus|doesn.t caus).{0,25}(?:redness|rash)|redness.{0,20}(?:gone|better|reduc)',r'(?:gave|caus|develop|got|trigger|gave me).{0,25}(?:redness|rash)|(?:redness|rash).{0,20}(?:appear|worse)'),
'irritation':('刺痛与刺激','sensitivity','肌肤反应',r'irritat|burning|sting|allerg|itch|alergy|irrigation',r'(?:no |without |not |doesn.t |didn.t |never ).{0,16}(?:irritat|burn|sting|itch|allerg)|(?:sooth|calm).{0,20}(?:irritat|burn)',r'(?:caus|gave|provok|made|trigger|had|feel|felt).{0,30}(?:irritat|burn|sting|allerg|itch|irrigation)|(?:irritat|burning|itchy|allergy|allergic|alergy)'),
'acne':('冒痘与闭口','sensitivity','肌肤反应',r'break.?out|broke (?:me )?out|pimple|clog|acne.{0,25}(?:reduc|clear|worse|improv|heal)|(?:reduc|clear|treat|help|caus).{0,25}acne',r'(?:no |without |doesn.t |didn.t |never ).{0,14}(?:break.?out|broke|pimple|clog)|(?:reduc|clear|heal|help|prevent|control).{0,25}(?:acne|pimple|break.?out)|(?:acne|pimple).{0,25}(?:reduc|clear|gone|improv)',r'(?:caus|gave|got|trigger|made|started|new|develop).{0,25}(?:acne|pimple|break.?out)|broke (?:me )?out|clog.{0,12}pore|pimple.{0,20}appear'),
'hydration':('保湿与滋润','effectiveness','功效体验',r'hydrat|moisturi|moisture|nourish',r'(?:good|great|best|decent|nice|super|well|deep|really).{0,20}(?:hydrat|moisturi)|(?:hydrat|moisturi).{0,25}(?:well|good|great|enough|long)|(?:keeps?|makes?|leaves?).{0,40}(?:hydrated|moisturi)|very hydrat|so hydrat|super hydrat',r'(?:not|doesn.t|didn.t|no|poor|lack).{0,18}(?:hydrat|moisturi)|(?:hydrat|moisture).{0,20}(?:not enough|doesn.t last|didn.t last|insufficient)'),
'dryness':('干燥与紧绷','effectiveness','肌肤反应',r'(?:leav|left|made|make|feel|felt|became|become|cause).{0,25}(?:dry|tight)|drying|dried.{0,12}(?:skin|face)|dry finish|dry patches|flak',r'(?:not |doesn.t |didn.t |without |no ).{0,15}(?:dry|tight|flak)|(?:reduc|help|reliev).{0,18}(?:dry|flak)',r'(?:leav|left|made|make|feel|felt|cause).{0,25}(?:dry|tight)|drying|dried.{0,12}(?:skin|face)|dry finish|dry patches|flak'),
'greasy':('油腻与黏腻','texture','质地肤感',r'greas|sticky|stickiness|tacky|oiliness|(?:feels?|makes?|made|left|leaves?|became|extremely|too|very).{0,18}oily|oily.{0,10}(?:finish|feeling|texture)',r'non.?greasy|(?:not |no |without |doesn.t |didn.t |never ).{0,16}(?:greas|sticky|tacky|oily)|(?:control|reduc).{0,12}oiliness',r'greas|sticky|stickiness|tacky|(?:feel|make|made|left|leav|extremely|too|very).{0,18}oily'),
'absorption':('吸收速度','texture','质地肤感',r'absorb|absorp',r'(?:quick|fast|well|nicely|easily).{0,14}absorb|absorb.{0,20}(?:quick|fast|well|nicely|easily)',r'(?:not |doesn.t |didn.t |slow|poor).{0,12}absorb|absorb.{0,20}(?:slow|poor|not well)|takes.{0,15}(?:long|time).{0,15}absorb'),
'weight':('轻薄与厚重','texture','质地肤感',r'light.?weight|heavy|thick|light texture|light on|light cream',r'light.?weight|light texture|light on|(?:not|isn.t|without).{0,8}(?:heavy|thick)',r'(?:too|very|quite|a bit|feels?|felt).{0,10}(?:heavy|thick)|heavy.{0,12}(?:skin|face)|thick.{0,12}(?:texture|consistency)'),
'blend':('延展与推开','texture','质地肤感',r'blend|spread',r'(?:easy|easily|well|nicely|smoothly).{0,15}(?:blend|spread)|(?:blend|spread).{0,15}(?:easy|easily|well|nicely)',r'(?:hard|difficult|not|doesn.t|didn.t).{0,15}(?:blend|spread)|(?:blend|spread).{0,15}(?:hard|difficult|not well)'),
'whitecast':('泛白与白膜','texture','妆效表现',r'white.?cast|whitish|white layer|white film',r'(?:no |without |not |doesn.t |didn.t |never ).{0,22}(?:white.?cast|whitish|white layer|white film)',r'(?:leave|leaves|left|gives?|has|have|creates?).{0,20}(?:white.?cast|whitish|white layer|white film)|white.?cast.{0,10}(?:problem|visible)'),
'pilling':('搓泥与上妆','texture','妆效表现',r'\bpill(?:s|ing)?\b|patch.{0,14}(?:makeup|make up)|under makeup|under make.up|cakey',r'(?:no |not |doesn.t |didn.t |without ).{0,20}(?:pill|patch|cakey)|(?:well|good|great).{0,15}under make.?up',r'(?:caus|starts?|keeps?|makes?).{0,15}(?:pill|patch|cakey)|\bpilling\b'),
'fragrance':('香味与气味','satisfaction','感官与包装',r'fragrance|smell|scent|perfume',r'(?:love|like|nice|good|great|pleasant|mild|no |free).{0,15}(?:smell|scent|fragrance)|(?:smell|scent|fragrance).{0,20}(?:nice|good|great|pleasant)|fragrance.free',r'(?:bad|strong|acute|awful|hate|unpleasant|too much).{0,15}(?:smell|scent|fragrance)|(?:smell|scent|fragrance).{0,25}(?:bad|strong|headache|nause|not.{0,8}good)|(?:don.t|didn.t).{0,8}like.{0,15}(?:smell|scent|fragrance)'),
'brightening':('提亮与淡斑','effectiveness','功效体验',r'brighten|dark spots?|pigment|skin.{0,18}(?:bright|glow)|face.{0,18}(?:bright|glow)',r'(?:help|reduc|fade|lighten|clear).{0,25}(?:dark spot|pigment)|(?:skin|face).{0,20}(?:bright|glow)|brighten.{0,15}(?:well|effect)',r'(?:not|doesn.t|didn.t|no).{0,20}(?:brighten|dark spot|pigment)|dark spot.{0,20}(?:worse|no change)'),
'cleansing':('清洁与卸除','effectiveness','功效体验',r'cleanse|cleaning|cleans\b|remov.{0,20}(?:dirt|makeup|make.up|oil)',r'(?:good|great|best|gentle).{0,12}cleanse|clean(?:s|ing).{0,20}(?:well|good|deep)|remov.{0,20}(?:dirt|makeup|make.up|oil)',r'(?:not|doesn.t|didn.t|poor).{0,15}(?:clean|remov)|(?:cleanse|cleaning).{0,15}(?:bad|poor|ineffective)'),
'packaging':('包装与容器','quality','感官与包装',r'packag|bottle|pump|container|leak|seal|tube',r'(?:good|great|nice|beautiful|excellent|love|appreciate|perfect).{0,20}(?:packag|bottle|container)|(?:packag|bottle|container).{0,20}(?:good|great|nice|beautiful|perfect|wow)',r'(?:poor|bad|broken|damaged|faulty).{0,20}(?:packag|bottle|pump|container)|(?:packag|bottle|pump|container).{0,35}(?:broke|fractur|leak|didn.t match|doesn.t work|damag)|leak|broken seal'),
'price':('价格与性价比','satisfaction','购买体验',r'price|budget|expensive|afford|money|cheap|cost|worth',r'budget.friend|afford|reasonable.{0,8}price|worth.{0,10}(?:money|price|it)|value for money|(?:good|best|great).{0,10}price|cheap',r'not.{0,8}(?:budget|worth|afford)|expensive|overpriced|waste.{0,12}money|cheaper price|high.{0,10}price'),
'visible':('效果明显与无变化','effectiveness','功效体验',r'(?:see|saw|seen|notice|visible|significant).{0,20}(?:result|change|difference|effect)|(?:no|not any).{0,12}(?:result|change|difference|effect)|(?:doesn.t|didn.t|not).{0,10}work|works? (?:well|great|wonder|amazing)|effective|good result',r'(?:see|saw|seen|notice|visible|significant).{0,20}(?:result|change|difference|effect)|works? (?:well|great|wonder|amazing)|(?:very |really |so )effective|good result',r'(?:no|not any).{0,12}(?:result|change|difference|effect)|(?:doesn.t|didn.t|not).{0,10}work|(?:not|in)effective|(?:didn.t|couldn.t|can.t).{0,18}(?:see|notice|provide).{0,45}(?:result|change|difference|effect|improvement)'),
'authenticity':('正品疑虑','quality','购买体验',r'authentic|original|orginal|fake|counterfeit',r'(?:authentic|original|orginal)',r'fake|counterfeit|not.{0,12}(?:original|authentic)|didn.t receive.{0,12}original')}

def norm(s):
 s=s.lower().replace('’',"'").replace('‘',"'")
 for a,b in [('did not',"didn't"),('does not',"doesn't"),('do not',"don't"),('could not',"couldn't"),('cannot',"can't")]:s=s.replace(a,b)
 return s
def has(p,s):return bool(re.search(p,s,re.I))
NEG=r'\b(?:not|no|never|don.t|doesn.t|didn.t|isn.t|wasn.t|can.t|couldn.t|without)\b'
def polarity(key,text):
 _,_,_,mention,pos,neg=RULES[key];p=has(pos,text);n=has(neg,text)
 # Positive negations such as 'no irritation' override the adverse word they negate.
 negated_adverse=key in ['redness','irritation','acne','dryness','greasy','weight','whitecast','pilling'] and p and has(NEG,text)
 if negated_adverse:n=False
 # Negated praise belongs to the negative side ('does not absorb well', 'not good packaging').
 if key not in ['redness','irritation','acne','dryness','greasy','weight','whitecast','pilling'] and has(NEG,text) and n:p=False
 if key=='hydration' and has(r'moisturi[sz](?:ed|es) (?:my|the|your) skin|hydrates? (?:my|the|your) skin',text) and not has(NEG,text):p=True
 if key=='authenticity' and n:p=False
 if key=='price' and n and has(r'not|waste|cheaper price',text):p=False
 if p and n:return 'mixed'
 return 'positive' if p else 'negative' if n else 'uncertain'
def overall(text,annotations):
 t=norm(text)
 pos=any(a['sentiment'] in ['positive','mixed'] for a in annotations)
 neg=any(a['sentiment'] in ['negative','mixed'] for a in annotations)
 clauses=re.split(r'[.!?;\n]+|\bbut\b|\bhowever\b',t)
 for c in clauses:
  praise=has(r'\b(good|great|best|love|excellent|amazing|perfect|satisfied|recommend|nice|favorite|favourite|awesome)\b',c)
  adverse=has(r'\b(bad|worst|hate|disappointed|disappointing|useless|waste|terrible|horrible)\b',c)
  if praise and has(NEG+r'.{0,18}\b(good|great|best|love|satisfied|recommend|nice)\b',c):neg=True
  elif praise:pos=True
  if adverse and not has(NEG+r'.{0,12}(bad|disappointed)',c):neg=True
 return 'mixed' if pos and neg else 'positive' if pos else 'negative' if neg else 'uncertain'

def annotate(text):
 # Split contrast clauses so positive hydration is not attached to a subsequent greasy complaint.
 chunks=[c.strip(' ,') for c in re.split(r'(?<=[.!?;])\s+|\b(?:but|however|although|yet)\b|,\s*(?=(?:it|this|the|my|and|also|does|not)\b)',text,flags=re.I) if c.strip(' ,')]
 out=[]
 for key,rule in RULES.items():
  found=[]
  for c in chunks:
   t=norm(c)
   if has(rule[3],t):found.append({'quote':c,'sentiment':polarity(key,t)})
  if not found:continue
  sentiments={a['sentiment'] for a in found}
  tone='mixed' if 'mixed' in sentiments or {'positive','negative'}<=sentiments else 'positive' if 'positive' in sentiments else 'negative' if 'negative' in sentiments else 'uncertain'
  out.append({'aspect':key,'sentiment':tone,'evidence':found,'method':'rules-v2'})
 return out
if __name__=='__main__':
 p=ROOT/'docs/data.json';data=json.loads(p.read_text())
 for r in data['reviews']:
  if 'sourceAnnotations' not in r:r['sourceAnnotations']=r['annotations']
  r['annotations']=annotate(r['text']);r['sentiment']=overall(r['text'],r['annotations'])
 data['meta']['analysis']={'method':'英文分句词典与否定规则 v2；未调用情绪模型。','topics':len(RULES),'coveredReviews':sum(bool(r['annotations']) for r in data['reviews']),'labels':sum(len(r['annotations']) for r in data['reviews']),'sentiments':dict(collections.Counter(r['sentiment'] for r in data['reviews']))}
 p.write_text(json.dumps(data,ensure_ascii=False))
 taxonomy={k:{'label':v[0],'parent':v[1],'group':v[2]} for k,v in RULES.items()}
 (ROOT/'docs/taxonomy.mjs').write_text('export const TOPICS = '+json.dumps(taxonomy,ensure_ascii=False)+';\n')
 print(json.dumps(data['meta']['analysis'],ensure_ascii=False))
 for k in RULES:
  vals=[r for r in data['reviews'] if any(a['aspect']==k for a in r['annotations'])]
  print(k,len(vals),dict(collections.Counter(a['sentiment'] for r in vals for a in r['annotations'] if a['aspect']==k)))
