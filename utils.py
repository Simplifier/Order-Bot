def format_price(price):
    price = '{0:.2f}'.format(price)
    ar = price.split('.')
    if ar[1] == '00':
        return ar[0]
    else:
        return price
