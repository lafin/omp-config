"""Grade statistics."""


def letter(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def average(values):
    if len(values) == 0:
        return 0
    total = 0
    count = 0
    for v in values:
        total = total + v
        count = count + 1
    return total / count


def highest(values):
    best = None
    for v in values:
        if best is None:
            best = v
        elif v > best:
            best = v
    return best


def passing(values):
    result = []
    for v in values:
        if v >= 60:
            result.append(v)
    return result


def pass_rate(values):
    if len(values) == 0:
        return 0
    count = 0
    for v in values:
        if v >= 60:
            count = count + 1
    return count / len(values)


def report(values):
    if len(values) == 0:
        return {"average": 0, "highest": None, "pass_rate": 0}
    return {"average": average(values), "highest": highest(values), "pass_rate": pass_rate(values)}


def old_passing_count(values):
    count = 0
    for v in values:
        if v >= 60:
            count = count + 1
    return count
