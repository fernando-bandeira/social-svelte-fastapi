import requests

with open('./backend/names.txt', encoding='utf-8') as arq:
    names = arq.readlines()

# for name in names:
#     payload = {
#         "name": name.replace('\n', '').replace(' ', '_').lower(),
#         "email": name.replace('\n', '').replace(' ', '_').lower() + "@email.com",
#         "password": "svelte",
#         "public": True
#     }
#     print(payload)
#     requests.post('http://localhost:8000/register/', json=payload)

for i in range(30, 35):
    requests.post(f'http://localhost:8000/follows/1/{i}/')
