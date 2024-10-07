from plugin import plugin
import requests

@plugin('exchange_rate')


def exchange_rate(jarvis, s):
    print('Showing exchange rate on global currencies\n\n')

    CURRENCIES = [
        'USD/US Dollar',
        'EUR/Euro',
        'JPY/Japanese yen',
        'GBP/Pound sterling',
        'AUD/ Australian dollar',
        'CAD/Canadian dollar',
        'CHF/Swiss franc',
        'CNH/Chinese renminbi',
        'HKD/Hong Kong dollar'
    ]

    print("Examples")
    for curr in CURRENCIES:
        print(curr)
    
    curr1 = str(input("\nPlease enter your first currency: "))
    curr2 = str(input("Please enter your second currency: "))

    api_url = 'https://api.api-ninjas.com/v1/exchangerate?pair=' + curr1 +'_' + curr2
    response = requests.get(api_url, headers={'X-Api-Key': 'dDcouxccX+Ne1OKZj+rRrw==CW8Mg7Tvlk3u8omW'})
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)