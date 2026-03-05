import sympy as sp
import random
from functools import reduce
from Consts import *
from egcd import egcd


def div_mod(num, den, fieldsize):
    """
    Finds the modular inverse of den mod fieldsize and multiplies it by num, all mod fieldsize.
    
    :param num: The numerator
    :param den: The denominator
    :param fieldsize: The modulus for the finite field

    """
    d, x, _ = egcd(den, fieldsize)
    if d != 1:
        raise ValueError("Denominator must be coprime to fieldsize")
    return (num * x) % fieldsize


def gen_shares(secret: int, n: int, t: int, fieldsize: int) -> Shares:
    """ 
    :param secret: The secret to share
    :param n: The number of shares to create
    :param t: The threshold number of shares needed to reconstruct the secret
    :param fieldsize: The modulus for the finite field
    :return: A list of n shares, where each share is a tuple (x, y)
    """

    if fieldsize <= 0:
        raise ValueError("fieldsize must be a positive integer")

    if t <= 0:
        raise ValueError("threshold t must be a positive integer")

    if n < t:
        raise ValueError("number of shares n must be larger than threshold t")

    x_values = list(range(t))
    random_coeffs = [random.SystemRandom().randint(0, fieldsize - 1) for _ in range(t - 1)]
    coeffs = [secret % fieldsize] + random_coeffs
    polynomial = list(zip(x_values, coeffs))

    points_for_shares = range(1, n + 1)
    return [(p, lagrange_interpolate(p, polynomial, fieldsize)) for p in points_for_shares]


def lagrange_interpolate(x, datapoints, fieldsize) -> int:
    """       
    :param x: The x value to evaluate the polynomial at
    :param datapoints: A list of tuples (x_i, y_i) representing the data points
    :param fieldsize: The modulus for the finite field
    :return: The value of the interpolated polynomial at x, computed modulo fieldsize
    """
    x_points, y_points = zip(*datapoints)
    numOfPoints = len(x_points)

    # Calculate the product of a list of numbers
    product = lambda vals: reduce(lambda acc, v: acc * v, vals, 1)
    
    denominators = []
    numerators = []
    for i in range(numOfPoints):
        restOfList = list(x_points)
        working_x = restOfList.pop(i)
        numsList = (x - o for o in restOfList)
        densList = (working_x - o for o in restOfList)
        numerators.append(product(numsList))
        denominators.append(product(densList))
    denominator = product(denominators)
    numerator = 0
    for i in range(numOfPoints):
        top = y_points[i] * (numerators[i] * denominator) % fieldsize
        numerator += div_mod(top , denominators[i], fieldsize)

    resultAtX = (div_mod(numerator, denominator, fieldsize) + fieldsize) % fieldsize
    return resultAtX

"""  
Reconstructs multiple secrets given m data points where:
    secret1 is at x = -numOfSecrets+1
    secret2 is at x = -numOfSecrets+2, 
    .
    .
    .
    secretN is at x = 0
"""
def reconstruct_secret(shares, fieldsize):
    return lagrange_interpolate(0, shares, fieldsize)


def lagrange_basis_at_zero(xPoints, index, threshold, fieldsize) -> int:
    """
    Computes the value of the Lagrange basis polynomial at x=0 for a given index.

    :param xPoints: A list of x-coordinates of the data points
    :param index: The index of the basis polynomial to compute
    :param threshold: The total number of data points (threshold)
    :param fieldsize: The modulus for the finite field
    :return: The value of the Lagrange basis polynomial at x=0 for the given index, computed modulo fieldsize
    """
    result = 1
    for i in range(threshold):
        if i == index:
            continue
        temp = div_mod(xPoints[i], xPoints[i] - xPoints[index], fieldsize)
        result = (result * temp) % fieldsize
    return result