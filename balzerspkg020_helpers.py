#!/usr/bin/env python

def interpolate_numpy(value, value_table, exp=True):
    """
    Convert from voltage to pressure using value_table.
    Doing a vectorized conversion if value is an array of values.

    Uses the interpolation function from numpy.
    If exp = True the interpolation will be done on exponentiated
    voltages (slightly more precise and correct).
    """
    import numpy as np
    #return np.interp(value, [row[0] for row in value_table], [row[1] for row in value_table])
    value_table = np.array(value_table)
    xp = value_table[:,0]
    fp = value_table[:,1]
    if exp:
        value = np.exp(value)
        xp    = np.exp(xp)
    return np.interp(value, xp, fp)

def interpolate_naive(value, value_table):
    """
    Interpolate a function using a value_table.

    In between the reference data points,
    a simple linear interpolation is done.
    """

    # don't extrapolate, return edge value if out of lookup range
    if value >= value_table[-1][0]:
        return value_table[-1][1]
    if value <= value_table[0][0]:
        return value_table[0][1]

    # inside range - interpolate
    for voltage, pressure in value_table:
        if value > voltage:
            lower_voltage, lower_pressure = voltage, pressure
            continue
        else:
            dvoltage = voltage - lower_voltage
            dpressure = pressure - lower_pressure
            return lower_pressure + (value - lower_voltage) * dpressure/dvoltage

def interpolate_log_aware(value, value_table):
    """
    Interpolate a value from a logarithmized value
    using a lookup table.
    """
    import math
    # don't extrapolate, return edge value if out of lookup range
    if value >= value_table[-1][0]:
        return value_table[-1][1]
    if value <= value_table[0][0]:
        return value_table[0][1]

    # inside range - interpolate
    for voltage, pressure in value_table:
        if value > voltage:
            lower_voltage, lower_pressure = voltage, pressure
            continue
        else:
            dvoltage = voltage - lower_voltage
            log_pressure2 = math.log(pressure)
            log_pressure1 = math.log(lower_pressure)
            dlogpressure = log_pressure2 - log_pressure1
            interp_log_pressure = log_pressure1 + (value - lower_voltage) * dlogpressure/dvoltage
            return math.exp(interp_log_pressure)

# default interpolate function: The numpy version:
interpolate = interpolate_numpy

def main():
    from balzerspkg020 import tables
    import sys
    while True:
        line = sys.stdin.readline()
        if not line: break
        try:
            num = float(line)
        except:
            sys.stderr.write("Couln't interpret this as a number: " + line)
            continue
        tpr2 = interpolate(num, tables['tpr2'])
        ikr  = interpolate(num, tables['ikr'])
        print("As TPR2 value: %s" % tpr2)
        print("As IKR value: %s"  % ikr)

if __name__ == "__main__": main()
