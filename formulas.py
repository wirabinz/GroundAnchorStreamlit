import numpy as np

def calculate_clay_bond_strength(spt_value):
    SPT_clay = np.array([0.75, 2.25, 5.0, 6.0, 7.5, 10.0, 12.0, 24.0, 36.0])
    bond_strength_clay = np.array([0.008, 0.022, 0.044, 0.05, 0.06, 0.075, 0.087, 0.135, 0.185])
    """
    Calculate bond strength for clay soil.
    Piecewise linear interpolation.
    For SPT <= 0.75: Extrapolate from first segment
    """
    # Handle SPT <= 0.75 (extrapolate from first data point)
    if spt_value <= SPT_clay[0]:
        if spt_value <= 0:
            return 0.0  # SPT cannot be negative or zero
        # Linear extrapolation from (0,0) to first data point
        slope = bond_strength_clay[0] / SPT_clay[0]
        return slope * spt_value
    
    # For SPT between data points up to 12
    if spt_value <= 12:
        for i in range(len(SPT_clay) - 1):
            if SPT_clay[i] <= spt_value <= SPT_clay[i + 1]:
                x1, y1 = SPT_clay[i], bond_strength_clay[i]
                x2, y2 = SPT_clay[i + 1], bond_strength_clay[i + 1]
                return y1 + (spt_value - x1) * (y2 - y1) / (x2 - x1)
        return bond_strength_clay[-1]
    
    # For 12 < SPT <= 36
    elif spt_value <= 36:
        slope = (0.185 - 0.087) / (36 - 12)
        return 0.087 + slope * (spt_value - 12)
    
    # For SPT > 36
    else:
        slope = (0.185 - 0.087) / (36 - 12)
        return 0.185 + slope * (spt_value - 36)

def calculate_sand_bond_strength(spt):
    # Constant linear relationship for Sand from provided notebook
    return 0.005 * spt