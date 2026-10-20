"""Shipping cost calculator."""


def zone_rate(zone):
    if zone == "local":
        return 5
    elif zone == "national":
        return 10
    elif zone == "international":
        return 25
    else:
        raise ValueError("unknown zone")


def weight_surcharge(weight):
    if weight <= 0:
        raise ValueError("weight must be positive")
    if weight <= 1:
        surcharge = 0
    elif weight <= 5:
        surcharge = 3
    elif weight <= 20:
        surcharge = 8
    else:
        surcharge = 20
    return surcharge


def express_fee(express, base):
    if express == True:
        fee = base * 0.5
        return fee
    else:
        fee = 0
        return fee


def shipping_cost(zone, weight, express=False):
    base = zone_rate(zone)
    surcharge = weight_surcharge(weight)
    total = base + surcharge
    fee = express_fee(express, total)
    total = total + fee
    return total


def legacy_cost(zone, weight):
    if zone == "local":
        base = 5
    elif zone == "national":
        base = 10
    elif zone == "international":
        base = 25
    else:
        raise ValueError("unknown zone")
    if weight <= 0:
        raise ValueError("weight must be positive")
    if weight <= 1:
        extra = 0
    elif weight <= 5:
        extra = 3
    elif weight <= 20:
        extra = 8
    else:
        extra = 20
    return base + extra
