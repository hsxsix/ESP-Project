import requests

icon_70x70_url = "https://ss1.bdstatic.com/5eN1bjq8AAUYm2zgoY3K/r/www/aladdin/img/new_weath/bigicon/{}.png"
icon_50x50_url = "https://ss1.bdstatic.com/5eN1bjq8AAUYm2zgoY3K/r/www/aladdin/img/new_weath/icon/{}.png"
for i in range(1,25):
    icon_url = icon_70x70_url.format(i)
    print(icon_url)
    request = requests.get(icon_url)
    print(request.status_code)
    if "访问的页面不存在" not in request.text:
        with open('{}.png'.format(i), 'wb') as f:
            f.write(request.content)
