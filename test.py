import json
with open('scheme.json') as f:
    data = json.load(f)
    for d in data['classes']:
        if d['name'] == '1st':
            data = d
            break
development_page_count=0
for development_page in range(0,3):
    access_accounts=[dic['username'] for dic in data['development_page_access'][development_page_count]['Auth_teachers_access']]
    print(access_accounts)