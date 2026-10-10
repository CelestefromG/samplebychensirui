from annotate_reviews import annotate,overall
cases=[
 ('I have oily skin.',{},'uncertain'),
 ('It leaves my skin greasy.',{'greasy':'negative'},'negative'),
 ('It is not greasy.',{'greasy':'positive'},'positive'),
 ('It caused redness and a burning sensation.',{'redness':'negative','irritation':'negative'},'negative'),
 ('It does not cause irritation.',{'irritation':'positive'},'positive'),
 ('It absorbs quickly.',{'absorption':'positive'},'positive'),
 ('It does not absorb well.',{'absorption':'negative'},'negative'),
 ('Good packaging.',{'packaging':'positive'},'positive'),
 ('The packaging was damaged.',{'packaging':'negative'},'negative'),
 ('It is hydrating but leaves my skin greasy.',{'hydration':'uncertain','greasy':'negative'},'negative'),
 ('It hydrates my skin well but leaves my skin greasy.',{'hydration':'positive','greasy':'negative'},'mixed'),
 ('It leaves no white cast.',{'whitecast':'positive'},'positive'),
 ('It leaves a white cast.',{'whitecast':'negative'},'negative'),
 ('It did not notice any brightening effect.',{'brightening':'negative','visible':'negative'},'negative'),
 ('Makes my skin visibly plump and hydrated',{'hydration':'positive'},'positive'),
 ('My skin is acne prone.',{},'uncertain'),
]
for text,expected,tone in cases:
 a=annotate(text); actual={x['aspect']:x['sentiment'] for x in a}
 for k,v in expected.items(): assert actual.get(k)==v,(text,expected,actual)
 if not expected:assert not actual,(text,actual)
 assert overall(text,a)==tone,(text,tone,overall(text,a))
 for x in a:
  for e in x['evidence']:assert e['quote'] in text
print('PASS: 16 negation, mixed sentiment, skin-type context, quote provenance cases')
